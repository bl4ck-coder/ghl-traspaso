"""Copia título y descripción aprobados a los campos nativos de ADICIO 2. No publica."""
import json, re, time
from pathlib import Path
from editor9333 import Editor
ref=Path(__file__).resolve().parents[2]/'31-adicio-home-ghl/sitio/index.html'
html=ref.read_text(encoding='utf8')
expected={'Título':re.search(r'<title>([^<]+)</title>',html)[1], 'Descripción':re.search(r'<meta name="description" content="([^"]+)"',html)[1]}
e=Editor()
def js(s):
 pre='if(location.pathname!=="/location/LOCATION_ID/page-builder/PAGE_ID"||!document.body.innerText.includes("ADICIO 2"))throw Error("Destino inesperado");'
 return e.js('(()=>{'+pre+s+'})()')
fields='const f=Object.fromEntries([...document.querySelectorAll("input,textarea")].filter(x=>x.getBoundingClientRect().width&&["Título","Descripción"].includes(x.placeholder)).map(x=>[x.placeholder,x]));'
old=js(fields+'return Object.fromEntries(Object.entries(f).map(([k,n])=>[k,n.value]));')
assert set(old)==set(expected) and all(v in ('',expected[k]) for k,v in old.items()),old
res=js(fields+'const expected='+json.dumps(expected)+'; for(const [k,v] of Object.entries(expected)){const n=f[k];Object.getOwnPropertyDescriptor(Object.getPrototypeOf(n),"value").set.call(n,v);n.dispatchEvent(new Event("input",{bubbles:true}));n.dispatchEvent(new Event("change",{bubbles:true}));n.blur();}return Object.fromEntries(Object.entries(f).map(([k,n])=>[k,n.value]));')
assert res==expected,res
time.sleep(.4)
print(js('return [...document.querySelectorAll("button")].filter(b=>b.getBoundingClientRect().width&&/Guardar|Actualizar/.test(b.textContent.trim())).map(b=>[b.id,b.textContent.trim(),b.disabled]);'))
assert js('const b=document.getElementById("pg-website-builder__btn--save");if(!b||b.disabled)return false;b.click();return true;')
print('Guardado solicitado:',res)
