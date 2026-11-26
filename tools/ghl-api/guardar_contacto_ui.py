"""Agrega CSS y adaptador de mapa usando los campos visibles de ADICIO 2. Nunca publica."""
import argparse, json, time
from pathlib import Path
from editor9333 import Editor

ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--agregar-css',type=Path);a=ap.parse_args()
css=(a.out/'contacto.css').read_text(encoding='utf8')
js=Path(__file__).with_name('mapa-ghl.js').read_text(encoding='utf8')
e=Editor()
path='/location/LOCATION_ID/page-builder/PAGE_ID'
def j(s):
 return e.js('(()=>{if(location.pathname!=='+json.dumps(path)+'||!document.body.innerText.includes("ADICIO 2")||document.querySelectorAll(".s-contacto").length!==1)throw Error("Destino inesperado");'+s+'})()')
def wait(s):
 for _ in range(30):
  v=j(s)
  if v:return v
  time.sleep(.2)
 raise RuntimeError('No apareció el control esperado')
def click(id_):
 return wait('const b=[...document.querySelectorAll("#'+id_+'")].find(b=>!b.disabled&&b.getBoundingClientRect().width&&b.textContent.trim()!=="Cancelar");if(!b)return false;b.click();return true;')
C='const cm=document.querySelector(".hl-builder-custom-css-modal .CodeMirror")?.CodeMirror;'
B='const es=[...document.querySelectorAll(".n-tab-pane .CodeMirror")].filter(b=>b.getBoundingClientRect().width);const cm=es.length===1&&es[0].CodeMirror;'

def set_field(expr,current,addition,marker,name):
 p=a.out/name
 if not p.exists():p.write_text(current,encoding='utf8')
 if marker in current:
  assert current.endswith(addition) or current.startswith(addition),name+' ya tiene otro bloque con esa marca'
  new=current
 else:new=(current.rstrip()+'\n'+addition) if name.startswith('css') else (addition+'\n'+current)
 q=json.dumps(new)
 assert j(expr+'cm.setValue('+q+');return cm.getValue()==='+q+';'),name
 return len(new)

click('hl-builder-custom-css-button');wait(C+'return !!cm;')
old=j(C+'return cm.getValue();')
assert 'reglas originales portadas' in old
if a.agregar_css:
 addition=a.agregar_css.read_text(encoding='utf8')
 assert 'ADICIO CONTACTO' in old and 'ADICIO AJUSTE REDES' in addition
 print('CSS',set_field(C,old,addition,'ADICIO AJUSTE REDES','css-antes-ajuste-redes.txt'))
 click('hl-builder-custom-css-modal-save-button');click('pg-website-builder__btn--save')
 raise SystemExit(0)
print('CSS',set_field(C,old,css,'ADICIO CONTACTO','css-antes-contacto.txt'))
click('hl-builder-custom-css-modal-save-button')
click('hl-builder-tracking-code-button')
wait('const t=[...document.querySelectorAll("[role=tab],.n-tabs-tab")].find(b=>b.textContent.trim()==="Seguimiento de pie de página"&&b.getBoundingClientRect().width);if(!t)return false;t.click();return true;')
wait(B+'return !!cm;');old=j(B+'return cm.getValue();')
assert 'ADICIO PILOTO' in old
print('Body',set_field(B,old,'<script>'+js+'</script>','ADICIO MAPA GHL v2','body-antes-contacto.txt'))
click('hl-builder-tracking-code-modal-save-button');click('pg-website-builder__btn--save')
print('Guardado solicitado; verificar en la vista previa sin inyección.')
