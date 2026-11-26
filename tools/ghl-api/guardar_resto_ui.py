"""Carga CSS por el editor de ADICIO 2 exclusivamente. No publica ni usa credenciales."""
import argparse,json,time
from pathlib import Path
from editor9333 import Editor
p=argparse.ArgumentParser();p.add_argument('carpeta',type=Path);p.add_argument('--archivo',default='resto.css');p.add_argument('--marca',default='ADICIO LOTE RESTANTE');a=p.parse_args()
css=(a.carpeta/a.archivo).read_text(encoding='utf8');assert css.count(a.marca)==1
path='/location/LOCATION_ID/page-builder/PAGE_ID'
e=Editor()
def run(s):
 return e.js('(()=>{if(location.pathname!=='+json.dumps(path)+'||!document.body.innerText.includes("ADICIO 2")||!document.querySelector(".s-contacto")||!document.querySelector(".s-pie"))throw Error("Destino inesperado");'+s+'})()')
def wait(s):
 for _ in range(35):
  v=run(s)
  if v:return v
  time.sleep(.2)
 raise RuntimeError('Control no disponible: '+s[:90])
def click(id_):
 rid=json.dumps('#'+id_)
 return wait('const b=[...document.querySelectorAll('+rid+')].find(b=>!b.disabled&&b.getBoundingClientRect().width&&b.textContent.trim()!=="Cancelar");if(!b)return false;b.click();return true;')
C='const cm=document.querySelector(".hl-builder-custom-css-modal .CodeMirror")?.CodeMirror;'
click('hl-builder-custom-css-button');wait(C+'return !!cm;')
prev=run(C+'return cm.getValue();');assert 'ADICIO CONTACTO' in prev
backup=a.carpeta/(a.archivo+'.antes');
if not backup.exists():backup.write_text(prev,encoding='utf8')
assert a.marca not in prev,'Ya hay un bloque con esa marca. Verificar la vista previa antes de modificarlo.'
new=prev.rstrip()+'\n'+css
q=json.dumps(new);assert run(C+'cm.setValue('+q+');return cm.getValue()==='+q+';')
click('hl-builder-custom-css-modal-save-button');click('pg-website-builder__btn--save')
time.sleep(4)
click('hl-builder-custom-css-button');wait(C+'return !!cm;');actual=run(C+'return cm.getValue();')
assert actual.count(a.marca)==1 and 'ADICIO CONTACTO' in actual and 'ADICIO AJUSTE REDES' in actual
print('Bloque leído en el editor:',len(actual.encode()),'bytes totales. GHL puede reformatear el CSS; verificar efecto en la vista previa.')
wait('const b=[...document.querySelectorAll("#hl-builder-custom-css-modal-save-button")].find(b=>b.getBoundingClientRect().width&&b.textContent.trim()==="Cancelar");if(!b)return false;b.click();return true;')
