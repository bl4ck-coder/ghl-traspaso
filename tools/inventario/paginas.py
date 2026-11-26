"""SOLO LECTURA. Por cada sitio/funnel de _crudo/funnels-list.json guarda sitios/<id>.json y,
por cada página, paginas/<pageId>.json = {doc: GET /funnels/page/<id>, pageData: GET pageDataDownloadUrl}."""
import json, sys
from pathlib import Path
sys.path.insert(0, r"../ghl-api")
from cdp9333 import Pestana

INV = Path(__file__).resolve().parent.parent
LOC = "LOCATION_ID"
JS = r"""(async (ids) => {
  const db = await new Promise((ok, ko) => { const q = indexedDB.open('firebaseLocalStorageDb'); q.onsuccess = () => ok(q.result); q.onerror = () => ko(q.error); });
  const rows = await new Promise((ok, ko) => { const t = db.transaction('firebaseLocalStorage', 'readonly').objectStore('firebaseLocalStorage').getAll(); t.onsuccess = () => ok(t.result); t.onerror = () => ko(t.error); });
  const u = rows.map(r => r.value).find(v => v && v.stsTokenManager);
  const H = {'token-id': u.stsTokenManager.accessToken, 'channel': 'APP', 'source': 'WEB_USER', 'version': '2021-07-28'};
  const out = {};
  for (const id of ids) {
    try {
      const r = await fetch(`https://backend.leadconnectorhq.com/funnels/page/${id}?locationId=%LOC%`, {headers: H});
      const doc = await r.json(); let pd = null;
      if (doc.pageDataDownloadUrl) pd = await (await fetch(doc.pageDataDownloadUrl)).json();
      out[id] = {status: r.status, doc, pageData: pd};
    } catch (e) { out[id] = {error: String(e)}; }
  }
  return out;
})(%IDS%)"""

d = json.load(open(INV / "_crudo" / "funnels-list.json", encoding="utf-8"))
p = Pestana()
for k, v in d.items():
    if "funnel/list" not in k:
        continue
    for f in v["data"]["funnels"]:
        (INV / "sitios").mkdir(exist_ok=True)
        (INV / "sitios" / f"{f['_id']}.json").write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding="utf-8")
        ids = [pg for s in f["steps"] for pg in s.get("pages", [])]
        r = p.js(JS.replace("%LOC%", LOC).replace("%IDS%", json.dumps(ids)))
        for pid, res in r.items():
            (INV / "paginas" / f"{pid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
            pd = res.get("pageData") or {}
            print(f["name"][:30], pid, res.get("status"), "secciones", len(pd.get("sections", []) or []), res.get("error", ""))
