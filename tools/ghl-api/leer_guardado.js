(async () => {
  const db = await new Promise((ok, ko) => { const q = indexedDB.open('firebaseLocalStorageDb'); q.onsuccess = () => ok(q.result); q.onerror = () => ko(q.error); });
  const rows = await new Promise((ok, ko) => { const t = db.transaction('firebaseLocalStorage', 'readonly').objectStore('firebaseLocalStorage').getAll(); t.onsuccess = () => ok(t.result); t.onerror = () => ko(t.error); });
  const u = rows.map(r => r.value).find(v => v && v.stsTokenManager);
  const H = {'token-id': u.stsTokenManager.accessToken, 'channel': 'APP', 'source': 'WEB_USER', 'version': '2021-07-28'};
  const doc = await (await fetch('https://backend.leadconnectorhq.com/funnels/page/PAGE_ID?locationId=LOCATION_ID', {headers: H})).json();
  const pd = await (await fetch(doc.pageDataDownloadUrl)).json();
  return JSON.stringify({version: doc.pageVersion, pd});
})()
