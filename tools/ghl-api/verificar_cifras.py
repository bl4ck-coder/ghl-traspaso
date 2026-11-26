"""Prueba el signo luego de recorrer el borrador, al bajar y volver, con y sin movimiento."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--js',type=Path);a=p.parse_args()
url='https://sites.leadconnectorhq.com/preview/PAGE_ID'
with sync_playwright() as w:
 b=w.chromium.launch(channel='msedge')
 for width in (360,1920):
  for motion in ('reduce','no-preference'):
   q=b.new_page(viewport={'width':width,'height':950},reduced_motion=motion); errs=[];q.on('pageerror',lambda e:errs.append(str(e)))
   assert q.goto(url,wait_until='domcontentloaded').ok
   if a.js:q.add_script_tag(content=a.js.read_text(encoding='utf8'))
   for s in ('.s-servicios','.s-equipo .cifra','.s-pie','.s-equipo .cifra:last-child'):
    q.locator(s).first.evaluate('x=>x.scrollIntoView({behavior:"instant",block:"center"})');q.wait_for_timeout(500)
   q.wait_for_function("()=>!document.querySelector('.s-equipo .capa-odo') && document.querySelectorAll('.s-equipo .cifra-numero p > .cifra-signo').length===4",timeout=9000)
   r=q.locator('.s-equipo .cifra-numero p').evaluate_all('ns=>ns.map(n=>{const s=n.querySelector(".cifra-signo"),c=getComputedStyle(s);return [n.textContent,c.color,parseFloat(c.fontSize)/parseFloat(getComputedStyle(n).fontSize)]})')
   assert [x[0] for x in r]==['20+','500+','50+','98%'] and all(x[1]=='rgb(0, 196, 154)' and .49<=x[2]<=.51 for x in r),r
   assert not errs,errs
   print(width,motion,r,flush=True);q.close()
