'use strict';
const $ = id => document.getElementById(id);
let data;
const format = value => value && Number.isFinite(Date.parse(value)) ? new Date(value).toLocaleString('zh-CN', {timeZone:'Asia/Shanghai',hour12:false})+'（北京时间）' : '暂无成功记录';
function render() {
  if (!data) return;
  const stale = !data.last_success_at || Date.now()-Date.parse(data.last_success_at)>12*3600000;
  const state = data.status==='failed'?'抓取失败，显示保留数据':data.status==='partial'?'部分来源失败，部分主题保留旧数据':data.status==='ok'?'上次抓取成功':'尚未完成首次抓取';
  $('newsStatus').classList.toggle('warning',stale||data.status!=='ok');
  $('newsStatus').textContent=state+(stale?' · 数据已过时（超过 12 小时或尚无成功记录）':'')+'\n最近尝试：'+format(data.attempted_at)+'\n最近至少一个来源成功：'+format(data.last_success_at)+'\n以下每条另列文章发布时间；重新读取不会触发服务器抓取。';
  $('sourceStatus').textContent=(data.sources||[]).map(s=>s.topic+'：'+(s.status==='ok'?'成功':'失败，可能显示旧数据')+' · 上次成功 '+format(s.last_success_at)).join('\n');
  const list=$('newsList');list.replaceChildren();
  const items=(data.items||[]).filter(i=>$('topic').value==='all'||i.topic===$('topic').value);
  if(!items.length){list.textContent='暂无可显示的新闻；请检查抓取状态或稍后重试。';return;}
  for(const item of items){
    let url;try{url=new URL(item.url)}catch{continue;}
    if(url.protocol!=='https:'||url.hostname!=='news.google.com')continue;
    const row=document.createElement('div');row.className='newsitem';
    const meta=document.createElement('div');meta.className='newsmeta';meta.textContent=item.topic+' · '+item.source+' · 发布于 '+format(item.published_at);
    const link=document.createElement('a');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';link.textContent=item.title+' ↗';
    row.append(meta,link);list.append(row);
  }
}
async function load(){
  $('reload').disabled=true;const ctrl=new AbortController();const timer=setTimeout(()=>ctrl.abort(),15000);
  try{const response=await fetch('data/musk-news.json',{cache:'no-store',signal:ctrl.signal});if(!response.ok)throw Error();const next=await response.json();if(next.schema_version!==1||!Array.isArray(next.items)||!Array.isArray(next.sources))throw Error();data=next;render();}
  catch{if(data)render();$('newsStatus').classList.add('warning');$('newsStatus').textContent='读取已发布数据失败。'+(data?'保留本次页面之前读取的数据。\n'+$('newsStatus').textContent:'无法确认新闻更新时间；请稍后重试。');}
  finally{clearTimeout(timer);$('reload').disabled=false;}
}
$('topic').onchange=render;$('reload').onclick=load;load();setInterval(load,300000);setInterval(render,60000);
const key='ai_mastery_musk_notes_v1';
try{$('note').value=localStorage.getItem(key)||'';}catch{$('noteStatus').textContent='浏览器存储不可用，请导出笔记。';}
$('saveNote').onclick=()=>{try{localStorage.setItem(key,$('note').value);$('noteStatus').textContent='已保存 · '+format(new Date().toISOString());}catch{$('noteStatus').textContent='保存失败，请导出笔记。';}};
$('exportNote').onclick=()=>{const url=URL.createObjectURL(new Blob([$('note').value],{type:'text/plain;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='musk-learning-notes.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
