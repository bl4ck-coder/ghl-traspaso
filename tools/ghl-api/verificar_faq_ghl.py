"""Prueba las tres preguntas de ADICIO 2 con clic y teclado, sin guardar ni publicar."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--capa',type=Path);a=p.parse_args()
U='https://sites.leadconnectorhq.com/preview/PAGE_ID'
M='''(h)=>new Promise(resolve=>{const q=h.nextElementSibling,t=performance.now(), r=[];function frame(){r.push([Math.round(performance.now()-t), Math.round(q.getBoundingClientRect().height),h.getAttribute('aria-expanded')]);if(performance.now()-t<865)requestAnimationFrame(frame);else resolve(r)}; frame()})'''
with sync_playwright() as w:
 b=w.chromium.launch(channel='msedge')
 for width in (1920,412):
  q=b.new_page(viewport={'width':width,'height':950 if width==1920 else 915}); errs=[];q.on('pageerror',lambda e:errs.append(str(e)))
  if a.capa:q.add_init_script("window.__adicioCapa={estado:'bloqueada'}")
  q.goto(U,wait_until='networkidle'); q.locator('.s-faq').scroll_into_view_if_needed()
  if a.capa:q.evaluate('delete window.__adicioCapa');q.add_script_tag(content=a.capa.read_text(encoding='utf8'))
  h=q.locator('.s-faq .hl-faq-child-heading'); h.first.wait_for();assert h.count()==3
  for i in range(3):
   n=h.nth(i); n.scroll_into_view_if_needed();q.wait_for_function("i=>document.querySelectorAll('.s-faq .hl-faq-child-heading')[i].getAttribute('role')==='button'",arg=i,timeout=4500)
   vals=[]
   for action in ('open','close'):
    n.evaluate('(h,f)=>{window.faqMedida=eval(f)(h)}',M)
    if action=='open':n.locator('h3').click()
    else:n.press('Enter')
    frames=q.evaluate('window.faqMedida'); top=max(x[1] for x in frames); last=frames[-1]; mid=sum(1 for _,px,_ in frames if 0<px<top)
    assert top>=40 and mid>=4 and ((last[1]>=40 and last[2]=='true') if action=='open' else (last[1]==0 and last[2]=='false')), (width,i,action,top,mid,last)
    vals.append([top,mid,last[1]])
   print(width,i+1,vals)
  assert not errs,errs
  q.close()
 q=b.new_page(viewport={'width':412,'height':915},reduced_motion='reduce'); errs=[];q.on('pageerror',lambda e:errs.append(str(e)))
 if a.capa:q.add_init_script("window.__adicioCapa={estado:'bloqueada'}")
 q.goto(U,wait_until='networkidle');q.locator('.s-faq').scroll_into_view_if_needed()
 if a.capa:q.evaluate('delete window.__adicioCapa');q.add_script_tag(content=a.capa.read_text(encoding='utf8'))
 n=q.locator('.s-faq .hl-faq-child-heading').first
 q.wait_for_function("document.querySelector('.s-faq .hl-faq-child-heading')?.getAttribute('role')==='button'")
 measure="h=>[h.getAttribute('aria-expanded'),h.nextElementSibling.getBoundingClientRect().height,document.documentElement.classList.contains('capa-activa')]"
 n.press('Space');opened=n.evaluate(measure);n.press('Space');closed=n.evaluate(measure)
 assert opened[0]=='true' and opened[1]>40 and opened[2] is False,opened
 assert closed==['false',0,False] and not errs,(closed,errs)
 print('412 movimiento reducido:',opened,closed)
 q.close()
