"""Solo el formulario dedicado al borrador ADICIO 2. GET por defecto, --guardar escribe y relee."""
import argparse,json,time
from pathlib import Path
from editor9333 import Editor
pa=argparse.ArgumentParser();pa.add_argument('--css',type=Path);pa.add_argument('--respaldo',type=Path);pa.add_argument('--guardar',action='store_true');a=pa.parse_args()
ID='FORM_ID'; NAME='Suscripción novedades ADICIO (estilo)'; LOC='LOCATION_ID'; PAGE='PAGE_ID'
e=Editor(); assert e.js("location.pathname==='/location/"+LOC+"/page-builder/"+PAGE+"'&&document.body.innerText.includes('ADICIO 2')&&document.querySelector('.s-novedades iframe')?.src.includes('"+ID+"')")
BASE='''const db=await new Promise((ok,err)=>{const q=indexedDB.open('firebaseLocalStorageDb');q.onsuccess=()=>ok(q.result);q.onerror=()=>err(q.error)});const rows=await new Promise((ok,err)=>{const q=db.transaction('firebaseLocalStorage').objectStore('firebaseLocalStorage').getAll();q.onsuccess=()=>ok(q.result);q.onerror=()=>err(q.error)});const token=rows.find(o=>o.value?.stsTokenManager?.accessToken)?.value.stsTokenManager.accessToken;if(!token)throw Error('Sesión no disponible');const headers={'token-id':token,channel:'APP',source:'WEB_USER',version:'2021-07-28','content-type':'application/json'};const url='https://backend.leadconnectorhq.com/forms/'+'''+json.dumps(ID)+''';'''
def run(t):return e.js('(async()=>{'+BASE+t+'})()')
READ='''const r=await fetch(url,{headers,cache:'no-store'});if(!r.ok)throw Error('GET '+r.status);const raw=await r.json(), f=raw.form || raw;if(f._id!=='''+json.dumps(ID)+'''||f.name!=='''+json.dumps(NAME)+'''||f.locationId!=='''+json.dumps(LOC)+''')throw Error('Destino inesperado');const v=[...(f.versionHistory||[])].sort((a,b)=>new Date(b.dateAdded||b.createdAt||0)-new Date(a.dateAdded||a.createdAt||0))[0];const d=v?.formDataDownloadUrl?await (await fetch(v.formDataDownloadUrl,{cache:'no-store'})).json():f.formData;if(!d?.form)throw Error('formData ausente');return d;'''
data=run(READ);f=data['form'];print('Formulario:',ID, NAME,'campos',[x.get('tag') for x in f['fields']], 'CSS generado',len(f.get('fieldCSS','')),'CSS propio',len(f.get('customStyle','')))
if a.guardar:
 assert a.css and a.respaldo and not a.respaldo.exists()
 assert sorted(x.get('tag') for x in f['fields'])==['button','email']
 a.respaldo.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 css=a.css.read_text(encoding='utf8').strip();old=f.get('fieldCSS','');assert 'ADICIO FORM IFRAME 1' not in old and 'ADICIO FORM IFRAME 1' in css
 f['fieldCSS']=old.rstrip()+'\n'+css
 payload={'name':NAME,'formData':data}
 status=run('const r=await fetch(url,{method:"POST",headers,body:JSON.stringify('+json.dumps(payload,ensure_ascii=True)+')});return r.status;');print('Guardado HTTP',status);assert status in (200,201)
 for _ in range(7):
  actual=run(READ)
  if actual['form'].get('fieldCSS')==f['fieldCSS']:break
  time.sleep(1.5)
 else:raise AssertionError('El CSS no se leyó de vuelta exacto')
 print('CSS verificado exacto:',len(f['fieldCSS']),'caracteres; campos preservados:',actual['form']['fields']==f['fields'])
