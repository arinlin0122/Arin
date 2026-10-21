import datetime as dt
import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('news',Path(__file__).resolve().parents[1]/'scripts/update_musk_news.py')
n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
NOW=dt.datetime(2026,10,21,tzinfo=dt.timezone.utc)
class NewsTests(unittest.TestCase):
    def item(self, topic):
        return {'title':topic+' headline','topic':topic,'published_at':NOW.isoformat(),'url':'https://news.google.com/rss/articles/a','source':'Publisher'}
    def test_failure_keeps_old_timestamp_and_items(self):
        old={'last_success_at':'2026-10-19T00:00:00+00:00','items':[self.item('Tesla')], 'sources':[]}
        def fail(*args): raise RuntimeError()
        result=n.update(old,fail,NOW)
        self.assertEqual(result['status'],'failed');self.assertEqual(result['items'],old['items']);self.assertEqual(result['last_success_at'],old['last_success_at'])
    def test_partial_preserves_failed_topic(self):
        def fetch(topic,now):
            if topic=='Tesla': raise RuntimeError()
            return [self.item(topic)]
        result=n.update({'items':[self.item('Tesla')]},fetch,NOW)
        self.assertEqual(result['status'],'partial');self.assertEqual(len(result['items']),5)
    def test_success_deduplicates(self):
        result=n.update({},lambda topic,now:[self.item('Tesla')],NOW)
        self.assertEqual(result['status'],'ok');self.assertEqual(len(result['items']),1)
    def test_parse_rejects_unsafe_future_and_old(self):
        template='<rss><channel><item><title>Tesla test</title><link>{}</link><pubDate>{}</pubDate><source>P</source></item></channel></rss>'
        for link,date in [('javascript:alert(1)','Wed, 21 Oct 2026 00:00:00 GMT'),('https://news.google.com/a','Wed, 21 Oct 2030 00:00:00 GMT'),('https://news.google.com/a','Wed, 01 Oct 2026 00:00:00 GMT')]:
            with self.assertRaises(ValueError): n.parse_feed(template.format(link,date),'Tesla',NOW)
        self.assertEqual(len(n.parse_feed(template.format('https://news.google.com/a','Wed, 21 Oct 2026 00:00:00 GMT'),'Tesla',NOW)),1)
if __name__=='__main__': unittest.main()
