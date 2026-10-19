import os,json,urllib.request,urllib.parse,datetime,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
now=datetime.datetime.now(datetime.timezone.utc)
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'AI-Mastery-Hub/1.0'})
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)
since=int(now.timestamp())-3*86400
params=urllib.parse.urlencode({'query':'AI','tags':'story','hitsPerPage':80,'numericFilters':f'created_at_i>{since}'})
hits=get('https://hn.algolia.com/api/v1/search_by_date?'+params).get('hits',[])
items=[];seen=set()
for h in hits:
 u=h.get('url') or '';t=h.get('title') or '';domain=urllib.parse.urlparse(u).netloc.lower()
 if not u.startswith('https://') or not t or domain in seen or not domain:continue
 seen.add(domain);items.append({'title':t[:240],'url':u,'source':domain,'date':(h.get('created_at') or '')[:10]})
 if len(items)>=12:break
if len(items)<3:raise RuntimeError('Insufficient news; previous briefing remains')
stories=[];method='headline-only, not independently verified'
key=os.getenv('OPENAI_API_KEY')
if key:
 prompt='从以下新闻标题和元数据选择 5-7 条最重要且不同主题的 AI 新闻。用中文分别生成 type,title,summary,why,action，并原样保留 date,source,url。仅有标题，严禁编造正文、数字、引述或确认未验证的事实。用谨慎措辞。只返回 JSON 对象 {"stories":[...]}.\n'+json.dumps(items,ensure_ascii=False)
 body=json.dumps({'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'input':prompt,'text':{'format':{'type':'json_object'}},'max_output_tokens':2300}).encode()
 req=urllib.request.Request('https://api.openai.com/v1/responses',data=body,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(req,timeout=75) as r:resp=json.load(r)
  parsed=json.loads(''.join(c.get('text','') for o in resp.get('output',[]) for c in o.get('content',[]) if c.get('type')=='output_text'))
  by_url={x['url']:x for x in items}
  for s in parsed.get('stories',[]):
   if s.get('url') not in by_url:continue
   base=by_url[s['url']]
   stories.append({k:str(s.get(k,''))[:900] for k in ('type','title','summary','why','action')}|base)
   if len(stories)==7:break
  method='AI-assisted digest of headlines, not full articles'
 except Exception as e:print('AI step failed, using headline-only:',str(e)[:160])
if not stories:
 stories=[{'type':'待核实线索','title':x['title'],'summary':'根据新闻标题发现的最新线索，尚未阅读全文。','why':'需要阅读原文核实具体事实和影响。','action':'打开原文并记录三个关键事实。',**x} for x in items[:6]]
now_shanghai=now+datetime.timedelta(hours=8)
result={'date':now_shanghai.date().isoformat(),'generated_at':now.isoformat(),'method':method,'stories':stories,'candidate_count':len(items)}
(root/'data/latest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Generated',len(stories),'stories')
