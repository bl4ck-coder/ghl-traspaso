"""Pone el estilo de ADICIO en el CSS propio del formulario de suscripción (vale en editor y en página). No publica."""
import json
from editor9333 import Editor
CSS = """@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;700&display=swap');
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
@media(max-width:640px){#_builder-form .form-side>.row,#_builder-form .fields-container{flex-direction:column!important}#_builder-form .form-field-wrapper[id*=_button_],#_builder-form button.button-element{width:100%!important}}"""
JS = '''(async (css) => {
  const db = await new Promise(o => { const q = indexedDB.open('firebaseLocalStorageDb'); q.onsuccess = () => o(q.result) });
  const a = await new Promise(o => { const r = db.transaction('firebaseLocalStorage').objectStore('firebaseLocalStorage').getAll(); r.onsuccess = () => o(r.result) });
  const t = a.map(x => x.value && x.value.stsTokenManager && x.value.stsTokenManager.accessToken).find(Boolean);
  const H = {'token-id': t, channel: 'APP', source: 'WEB_USER', version: '2021-07-28', 'content-type': 'application/json'};
  const ID = 'FORM_ID', B = 'https://backend.leadconnectorhq.com/forms/' + ID;
  const f0 = await (await fetch(B, {headers: H})).json(); const f = f0.form || f0;
  const v = f.versionHistory && f.versionHistory[0];
  const data = (v && v.formDataDownloadUrl) ? await (await fetch(v.formDataDownloadUrl)).json() : f.formData;
  data.form.customStyle = css;
  const out = {};
  for (const m of ['PUT', 'PATCH']) {
    const r = await fetch(B, {method: m, headers: H, body: JSON.stringify({locationId: 'LOCATION_ID', name: f.name, formData: data})});
    out[m] = [r.status, (await r.text()).slice(0, 200)];
    if (r.ok) break;
  }
  return JSON.stringify(out);
})(''' + json.dumps(CSS) + ')'
print(Editor().js(JS))
