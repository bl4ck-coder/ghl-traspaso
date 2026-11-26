"""Mide cuatro fallas del editor de ADICIO 2 sin editar ni guardar. --css prueba en memoria."""
import argparse,json
from pathlib import Path
from editor9333 import Editor
p=argparse.ArgumentParser();p.add_argument('--css',type=Path);a=p.parse_args()
e=Editor()
pre="if(!location.pathname.endsWith('/PAGE_ID') || !document.querySelector('#page-creator .previewer .s-blog')) throw Error('Destino equivocado');"
if a.css:
    e.js("(()=>{"+pre+"const s=document.createElement('style');s.id='adicio-paridad-temporal';s.textContent="+json.dumps(a.css.read_text(encoding='utf8'))+"; document.head.append(s)})()")
try:
    r=e.js('(()=>{'+pre+'''const all=s=>[...document.querySelectorAll('#page-creator .previewer '+s)];
const box=n=>n.getBoundingClientRect(); const widths=s=>all(s).map(n=>Math.round(box(n).width));
const overlap=s=>{const ns=all(s).map(box).filter(b=>b.width&&b.height);return ns.flatMap((a,i)=>ns.slice(i+1).map(b=>Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left))*Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)))).filter(n=>n>1).length};
const circles=all('.s-pie button.red-circulo').map(n=>[getComputedStyle(n.querySelector('.main-heading-button')).clipPath,getComputedStyle(n,':after').backgroundImage]);
const contact=all('.s-contacto button.red').map(n=>[getComputedStyle(n,':before').backgroundImage,getComputedStyle(n,':after').content]);
return {viewport:innerWidth,blog:widths('.s-blog .col-blog .tiptap p'),hero:widths('.s-hero .botones button.boton'),heroCruces:overlap('.s-hero .botones button.boton'),contactoCruces:overlap('.s-contacto .redes button.red'),contacto:contact,pie:widths('.s-pie .redes-pie button.red-circulo'),pieCruces:overlap('.s-pie .redes-pie button.red-circulo'),circulos:circles,bloquesNativos:all('.s-blog .c-paragraph .tiptap').length};})()''')
finally:
    if a.css:e.js("document.getElementById('adicio-paridad-temporal')?.remove()")
print(json.dumps(r,ensure_ascii=False));
assert r['blog'] and min(r['blog'])>180 and r['bloquesNativos']==3
assert len(r['hero'])==2 and min(r['hero'])>130 and r['heroCruces']==0
assert len(r['contacto'])==4 and r['contactoCruces']==0 and all(icon!='none' and second=='none' for icon,second in r['contacto'])
assert len(r['pie'])==4 and min(r['pie'])>=40 and r['pieCruces']==0 and all(clip!='none' and icon!='none' for clip,icon in r['circulos'])