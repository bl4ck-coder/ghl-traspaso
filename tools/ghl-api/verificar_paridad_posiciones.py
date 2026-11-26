"""Mide pares por sección contra el original, sin comparar coordenadas globales."""
from pathlib import Path
import argparse
from playwright.sync_api import sync_playwright
pa=argparse.ArgumentParser();pa.add_argument('--css',type=Path);pa.add_argument('--informar',action='store_true');args=pa.parse_args()
U={'o':'http://127.0.0.1:8831/','g':'https://sites.leadconnectorhq.com/preview/PAGE_ID'}
S={'faq':['.s-faq .col-faq-intro p','.s-faq .boton','.s-faq :is(details,.hl-faq-child)'],'como':['.s-como .sello','.s-como .col-pasos','.s-como .anim-paso'],'novedades':['.s-novedades input[type=email]','.s-novedades .col-novedades']}
J='''([k,sels])=>{const sec=document.querySelector('.s-'+k).getBoundingClientRect();return [Math.round(sec.height),...sels.map(s=>[...document.querySelectorAll(s)].map(n=>Math.round(n.getBoundingClientRect().top-sec.top)))]}'''
with sync_playwright() as w:
 b=w.chromium.launch(channel='msedge'); fail=[]
 for width in (1920,900,412,360):
  m={}
  for key,u in U.items():
   p=b.new_page(viewport={'width':width,'height':915},reduced_motion='reduce');p.goto(u,wait_until='networkidle')
   if key=='g' and args.css:p.add_style_tag(content=args.css.read_text(encoding='utf8'))
   p.evaluate('document.fonts.ready.then(()=>null)');p.locator(S['novedades'][0]).wait_for();m[key]={k:p.evaluate(J,[k,v]) for k,v in S.items()}
   assert p.evaluate('document.documentElement.scrollWidth-innerWidth')==0
   p.close()
  for k in S:assert [len(row) for row in m['g'][k][1:]]==[len(row) for row in m['o'][k][1:]] and all(m['g'][k][1:]),(width,k,m)
  diff={k:[m['g'][k][0]-m['o'][k][0],*[[a-b for a,b in zip(gs,os)] for gs,os in zip(m['g'][k][1:],m['o'][k][1:])]] for k in S};print(width,diff,flush=True)
  for k,v in diff.items():
   y=max(abs(n) for n in [v[0],*(i for group in v[1:] for i in group)])
   maxy={'faq':1,'como':2,'novedades':8}[k]
   if y>maxy:fail.append((width,k,y,maxy))
 if not args.informar:assert not fail,fail
