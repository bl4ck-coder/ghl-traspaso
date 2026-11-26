"""Sube ../datos/home-pagedata.json como BORRADOR de «ADICIO 2» (autosave del editor), desde la ventana visible.

Antes saca la pestaña del editor (para que el editor abierto no pise lo guardado), lee el token de
IndexedDB, pide la versión actual de la página y guarda. Después vuelve a abrir el editor y saca foto.
Uso: uv run -q --with websocket-client python subir.py [archivo-pagedata]
Nunca publica. Imprime solo códigos y conteos (no el token).
"""
import json, sys, time
from pathlib import Path
from cdp9333 import Pestana

H = Path(__file__).resolve().parent
LOC, FUNNEL, PAGE = "LOCATION_ID", "FUNNEL_ID", "PAGE_ID"
LISTA = f"https://app.bizurai.com/v2/location/{LOC}/funnels-websites/websites/{FUNNEL}/pages"
EDITOR = f"https://app.bizurai.com/location/{LOC}/page-builder/{PAGE}?source=website"
FOTO = r"ver9333.png"

archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else H.parent / "datos" / "home-pagedata.json"
pd = json.load(open(archivo, encoding="utf-8"))

p = Pestana()
if "page-builder" in (p.js("location.href") or ""):
    p.ir(LISTA)
    time.sleep(8)

JS = r"""(async (pd) => {
  const db = await new Promise((ok, ko) => { const q = indexedDB.open('firebaseLocalStorageDb'); q.onsuccess = () => ok(q.result); q.onerror = () => ko(q.error); });
  const rows = await new Promise((ok, ko) => { const t = db.transaction('firebaseLocalStorage', 'readonly').objectStore('firebaseLocalStorage').getAll(); t.onsuccess = () => ok(t.result); t.onerror = () => ko(t.error); });
  const u = rows.map(r => r.value).find(v => v && v.stsTokenManager);
  const tok = u.stsTokenManager.accessToken;
  const H = {'token-id': tok, 'channel': 'APP', 'source': 'WEB_USER', 'version': '2021-07-28', 'content-type': 'application/json'};
  const B = 'https://backend.leadconnectorhq.com';
  const doc = await (await fetch(`${B}/funnels/page/%PAGE%?locationId=%LOC%`, {headers: H})).json();
  const v = doc.pageVersion || (doc.page && doc.page.pageVersion) || 1;
  const hist = ((doc.page || doc).versionHistory || []).filter(x => x && x.schemaMarkupId);
  hist.sort((a, b) => String(b.updatedAt || '').localeCompare(String(a.updatedAt || '')));
  const schemaMarkupId = '%SCHEMA%' || (hist.length ? hist[0].schemaMarkupId : undefined);
  const body = {funnelId: '%FUNNEL%', pageData: pd, pageVersion: v + 1, pageType: 'draft', manualSave: true, ...(schemaMarkupId ? {schemaMarkupId} : {}),
    integrations: {videoBackground: false, blogMeta: {selectedBlogCategories: [], categoryNavigationList: []}, heading: 1, popup: false}};
  const r = await fetch(`${B}/funnels/builder/autosave/%PAGE%`, {method: 'POST', headers: H, body: JSON.stringify(body)});
  const t = await r.text();
  return {versionAntes: v, schemaMarkupId, status: r.status, respuesta: t.slice(0, 300), minToken: Math.round((u.stsTokenManager.expirationTime - Date.now()) / 60000)};
})(%PD%)"""
import os
expr = (JS.replace("%SCHEMA%", os.environ.get("SCHEMA_ID", "")).replace("%PAGE%", PAGE).replace("%LOC%", LOC).replace("%FUNNEL%", FUNNEL)
        .replace("%PD%", json.dumps(pd, ensure_ascii=False)))
r = p.js(expr)
print(json.dumps(r, ensure_ascii=False))
if r and r.get("status") in (200, 201):
    p.ir(EDITOR)
    time.sleep(25)
    print(p.foto(FOTO))
