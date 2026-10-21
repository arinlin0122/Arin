"""Public RSS metadata only; no API key, generated summaries, or article verification."""
import concurrent.futures
import datetime as dt
import email.utils
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / 'data/musk-news.json'
TOPICS = ('Elon Musk', 'xAI', 'Tesla', 'SpaceX', 'Neuralink')

def feed_url(topic):
    return 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': '"'+topic+'" when:7d', 'hl':'en-US', 'gl':'US', 'ceid':'US:en'})

def parse_feed(raw, topic, now):
    root = ET.fromstring(raw)
    if root.tag != 'rss' or root.find('channel') is None:
        raise ValueError('Invalid RSS document')
    items = []
    for item in root.findall('./channel/item'):
        title, url = item.findtext('title', '').strip(), item.findtext('link', '').strip()
        source = item.find('source')
        try:
            published = email.utils.parsedate_to_datetime(item.findtext('pubDate', '')).astimezone(dt.timezone.utc)
        except (ValueError, TypeError, AttributeError):
            continue
        if not re.search(r'\b'+re.escape(topic)+r'\b', title, re.I):
            continue
        if topic == 'xAI' and re.search(r'floating rate|income trust|tender offer', title, re.I):
            continue
        parsed = urllib.parse.urlparse(url)
        if not title or source is None or not source.text or parsed.scheme != 'https' or parsed.hostname != 'news.google.com':
            continue
        if published > now + dt.timedelta(minutes=10) or published < now - dt.timedelta(days=8):
            continue
        items.append({'title':title[:500], 'url':url, 'source':source.text[:200], 'topic':topic, 'published_at':published.isoformat()})
    if not items:
        raise ValueError('No valid recent items')
    return items[:15]

def fetch_topic(topic, now):
    for attempt in range(3):
        try:
            req = urllib.request.Request(feed_url(topic), headers={'User-Agent':'AI-Mastery-Hub/1.0 RSS reader'})
            with urllib.request.urlopen(req, timeout=20) as response:
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError('Feed too large')
            return parse_feed(raw, topic, now)
        except Exception:
            if attempt == 2:
                raise RuntimeError('RSS unavailable or invalid after 3 attempts') from None
            time.sleep(attempt + 1)

def update(previous, fetcher=fetch_topic, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    stamp = now.isoformat()
    items, sources = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = {topic:pool.submit(fetcher, topic, now) for topic in TOPICS}
        for topic, future in futures.items():
            try:
                batch = future.result()
                items.extend(batch)
                sources.append({'topic':topic, 'url':feed_url(topic), 'status':'ok', 'last_success_at':stamp})
            except Exception:
                old = next((s for s in previous.get('sources', []) if s['topic']==topic), {})
                items.extend(i for i in previous.get('items', []) if i['topic']==topic)
                sources.append({'topic':topic, 'url':feed_url(topic), 'status':'failed', 'last_success_at':old.get('last_success_at'), 'error':'RSS 获取失败；保留该主题上次数据'})
    unique = {}
    for item in sorted(items, key=lambda i:i['published_at'], reverse=True):
        key = re.sub(r'\W+', '', item['title'].lower())
        unique.setdefault(key, item)
    ok = sum(s['status']=='ok' for s in sources)
    return {'schema_version':1, 'attempted_at':stamp, 'last_success_at':stamp if ok else previous.get('last_success_at'), 'status':'ok' if ok==len(TOPICS) else 'partial' if ok else 'failed', 'sources':sources, 'items':list(unique.values())[:60]}

def main():
    previous = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    result = update(previous)
    OUTPUT.parent.mkdir(exist_ok=True)
    temp = OUTPUT.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    temp.replace(OUTPUT)
    print(f"RSS status: {result['status']}; {len(result['items'])} headlines")
    return 0 if result['status']=='ok' else 1

if __name__ == '__main__':
    raise SystemExit(main())
