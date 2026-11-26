"""Crea en ADICIO el formulario «Suscripción novedades» (solo email + botón) duplicando la forma del base. No publica nada."""
import json
CSS = '''@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;700&display=swap');
#_builder-form{padding:0!important;background:transparent!important}
#_builder-form .form-side>.row,#_builder-form .fields-container{display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;gap:10px!important;margin:0!important;padding:0!important}
#_builder-form .form-field-wrapper{margin:0!important;padding:0!important;width:auto!important;max-width:none!important}
#_builder-form .form-field-wrapper[id*=_email_]{flex:1 1 auto!important;min-width:0}
#_builder-form .form-field-wrapper[id*=_button_]{flex:none!important}
#_builder-form .form-builder--btn-submit{margin:0!important}
#_builder-form .email-input-wrapper svg{display:none!important}
#_builder-form input[type=email]{min-height:56px!important;padding:0 22px!important;border-radius:999px!important;border:1.5px solid rgba(10,43,78,.35)!important;background:#fff!important;font:500 18px/1.2 Figtree,system-ui,sans-serif!important;color:#14212E!important;box-shadow:none!important}
#_builder-form input::placeholder{color:#4A5867!important;font-family:Figtree,system-ui,sans-serif!important}
#_builder-form button.button-element{min-height:56px!important;width:auto!important;padding:0 28px!important;border-radius:999px!important;background:#005EB8!important;border:0!important;font:700 18px/1 Figtree,system-ui,sans-serif!important;color:#fff!important;box-shadow:0 14px 30px -14px rgba(0,94,184,.7)!important}
#_builder-form button.button-element:hover{background:#0A2B4E!important}
@media(max-width:640px){#_builder-form .form-side>.row,#_builder-form .fields-container{flex-direction:column!important}#_builder-form .form-field-wrapper[id*=_button_],#_builder-form button.button-element{width:100%!important}}'''
from pathlib import Path
from editor9333 import Editor
D = Path(__file__).resolve().parent.parent / 'datos'
base = json.loads((D / 'form-base.json').read_text(encoding='utf-8'))['data']['form']
email = next(f for f in base['fields'] if f['tag'] == 'email')
boton = next(f for f in base['fields'] if f['tag'] == 'button')
email = {**email, 'label': 'Email', 'placeholder': 'Ingresa tu mejor email', 'required': True, 'preview': ''}
boton = {**boton, 'label': 'Suscribite', 'bgColor': '005EB8FF', 'fullwidth': False, 'radius': 999, 'borderRadius': 999}
form = {**base, 'fields': [email, boton], 'formLabelVisible': False, 'customStyle': CSS}
form['formAction'] = {**base['formAction'], 'actionType': '2', 'thankyouText': '<p style="margin:0;font-family:Figtree,Arial,sans-serif;color:#0A2B4E;font-weight:600">¡Listo! Te vamos a escribir con las novedades de ADICIO.</p>'}
body = {'locationId': 'LOCATION_ID', 'name': 'Suscripción novedades ADICIO (estilo)', 'formData': {'form': form}}
(D / 'form-suscripcion-body.json').write_text(json.dumps(body, ensure_ascii=False), encoding='utf-8')
JS = '''(async (body) => {
  const db = await new Promise((ok, ko) => { const q = indexedDB.open('firebaseLocalStorageDb'); q.onsuccess = () => ok(q.result); q.onerror = () => ko(q.error) });
  const all = await new Promise(ok => { const r = db.transaction('firebaseLocalStorage').objectStore('firebaseLocalStorage').getAll(); r.onsuccess = () => ok(r.result) });
  const tok = all.map(x => x.value && x.value.stsTokenManager && x.value.stsTokenManager.accessToken).find(Boolean);
  const H = {'token-id': tok, 'channel': 'APP', 'source': 'WEB_USER', 'version': '2021-07-28', 'content-type': 'application/json'};
  const lst = await (await fetch('https://backend.leadconnectorhq.com/forms/?locationId=LOCATION_ID&limit=50', {headers: H})).json();
  const ya = lst.forms.find(f => f.name === body.name);
  if (ya) return JSON.stringify({ya: ya._id});
  const r = await fetch('https://backend.leadconnectorhq.com/forms/', {method: 'POST', headers: H, body: JSON.stringify(body)});
  return JSON.stringify({status: r.status, text: (await r.text()).slice(0, 800)});
})(''' + json.dumps(body, ensure_ascii=False) + ')'
print(Editor().js(JS))
