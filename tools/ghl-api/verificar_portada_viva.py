"""Prueba la portada guardada en GHL, sin inyectar código ni escribir en el sitio."""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

U='https://sites.leadconnectorhq.com/preview/PAGE_ID'
OUT=Path(sys.argv[1]); OUT.mkdir(parents=True,exist_ok=True)
results={}; failures=[]
def check(ok, name):
    if not ok: failures.append(name)
with sync_playwright() as pw:
    b=pw.chromium.launch(channel='msedge')
    for w,h,reduce in [(1920,950,False),(900,900,False),(412,915,False),(412,915,True)]:
        k=f'{w}-'+('quieta' if reduce else 'activa'); p=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce' if reduce else 'no-preference'); errs=[]
        p.on('pageerror',lambda x:errs.append(str(x)))
        p.goto(U,wait_until='load',timeout=45000)
        p.wait_for_function("['activa','quieta','sin-gsap'].includes(window.__adicioCapa?.estado)",timeout=15000)
        p.evaluate('document.fonts.ready.then(()=>null)')
        d=p.context.new_cdp_session(p); d.send('DOM.enable'); d.send('CSS.enable'); root=d.send('DOM.getDocument')['root']['nodeId']; h1=d.send('DOM.querySelector',{'nodeId':root,'selector':'.s-hero h1'})['nodeId']; fonts=d.send('CSS.getPlatformFontsForNode',{'nodeId':h1})['fonts']
        item=p.evaluate('''()=>({estado:window.__adicioCapa?.estado, total:document.querySelectorAll('.capa-corazon-hero').length,horizontal:document.documentElement.scrollWidth-innerWidth, fondo:getComputedStyle(document.querySelector('.col-hero-foto')).backgroundImage, boton:[...document.querySelectorAll('.s-hero .boton')].map(x=>[x.tagName,x.getAttribute('href')]),marca:document.documentElement.className})''')
        item['fuentes_h1']=fonts; item['errores']=errs; results[k]=item
        check(item['estado']==('quieta' if reduce else 'activa'),k+' estado capa')
        check(item['total']==(0 if reduce else 1),k+' un corazón o versión quieta')
        if reduce: check('corazon-degrade.svg' in item['fondo'],k+' corazón estático visible')
        check(item['horizontal']==0,k+' desborde')
        check(not errs,k+' errores JS')
        check(any('bricolage' in (f['familyName']+' '+f['postScriptName']).lower() for f in fonts),k+' fuente usada para pintar H1')
        if not reduce:
            light=p.locator('.capa-corazon-hero path').last
            s1=light.evaluate('e=>[e.style.strokeDashoffset,e.style.opacity]') if item['total'] else []
            p.wait_for_timeout(550)
            s2=light.evaluate('e=>[e.style.strokeDashoffset,e.style.opacity]') if item['total'] else []
            p.wait_for_timeout(2500)
            # At rest the light should be gone. It may already have finished before s1 on a slow font load.
            s3=light.evaluate('e=>[e.style.strokeDashoffset,e.style.opacity]') if item['total'] else []
            item['luz']=[s1,s2,s3]
            check(s3 and float(s3[1])==0,k+' luz termina')
        if w<=1120:
            t=p.get_by_role('button',name='Menú principal'); t.focus(); t.press('Enter')
            p.wait_for_function("document.querySelector('.nav-menu-mobile').getAttribute('aria-expanded')==='true'")
            links=p.locator('.nav-menu-desktop .menu-item a'); item['enlaces_menu']=links.count()
            check(links.count()==6 and links.first.is_visible(),k+' menú abierto')
            p.screenshot(path=OUT/f'{k}-menu.png')
            p.keyboard.press('Escape'); check(t.get_attribute('aria-expanded')=='false' and t.evaluate('el=>el===document.activeElement'),k+' Escape devuelve foco')
            t.click(); links.first.click(); check(t.get_attribute('aria-expanded')=='false',k+' elegir enlace cierra')
        p.close()
    b.close()
(OUT/'viva.json').write_text(json.dumps({'medidas':results,'fallas':failures},ensure_ascii=False,indent=2),encoding='utf-8')
for k,d in results.items(): print(k,d['estado'],'corazón',d['total'],'fuentes',[x['familyName'] for x in d['fuentes_h1']],'menú',d.get('enlaces_menu'),'luz',d.get('luz'))
print('Fallas:',failures)
sys.exit(bool(failures))
