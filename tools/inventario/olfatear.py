"""SOLO LECTURA. Navega la pestaña de Bizurai a una URL del panel y anota qué pedidos hace el front al backend.
Uso: python olfatear.py <nombre> <url> [segundos]
Guarda _red/<nombre>.json con método+url (sin cabeceras ni token) y una captura en capturas/<nombre>.png.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, r"../ghl-api")
from cdp9333 import Pestana

INV = Path(__file__).resolve().parent.parent
nombre, url = sys.argv[1], sys.argv[2]
seg = float(sys.argv[3]) if len(sys.argv) > 3 else 12
p = Pestana()
assert "location/LOCATION_ID" in url, "solo la subcuenta de ADICIO"
p.cmd("Network.enable")
p.ir(url)
fin = time.time() + seg
vistos = []
p.ws.settimeout(1)
while time.time() < fin:
    try:
        m = json.loads(p.ws.recv())
    except Exception:
        continue
    if m.get("method") == "Network.requestWillBeSent":
        r = m["params"]["request"]
        u = r["url"]
        if any(h in u for h in ("leadconnectorhq.com", "msgsndr", "bizurai.com/api")) and not u.endswith((".js", ".css", ".png", ".svg", ".woff2")):
            vistos.append({"m": r["method"], "u": u, "post": (r.get("postData") or "")[:300]})
try:
    p.cmd("Network.disable")
except Exception:
    pass
p.ws.settimeout(120)
(INV / "_red").mkdir(exist_ok=True)
(INV / "_red" / f"{nombre}.json").write_text(json.dumps(vistos, ensure_ascii=False, indent=1), encoding="utf-8")
p.foto(str(INV / "capturas" / f"{nombre}.png"))
print(p.js("location.href"), "|", p.js("document.title"))
seen = set()
for v in vistos:
    k = v["m"] + " " + v["u"].split("?")[0]
    if k in seen:
        continue
    seen.add(k)
    print(v["m"], v["u"][:230], ("POST:" + v["post"][:120]) if v["post"] else "")
