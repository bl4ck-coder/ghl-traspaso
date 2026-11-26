"""Audita original y vista previa real. No guarda ni envía formularios."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
urls={'origen':'http://127.0.0.1:8831/','ghl':'https://sites.leadconnectorhq.com/preview/PAGE_ID'}
keys=['.s-nav','.s-hero','.s-servicios','.s-equipo','.s-como','.s-novedades','.s-contacto','.s-faq','.s-blog','.s-pie']
styles='''(keys)=>({head:{title:document.title,lang:document.documentElement.lang,description:document.querySelector('meta[name="description"]')?.content,robots:document.querySelector('meta[name="robots"]')?.content,schema:[...document.querySelectorAll('script[type="application/ld+json"]')].map(x=>{try{return JSON.parse(x.textContent)}catch{return 'inválido'}})},h:[...document.querySelectorAll('#preview-container h1,#preview-container h2,#preview-container h3,body > header h1,main :is(h1,h2,h3)')].map(x=>[x.tagName,x.textContent.replace(/\\s+/g,' ').trim()]),sections:Object.fromEntries(keys.map(k=>{let e=document.querySelector(k);if(!e)return[k,null];let r=e.getBoundingClientRect();return[k,{height:Math.round(r.height),scrollWidth:e.scrollWidth,width:e.clientWidth,images:[...e.querySelectorAll('img')].filter(x=>!x.naturalWidth).map(x=>x.getAttribute('src')),headings:[...e.querySelectorAll('h1,h2,h3')].map(x=>[x.tagName,x.textContent.replace(/\\s+/g,' ').trim()]),links:[...e.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href')).filter(h=>h.length>1&&!document.getElementById(h.slice(1)))}]})),overflow:document.documentElement.scrollWidth-innerWidth,forms:[...document.querySelectorAll('.s-novedades input,.s-novedades iframe,.s-novedades form,.s-novedades .c-form')].map(x=>[x.tagName,x.getAttribute('type'),x.getAttribute('placeholder'),x.getAttribute('action'),x.getAttribute('src')])})'''
result={}
with sync_playwright() as sp:
 b=sp.chromium.launch(channel='msedge')
 for width,height in [(1920,950),(900,900),(412,915),(360,800)]:
  for key,url in urls.items():
   p=b.new_page(viewport={'width':width,'height':height},reduced_motion='reduce',has_touch=width<500,is_mobile=width<500);errors=[];http=[]
   p.on('pageerror',lambda e:errors.append(str(e)));p.on('response',lambda r:http.append([r.status,r.url]) if r.status>=400 else None)
   response=p.goto(url,wait_until='domcontentloaded',timeout=30000);assert response.ok,(response.status,url)
   p.locator('.s-pie').wait_for(timeout=10000)
   p.evaluate('document.fonts.ready.then(()=>null)')
   for sel in keys[2:]:
    loc=p.locator(sel).first;loc.evaluate('e=>e.scrollIntoView()');k=p.evaluate('''s=>Promise.race([Promise.all([...document.querySelectorAll(s+' img')].map(i=>i.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,1100))])''',sel)
    if width in (1920,412):loc.screenshot(path=out/f'{width}-{key}-{sel[3:]}.jpg',quality=85)
   data=p.evaluate(styles,keys);data['errors']=errors;data['http']=http
   result[f'{width}-{key}']=data
   print(width,key,[(s,v['height'],len(v['images'])) for s,v in data['sections'].items() if v], 'overflow',data['overflow'],'errors',errors,flush=True)
   p.close()
   (out/'auditoria.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
 b.close()
