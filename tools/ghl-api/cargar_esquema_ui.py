"""Pega el JSON-LD aprobado en Vista JSON del modal nativo de ADICIO 2. No publica."""
import json, re, time
from pathlib import Path
from editor9333 import Editor

ref=Path(__file__).resolve().parents[2]/'31-adicio-home-ghl/sitio/index.html'
schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',ref.read_text(encoding='utf8'),re.S)[1])
media='https://adicio-ghl-prueba.vercel.app/'
for row in schema['@graph']:
    for k in ('logo','image'):
        if str(row.get(k,'')).startswith('media/'): row[k]=media+row[k]
text=json.dumps(schema,ensure_ascii=False)
e=Editor()
G='const n=document.querySelector("[role=dialog] .cm-content");if(location.pathname!=="/location/LOCATION_ID/page-builder/PAGE_ID"||!document.body.innerText.includes("ADICIO 2")||!n)throw Error("Destino inesperado");'
def js(s): return e.js('(()=>{'+G+s+'})()')
assert js('if(n.textContent.trim())return false;n.focus();return document.activeElement===n;')
e.cmd('Input.insertText',text=text)
assert json.loads(js('return n.textContent;'))==schema
assert js('const b=document.getElementById("schema-save-btn");if(!b||b.disabled)return false;b.click();return true;')
time.sleep(2)
print(e.js('''[document.body.innerText.split(String.fromCharCode(10)).slice(-22),[...document.querySelectorAll('[role=dialog] button')].filter(b=>b.getBoundingClientRect().width).map(b=>[b.id,b.textContent.trim(),b.disabled])]'''))
