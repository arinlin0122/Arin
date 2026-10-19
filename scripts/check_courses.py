import json,urllib.request,urllib.error,datetime,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
urls=['https://www.deeplearning.ai/courses/ai-for-everyone/','https://huggingface.co/learn/agents-course/unit0/introduction','https://www.deeplearning.ai/the-batch/','https://aiindex.stanford.edu/report/','https://academy.openai.com/','https://learn.microsoft.com/en-us/training/']
results=[]
for url in urls:
 try:
  req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=12) as r:code=r.status
 except urllib.error.HTTPError as e:code=e.code
 except Exception:code=0
 status='broken' if code in (404,410) else ('needs_review' if code==0 or code>=400 else 'ok')
 results.append({'url':url,'status':status,'http_status':code})
(root/'data/course-status.json').write_text(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results},ensure_ascii=False,indent=2)+'\n')
print('Checked',len(results),'links')
