"""Compara portada original y borrador GHL; --css prueba en memoria sin escribir en GHL."""
import argparse
import json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

p = argparse.ArgumentParser()
p.add_argument('out', type=Path); p.add_argument('--css', type=Path); p.add_argument('--js', type=Path); p.add_argument('--exigir', action='store_true')
a = p.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
u = 'https://sites.leadconnectorhq.com/preview/PAGE_ID'
orig = 'http://127.0.0.1:8831/importar.html'
js = '''() => {
 const names = ['.s-nav','.fila-nav','h1','.bajada','.hero-zonas','.botones','.firma','.col-hero-foto','.hero-foto','.fila-pilares','.pilar'];
 const rect = e => {const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(Math.round)};
 const blocks = Object.fromEntries(names.map(n=>{const e=document.querySelector(n);return [n,e?rect(e):null]}));
 const fonts=[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family.toLowerCase());
 const nav=document.querySelector('.s-nav'); const st=getComputedStyle(nav); const toggle = nav.querySelector('.nav-menu-mobile,.menu-boton');
 return {blocks,fonts:[...new Set(fonts)],sticky:st.position,overflow:document.documentElement.scrollWidth-innerWidth,navToggle:toggle?rect(toggle).slice(2):null,h1:document.querySelector('h1').textContent.trim(),img:[...document.querySelectorAll('.s-nav img,.s-hero img')].filter(i=>i.naturalWidth===0).map(i=>i.src)};
}'''
res = {}
with sync_playwright() as w:
 b = w.chromium.launch(channel='msedge')
 for width,height in ((1920,950),(1024,900),(900,900),(412,915),(360,800)):
  res[width] = {}; canvases = []
  for label,url in [('original',orig),('ghl',u)]:
   page=b.new_page(viewport={'width':width,'height':height},reduced_motion='reduce'); errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
   page.goto(url,wait_until='load',timeout=40000)
   if label=='ghl' and a.css: page.add_style_tag(content=a.css.read_text(encoding='utf-8'))
   if label=='ghl' and a.js: page.add_script_tag(content=a.js.read_text(encoding='utf-8'))
   if label=='ghl' and width<=1120:
    page.wait_for_function("document.querySelector('.s-nav').hasAttribute('data-adicio-menu-listo')",timeout=10000)
   page.evaluate('Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,4000))]).then(()=>null)')
   page.evaluate('''async()=>await Promise.all([...document.querySelectorAll('.s-nav img,.s-hero img')].map(i=>{i.loading='eager';return Promise.race([i.decode().catch(()=>{}),new Promise(r=>setTimeout(r,2500))])})).then(()=>null)''')
   row = page.evaluate(js); row['errors']=errors; res[width][label]=row
   if width in (1920,900,412):
    f=a.out/f'{width}-{label}.png'; page.screenshot(path=f,clip={'x':0,'y':0,'width':width,'height':max(1,round(page.locator('.s-hero').evaluate('e=>e.getBoundingClientRect().bottom')))})
    canvases.append(Image.open(f).convert('RGB'))
   page.close()
  if canvases:
   i,j=canvases; out=Image.new('RGB',(i.width+j.width+12,max(i.height,j.height)),'white'); out.paste(i); out.paste(j,(i.width+12,0)); out.thumbnail((1500,1400)); out.save(a.out/f'{width}-comparacion.jpg',quality=94)
  x,y=res[width].values(); print(width,'alto H1',x['blocks']['h1'][3],y['blocks']['h1'][3],'y H1',x['blocks']['h1'][1],y['blocks']['h1'][1],'foto',x['blocks']['.hero-foto'],y['blocks']['.hero-foto'],'pilares',x['blocks']['.fila-pilares'][3],y['blocks']['.fila-pilares'][3],'fuentes',y['fonts'],'overflow',y['overflow'],'toggle',y['navToggle'],'errores',len(y['errors']))
(a.out/'resultado.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
