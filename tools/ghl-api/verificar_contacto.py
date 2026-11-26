"""Compara Contacto en el original y el borrador, sin escribir nada en GHL."""
from pathlib import Path
import argparse,json
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--css',type=Path);p.add_argument('--js',type=Path);p.add_argument('--width',type=int,action='append');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
sizes=[(w,h) for w,h in [(1920,950),(1180,900),(900,900),(412,915),(360,800)] if not a.width or w in a.width]
u={'original':'http://127.0.0.1:8831/','ghl':'https://sites.leadconnectorhq.com/preview/PAGE_ID'}
out={}
with sync_playwright() as w:
 b=w.chromium.launch(channel='msedge')
 for width,height in sizes:
  for label,url in u.items():
   page=b.new_page(viewport={'width':width,'height':height},has_touch=width<500,is_mobile=width<500); err=[];page.on('pageerror',lambda x:err.append(str(x)))
   if label=='ghl' and a.js: page.add_init_script(path=a.js)
   r=page.goto(url,wait_until='domcontentloaded',timeout=35000); assert r.ok,(r.status,url)
   page.wait_for_selector('.s-contacto',timeout=15000)
   if label=='ghl' and a.css: page.add_style_tag(content=a.css.read_text(encoding='utf8'))
   page.evaluate('document.fonts.ready.then(()=>null)')
   page.wait_for_function("window.__adicioCapa?.mapa==='en línea'",timeout=15000)
   page.locator('.mapa-caja').evaluate('x=>window.scrollTo({top:x.getBoundingClientRect().top+scrollY-innerHeight*.35,behavior:"instant"})')
   try: page.wait_for_selector('.capa-mapa.capa-listo',timeout=7500)
   except Exception:
    print(width,label,page.evaluate('''()=>({w:innerWidth,h:innerHeight,y:scrollY,max:document.documentElement.scrollHeight-innerHeight,map:document.querySelector('.mapa-caja').getBoundingClientRect().toJSON(),svg:document.querySelector('.capa-mapa')?.getBoundingClientRect().toJSON(),estado:window.__adicioCapa, imgs:[...document.querySelectorAll('.mapa-caja img')].map(n=>[n.className,n.naturalWidth]),st:window.ScrollTrigger?.getAll().filter(x=>x.trigger?.matches('.mapa-caja')).map(x=>[x.start,x.end,x.progress,x.isActive]),redes:[...document.querySelectorAll('.s-contacto .red')].map(e=>[e.clientWidth,e.textContent.trim()])})'''),flush=True)
    raise
   page.locator('.s-contacto').screenshot(path=a.out/f'{width}-{label}.png',timeout=15000)
   data=page.evaluate('''()=>{const c=document.querySelector('.s-contacto');const b={}; for(const s of ['.tarjeta-contacto','.tarjeta-cobertura','.tarjeta-contacto h2','.tarjeta-cobertura h2','.datos','.dato','.redes','.mapa-caja','.zonas','.zona','.zona-nombre','.zona-consulta']){const e=c.querySelector(s);if(e){const r=e.getBoundingClientRect(),t=getComputedStyle(e);b[s]=[r.x,r.y-c.getBoundingClientRect().y,r.width,r.height].map(Math.round);if(s==='.zona-nombre')b['rol']=e.getAttribute('role')}} return {b,overflow:document.documentElement.scrollWidth-innerWidth, links:[...c.querySelectorAll('a[href]')].map(x=>x.getAttribute('href')),txt:c.innerText.replace(/\\s+/g,' ').trim(),map:document.querySelectorAll('.capa-mapa').length}}''')
   z=page.get_by_role('button',name='Corredor Norte del AMBA',exact=True);m=page.locator('.capa-mapa');data['behavior']=[]
   if width<500:
    z.tap();data['behavior'].append((m.get_attribute('data-foco'),z.get_attribute('aria-pressed')))
   else:
    z.hover();data['behavior'].append((m.get_attribute('data-foco'),z.get_attribute('aria-pressed')));z.focus();z.press('Enter');data['behavior'].append((m.get_attribute('data-foco'),z.get_attribute('aria-pressed')))
   z.press('Escape');data['reset']=(m.get_attribute('data-foco'),z.get_attribute('aria-pressed'));data['errors']=err
   out[f'{width}-{label}']=data; print(width,label,'tarjetas',data['b']['.tarjeta-contacto'],data['b']['.tarjeta-cobertura'],'mapa',data['b']['.mapa-caja'], 'overflow',data['overflow'],'gestos',data['behavior'],data['reset'],err,flush=True)
   page.close()
 b.close()
(a.out/'resultado.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for width,_ in sizes:
 x,y=(out[f'{width}-{l}'] for l in u)
 assert x['links']==y['links'],(width,x['links'],y['links'])
 for z in [x,y]: assert z['map']==1 and not z['overflow'] and not z['errors'] and z['behavior'][-1]==('norte','true') and z['reset']==(None,'false'),(width,z)
