"""Agrega un <script> al código de pie de página de ADICIO 2 (una vez, por marca). Nunca publica."""
import argparse, json, time
from pathlib import Path
from editor9333 import Editor
ap=argparse.ArgumentParser();ap.add_argument('js',type=Path);ap.add_argument('--marca',required=True);ap.add_argument('--respaldo',type=Path,required=True);ap.add_argument('--reemplazar',type=Path);a=ap.parse_args()
script=a.js.read_text(encoding='utf8').strip();assert script.count(a.marca)==1
code='<script>'+script+'</script>'
e=Editor();path='/location/LOCATION_ID/page-builder/PAGE_ID'
def j(s): return e.js('(()=>{if(location.pathname!=='+json.dumps(path)+'||!document.body.innerText.includes("ADICIO 2"))throw Error("Destino inesperado");'+s+'})()')
def wait(s):
 for _ in range(35):
  v=j(s)
  if v:return v
  time.sleep(.2)
 raise RuntimeError('Control no disponible: '+s[:80])
def click(i): return wait('const b=[...document.querySelectorAll("#'+i+'")].find(b=>!b.disabled&&b.getBoundingClientRect().width&&b.textContent.trim()!=="Cancelar");if(!b)return false;b.click();return true;')
B='const es=[...document.querySelectorAll(".n-tab-pane .CodeMirror")].filter(b=>b.getBoundingClientRect().width);const cm=es.length===1&&es[0].CodeMirror;'
click('hl-builder-tracking-code-button')
wait('const t=[...document.querySelectorAll("[role=tab],.n-tabs-tab")].find(b=>b.textContent.trim()==="Seguimiento de pie de página"&&b.getBoundingClientRect().width);if(!t)return false;t.click();return true;')
wait(B+'return !!cm;');old=j(B+'return cm.getValue();')
assert 'ADICIO MAPA GHL' in old, 'No es el body esperado'
if a.marca in old:
 assert old.count(a.marca)==1
 print('Ya estaba; no cambio nada')
else:
 if a.reemplazar:
  anterior=a.reemplazar.read_text(encoding='utf8').strip()
  assert anterior and old.count(anterior)==1, 'El bloque anterior debe coincidir exactamente una vez'
  new=old.replace(anterior,script,1)
 else: new=old.rstrip()+'\n'+code
 if a.respaldo.exists(): assert a.respaldo.read_text(encoding='utf8')==old, 'Respaldo previo no coincide'
 else: a.respaldo.write_text(old,encoding='utf8')
 q=json.dumps(new)
 assert j(B+'cm.setValue('+q+');return cm.getValue()==='+q+';')
 click('hl-builder-tracking-code-modal-save-button');click('pg-website-builder__btn--save'); print('Body', len(new), 'caracteres; guardado pedido')
