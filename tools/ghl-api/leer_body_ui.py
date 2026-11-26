"""Lee el código de seguimiento de pie (Body) de ADICIO 2 y lo guarda en un archivo. No cambia nada."""
import json, sys, time
from pathlib import Path
from editor9333 import Editor
e = Editor(); path = '/location/LOCATION_ID/page-builder/PAGE_ID'
def j(s): return e.js('(()=>{if(location.pathname!==' + json.dumps(path) + ')throw Error("Destino inesperado");' + s + '})()')
def wait(s):
    for _ in range(35):
        v = j(s)
        if v: return v
        time.sleep(.2)
    raise RuntimeError('no disponible: ' + s[:80])
wait('const b=[...document.querySelectorAll("#hl-builder-tracking-code-button")].find(b=>b.getBoundingClientRect().width);if(!b)return false;b.click();return true;')
wait('const t=[...document.querySelectorAll("[role=tab],.n-tabs-tab")].find(b=>b.textContent.trim()==="Seguimiento de pie de página"&&b.getBoundingClientRect().width);if(!t)return false;t.click();return true;')
B = 'const es=[...document.querySelectorAll(".n-tab-pane .CodeMirror")].filter(b=>b.getBoundingClientRect().width);const cm=es.length===1&&es[0].CodeMirror;'
wait(B + 'return !!cm;')
v = j(B + 'return cm.getValue();')
Path(sys.argv[1]).write_text(v, encoding='utf-8')
j('const b=[...document.querySelectorAll("button")].find(b=>b.textContent.trim()==="Cancelar"&&b.getBoundingClientRect().width);if(b)b.click();return true;')
print(len(v))
