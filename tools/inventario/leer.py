"""SOLO LECTURA. Hace GET al backend de GHL desde la pestaña logueada (token de IndexedDB, nunca se imprime).
Uso: python leer.py <salida.json> <ruta1> [ruta2 ...]   (ruta relativa a https://backend.leadconnectorhq.com o URL completa)
Varias rutas -> guarda un dict {ruta: respuesta}. Imprime status y tamaño.
Solo GET: rechaza cualquier otro método.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, r"../ghl-api")
from cdp9333 import Pestana

JS = r"""(async (rutas) => {
  const db = await new Promise((ok, ko) => { const q = indexedDB.open('firebaseLocalStorageDb'); q.onsuccess = () => ok(q.result); q.onerror = () => ko(q.error); });
  const rows = await new Promise((ok, ko) => { const t = db.transaction('firebaseLocalStorage', 'readonly').objectStore('firebaseLocalStorage').getAll(); t.onsuccess = () => ok(t.result); t.onerror = () => ko(t.error); });
  const u = rows.map(r => r.value).find(v => v && v.stsTokenManager);
  const H = {'token-id': u.stsTokenManager.accessToken, 'channel': 'APP', 'source': 'WEB_USER', 'version': '2021-07-28'};
  const out = {};
  for (const r of rutas) {
    const url = r.startsWith('http') ? r : 'https://backend.leadconnectorhq.com' + r;
    try {
      const res = await fetch(url, {method: 'GET', headers: url.includes('leadconnectorhq.com') ? H : {}});
      const t = await res.text(); let j; try { j = JSON.parse(t); } catch (e) { j = t.slice(0, 200000); }
      out[r] = {status: res.status, data: j};
    } catch (e) { out[r] = {status: -1, error: String(e)}; }
  }
  return out;
})(%R%)"""

sal = Path(sys.argv[1]); rutas = sys.argv[2:]
p = Pestana()
r = p.js(JS.replace("%R%", json.dumps(rutas)))
sal.parent.mkdir(parents=True, exist_ok=True)
data = r if len(rutas) > 1 else r[rutas[0]]
sal.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
for k, v in r.items():
    print(v.get("status"), len(json.dumps(v.get("data", v.get("error")), ensure_ascii=False)), k[:160])
