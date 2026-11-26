"""Clic en «Guardar» del editor (ventana visible) y registra el pedido de guardado que hace el editor."""
import json, time
from editor9333 import Editor
e = Editor()
GUARDADO = "(() => { const t = document.body.innerText; const i = t.search(/(guardado|saved)/i); return i < 0 ? '' : t.slice(Math.max(0, i - 20), i + 40); })()"
e.cmd("Network.enable")
antes = e.js(GUARDADO)
e.js("document.getElementById('pg-website-builder__btn--save').click(), true")
fin = time.time() + 60; vistos = []
e.ws.settimeout(5)
while time.time() < fin:
    try:
        m = json.loads(e.ws.recv())
    except Exception:
        continue
    if m.get("method") == "Network.requestWillBeSent":
        u = m["params"]["request"]["url"]
        if "autosave" in u or "/builder/" in u or "/funnels/page" in u:
            vistos.append(("req", m["params"]["request"]["method"], u[:120], len(m["params"]["request"].get("postData") or "")))
    if m.get("method") == "Network.responseReceived":
        u = m["params"]["response"]["url"]
        if "autosave" in u or "/builder/" in u:
            vistos.append(("resp", m["params"]["response"]["status"], u[:120]))
            if "autosave" in u:
                break
time.sleep(3)
despues = e.js(GUARDADO)
print("antes:", antes, "| despues:", despues)
for v in vistos: print(v)
