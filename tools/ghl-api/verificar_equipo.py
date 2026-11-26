"""Compara cita, retrato y cifras con el original; no escribe en GHL."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--css',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
JS='''()=>{const s=document.querySelector('.s-equipo'),r=s.getBoundingClientRect();return Object.fromEntries(['.equipo-foto','.cita','.cifra','.cifra-numero p,.cifra-numero:is(p)'].map(k=>[k,[...s.querySelectorAll(k)].map(x=>{const b=x.getBoundingClientRect(),c=getComputedStyle(x);return [Math.round(b.x-r.x),Math.round(b.y-r.y),Math.round(b.width),Math.round(b.height),c.padding,c.fontSize]})]))}'''
with sync_playwright() as w:
 b=w.chromium.launch(channel='msedge');out={}
 for width in (1920,900,412,360):
  for k,u in [('o','http://127.0.0.1:8831/'),('g','https://sites.leadconnectorhq.com/preview/PAGE_ID')]:
   q=b.new_page(viewport={'width':width,'height':950},reduced_motion='reduce');q.goto(u,wait_until='domcontentloaded');q.locator('.s-equipo .cita').wait_for();q.evaluate('document.fonts.ready.then(()=>null)')
   if k=='g' and a.css:q.add_style_tag(content=a.css.read_text(encoding='utf8'))
   if a.out and width in (1920,360):
    a.out.mkdir(parents=True,exist_ok=True)
    for sel,nombre in [('.s-equipo .cita','cita'),('.s-equipo .cifra','cifras')]:
     el=q.locator(sel).first;el.evaluate('x=>x.scrollIntoView({block:"center",behavior:"instant"})')
     q.wait_for_function('s=>{const r=document.querySelector(s).getBoundingClientRect();return r.bottom>0&&r.top<innerHeight}',arg=sel)
     if nombre=='cita':
      foto=q.locator('.s-equipo .equipo-foto').first
      foto.evaluate('async img=>{await img.decode();if(!img.naturalWidth) throw Error("Retrato sin imagen")}')
     q.screenshot(path=a.out/f'{width}-{k}-{nombre}.png')
   out[k]=q.evaluate(JS);q.close()
  print(width,json.dumps(out,ensure_ascii=False),flush=True)
