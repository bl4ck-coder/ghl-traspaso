"""Prueba de edición reversible del H2 nativo del Blog en el borrador ADICIO 2."""
import json,time,sys
from playwright.sync_api import sync_playwright, TimeoutError
from editor9333 import Editor
from cdp9333 import Pestana
PAGE='PAGE_ID'; LOC='LOCATION_ID'
BASE='https://sites.leadconnectorhq.com/preview/'+PAGE
ORIGINAL='Compartir lo que sabemos también es una forma de cuidar'; TEMP=ORIGINAL+' · prueba temporal'
root=None; e=None

def start():
 global e
 for _ in range(20):
  try:
   e=Editor()
   if e.js(f"location.pathname==='/location/{LOC}/page-builder/{PAGE}'&&document.body.innerText.includes('ADICIO 2')&&!!document.querySelector('.s-blog .tiptap h2')"):return
  except Exception:pass
  time.sleep(.7)
 raise RuntimeError('Editor de borrador no disponible')

def j(s):
 return e.js('(()=>{if(!location.pathname.endsWith("/'+PAGE+'")||!document.body.innerText.includes("ADICIO 2"))throw Error("Destino inesperado");const h=document.querySelector(".s-blog .tiptap h2");if(!h)throw Error("No se encuentra el H2");'+s+'})()')

def write(expect,text):
 assert j('return h.textContent')==expect
 xy=j('h.scrollIntoView({block:"center",behavior:"instant"});const r=h.getBoundingClientRect();return [r.left+Math.min(120,r.width/2),r.top+Math.min(24,r.height/2)]')
 for k in ('mousePressed','mouseReleased'):
  e.cmd('Input.dispatchMouseEvent',type=k,x=xy[0],y=xy[1],button='left',clickCount=1)
 assert j('const p=h.closest(".tiptap");if(!p.isContentEditable)return false;p.focus();const r=document.createRange();r.selectNodeContents(h);const s=getSelection();s.removeAllRanges();s.addRange(r);return s.toString()===h.textContent;'), 'No se pudo activar la edición del H2'
 e.cmd('Input.insertText',text=text)
 assert j('return h.textContent')==text
 j('document.activeElement.blur();return true;')
 time.sleep(1.2)
 assert j('const b=document.querySelector("#pg-website-builder__btn--save"); if(!b||b.disabled)return false;b.click();return true;')
 time.sleep(2)

def verify_preview(tab,text):
 for _ in range(5):
  try:
   tab.goto(BASE+'?test-blog='+str(time.time_ns()),wait_until='domcontentloaded',timeout=15000)
   tab.wait_for_function('t=>document.querySelector(".s-blog h2")?.textContent.trim()===t',arg=text,timeout=3500)
   assert tab.locator('.s-blog .anim-titular').count()>0
   assert tab.locator('script[type="application/ld+json"]').count()>0
   return
  except TimeoutError: pass
 raise AssertionError('No se reflejó el H2 esperado en la vista previa')

with sync_playwright() as w:
 b=w.chromium.launch(channel='msedge'); t=b.new_page(reduced_motion='reduce');root=Pestana();start()
 if '--restaurar' in sys.argv:
  if j('return h.textContent')==TEMP:write(TEMP,ORIGINAL)
  assert j('return h.textContent')==ORIGINAL
  verify_preview(t,ORIGINAL);root.cmd('Page.reload',ignoreCache=True);start();assert j('return h.textContent')==ORIGINAL
  print('H2 original restaurado y releído en editor y preview');sys.exit(0)
 assert j('return h.textContent')==ORIGINAL
 try:
  write(ORIGINAL,TEMP);verify_preview(t,TEMP)
  root.cmd('Page.reload',ignoreCache=True);start();assert j('return h.textContent')==TEMP
  print('H2 nativo del Blog: edición, guardado, preview y reapertura OK')
 finally:
  if j('return h.textContent')==TEMP:
   write(TEMP,ORIGINAL);verify_preview(t,ORIGINAL)
   root.cmd('Page.reload',ignoreCache=True);start();assert j('return h.textContent')==ORIGINAL
   print('H2 original restaurado y releído en editor y preview')
  else:assert j('return h.textContent')==ORIGINAL
