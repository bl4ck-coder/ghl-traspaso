"""Compara fuentes efectivamente pintadas y recorrido de Servicios en el borrador, sin escribir en GHL."""
import argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser(); ap.add_argument('out',type=Path); ap.add_argument('--css',type=Path); ap.add_argument('--solo-fuentes',action='store_true'); a=ap.parse_args()
a.out.mkdir(parents=True,exist_ok=True)
u={'original':'http://127.0.0.1:8831/','ghl':'https://sites.leadconnectorhq.com/preview/PAGE_ID'}
font_targets=['.col-intro-texto .bajada p,.col-intro-texto p.bajada','.servicio-texto .numero p,.servicio-texto p.numero','.servicio-texto h3','.servicio-texto p:not(.numero):not(.numero p)','.s-pie .pie-lema p,.s-pie p.pie-lema']
all_results={}; failures=[]
def check(ok,msg):
 if not ok: failures.append(msg)

with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge')
 for width,height,reduce in ([(1920,950,True),(412,915,True)] if a.solo_fuentes else [(1920,950,False),(412,915,False),(1920,950,True)]):
  key=f'{width}-{reduce}'; pair={}
  for label,url in u.items():
   p=b.new_page(viewport={'width':width,'height':height},reduced_motion='reduce' if reduce else 'no-preference',has_touch=width<500,is_mobile=width<500); errs=[]
   p.on('pageerror',lambda ex:errs.append(str(ex)))
   response=p.goto(url,wait_until='domcontentloaded',timeout=25000); assert response and response.ok
   if label=='ghl' and a.css:p.add_style_tag(path=str(a.css))
   p.wait_for_function("window.__adicioCapa?.estado==="+json.dumps('quieta' if reduce else 'activa'),timeout=18000)
   p.evaluate('document.fonts.ready.then(()=>null)')
   c=p.context.new_cdp_session(p); c.send('DOM.enable'); c.send('CSS.enable'); root=c.send('DOM.getDocument')['root']['nodeId']
   fs=[]
   for sel in font_targets:
    n=c.send('DOM.querySelector',{'nodeId':root,'selector':sel})['nodeId']; assert n,sel
    out=c.send('CSS.getPlatformFontsForNode',{'nodeId':n})['fonts']; fs.append([x['familyName'] for x in out if x['glyphCount']])
   data={'fuentes':fs,'errores':errs}; pair[label]=data
   if not a.solo_fuentes:
    cards=p.locator('.servicios .anim-apilar'); assert cards.count()==4
    # Positions are taken from the static order, then sampled during scroll. Use instant steps so CSS smooth-scroll does not change the test.
    points=p.evaluate('''()=>{const box=document.querySelector('.servicios'),y=box.getBoundingClientRect().top+scrollY;const cs=[...box.querySelectorAll('.anim-apilar')];return cs.map((c,i)=>Math.round(c.getBoundingClientRect().top+scrollY-(innerWidth>980?215:300))).concat(Math.round(y+box.offsetHeight-100))}''')
    traces=[]
    for j,y in enumerate(points):
     p.evaluate('(y)=>window.scrollTo({top:y,behavior:"instant"})',y)
     if width<=980 and not reduce and j<4: p.wait_for_function('(i)=>Number(getComputedStyle(document.querySelectorAll(".servicios .anim-apilar")[i]).opacity)>.95',arg=j,timeout=5000)
     else: p.wait_for_timeout(280)
     p.evaluate('''()=>Promise.race([Promise.all([...document.querySelectorAll('.servicio-foto img')].filter(n=>n.getBoundingClientRect().top<innerHeight&&n.getBoundingClientRect().bottom>0).map(n=>n.decode().catch(()=>{}))),new Promise(r=>setTimeout(r,1700))])''')
     tr=p.evaluate('''()=>({cards:[...document.querySelectorAll('.servicios .anim-apilar')].map(n=>{const r=n.getBoundingClientRect(),s=getComputedStyle(n),i=n.querySelector('.servicio-foto img');return [Math.round(r.top),Math.round(r.bottom),s.position,Number(s.opacity).toFixed(2),i.naturalWidth]}),overflow:document.documentElement.scrollWidth-innerWidth})''');traces.append(tr)
     p.screenshot(path=a.out/f'{key}-{label}-{j}.jpg',quality=80)
    data['recorrido']=traces
    if width>980 and not reduce:check(all(t[2]=='sticky' for t in traces[0]['cards']),f'{key} {label}: las cuatro fichas usan sticky');check(any(abs(t['cards'][0][0]-118)<=2 and t['cards'][1][0]<t['cards'][0][1] for t in traces[:-1]),f'{key} {label}: fichas superpuestas durante scroll')
    else:check(all(t[2]!='sticky' for t in traces[0]['cards']),f'{key} {label}: scroll sin fijación')
    check(all(t['overflow']==0 for t in traces),f'{key} {label}: sin desborde')
    check(all(any(t['cards'][i][4]>0 for t in traces) for i in range(4)),f'{key} {label}: las cuatro fotos cargaron durante el recorrido')
   check(not errs,f'{key} {label}: sin errores JS'); p.close()
  all_results[key]=pair
  for i,(x,y) in enumerate(zip(pair['original']['fuentes'],pair['ghl']['fuentes'])):
   check(x and y and x==y,f'{key} fuente {i}: {x} != {y}')
  print(key,{l:v['fuentes'] for l,v in pair.items()},flush=True)
(a.out/'prueba.json').write_text(json.dumps({'resultados':all_results,'fallas':failures},ensure_ascii=False,indent=2),encoding='utf8')
print('Fallas:',failures)
raise SystemExit(bool(failures))
