"""Prueba qué forma de JSON-LD acepta el validador del modal de esquema de ADICIO 2 (no publica).
Uso: python probar_esquema.py <variante>   variante: graph | nodo0 | lista | ...
Reemplaza el texto del editor JSON del modal abierto y aprieta «Validar»; imprime el resultado.
"""
import json, re, sys, time
from pathlib import Path
from editor9333 import Editor

ref = Path(__file__).resolve().parents[2] / '31-adicio-home-ghl/sitio/index.html'
schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', ref.read_text(encoding='utf8'), re.S)[1])
media = 'https://adicio-ghl-prueba.vercel.app/'
for row in schema['@graph']:
    for k in ('logo', 'image'):
        if str(row.get(k, '')).startswith('media/'):
            row[k] = media + row[k]
BASE = 'https://adicio.com.ar/'
def abs_ids(o):
    if isinstance(o, dict):
        return {k: (BASE + v if k == '@id' and isinstance(v, str) and v.startswith('#') else abs_ids(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [abs_ids(x) for x in o]
    return o

var = sys.argv[1]
if var == 'graph':
    obj = schema
elif var == 'graph-abs':
    obj = abs_ids(schema)
elif var.startswith('nodo'):
    i = int(var[4:]); obj = {'@context': 'https://schema.org', **abs_ids(schema['@graph'][i])}
elif var == 'lista':
    obj = [{'@context': 'https://schema.org', **abs_ids(n)} for n in schema['@graph']]
elif var == 'script':
    obj = None
elif var == 'todos':
    nodes = [abs_ids(n) for n in schema['@graph']]
    for n in nodes:
        if n.get('@type') == 'WebSite': n['url'] = BASE
    schema_txt = {'@context': 'https://schema.org', '@graph': [{'@context': 'https://schema.org', **n} for n in nodes]}; obj = None
elif var == 'website-url':
    n = abs_ids(schema['@graph'][2]); n['url'] = BASE
    schema_txt = {'@context': 'https://schema.org', '@graph': [{'@context': 'https://schema.org', **n}]}; obj = None
elif var.startswith('s:'):
    idx = [int(x) for x in var[2:].split(',')]
    g = {'@context': 'https://schema.org', '@graph': [{'@context': 'https://schema.org', **abs_ids(schema['@graph'][i])} for i in idx]}
    obj = None; schema_txt = g
else:
    raise SystemExit('variante desconocida')
if obj is None:
    text = '<script type="application/ld+json">' + json.dumps(globals().get('schema_txt') or abs_ids(schema), ensure_ascii=False, indent=2) + '</script>'
else:
    text = json.dumps(obj, ensure_ascii=False, indent=2)

e = Editor()
if '--abrir' in sys.argv:
    def clic(x, y):
        e.cmd('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y); time.sleep(.2)
        for t in ('mousePressed', 'mouseReleased'):
            e.cmd('Input.dispatchMouseEvent', type=t, x=x, y=y, button='left', clickCount=1)
    def centro(texto, dentro='*'):
        L = json.loads(e.js('JSON.stringify([...document.querySelectorAll(' + json.dumps(dentro) + ')].filter(n=>n.children.length===0&&n.textContent.trim()===' + json.dumps(texto) + '&&n.getBoundingClientRect().width).map(n=>{const b=n.getBoundingClientRect();return [Math.round(b.x+b.width/2),Math.round(b.y+b.height/2)]}))'))
        if not L: raise SystemExit('no encuentro: ' + texto)
        return L[0]
    clic(*centro('Nuevo esquema')); time.sleep(1.5)
    clic(*centro('Añadir esquema')); time.sleep(3)
    clic(*centro('Vista JSON', '[role=dialog] *')); time.sleep(2)
G = ('const n=document.querySelector("[role=dialog] .cm-content");'
     'if(location.pathname!=="/location/LOCATION_ID/page-builder/PAGE_ID"||!n)throw Error("Destino inesperado");')
def js(s):
    return e.js('(()=>{' + G + s + '})()')
ok = js('const v=n.cmView&&n.cmView.view;if(!v)return "sin-view";'
        'v.dispatch({changes:{from:0,to:v.state.doc.length,insert:' + json.dumps(text) + '}});'
        'return v.state.doc.toString()===' + json.dumps(text) + ';')
print('cargado:', ok)
if ok is not True:
    raise SystemExit(1)
time.sleep(0.6)
js('const b=document.getElementById("schema-save-btn");b.click();return 1;')
time.sleep(2.5)
print(e.js('(()=>{const n=document.querySelector("[role=dialog] .cm-content");if(!n)return "modal-cerrado (aceptado)";const d=n.closest("[role=dialog]");'
         'const t=d.innerText;const i=t.search(/problema|error|inv[aá]lid/i);'
         'return JSON.stringify(i<0?"modal abierto sin error":t.slice(i,i+300));})()'))
