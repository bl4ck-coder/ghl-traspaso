"""Prueba aspecto del iframe de suscripción sin enviar el formulario."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse
p=argparse.ArgumentParser();p.add_argument('--css',type=Path);a=p.parse_args()
URL='https://apisystem.tech/widget/form/FORM_ID'
JS='''() => { const i=document.querySelector('input[type=email]'),b=document.querySelector('button.button-element');const g=n=>{const r=n.getBoundingClientRect(),c=getComputedStyle(n);return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height),c.borderTopLeftRadius,c.fontFamily]};return {input:g(i),button:g(b),scroll:document.documentElement.scrollWidth,mark:[...document.querySelectorAll('style')].some(n=>n.textContent.includes('ADICIO FORM IFRAME 1'))} }'''
with sync_playwright() as w:
 b=w.chromium.launch(channel='msedge');fails=[]
 for width in (514,634,289):
  q=b.new_page(viewport={'width':width,'height':300});q.goto(URL,wait_until='domcontentloaded');q.locator('input[type=email]').wait_for(timeout=12000)
  if a.css:q.add_style_tag(content=a.css.read_text(encoding='utf8'))
  q.evaluate('document.fonts.ready');q.wait_for_function("()=>getComputedStyle(document.querySelector('input[type=email]')).borderTopLeftRadius==='999px'",timeout=4000)
  m=q.evaluate(JS);print(width,m)
  i,h=m['input'],m['button']; checks=[m['mark'],m['scroll']<=width,i[3]>=56,h[3]>=56,i[4]=='999px',h[4]=='999px']
  checks += [abs(i[1]-h[1])<=2, h[0]>=i[0]+i[2]] if width>435 else [h[1]>=i[1]+i[3],abs(i[2]-h[2])<=3]
  if not all(checks):fails.append((width,checks))
  q.close()
 assert not fails,fails
