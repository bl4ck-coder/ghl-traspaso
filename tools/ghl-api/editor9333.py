"""Opera el editor de GHL (iframe page-builder) de la ventana visible por CDP directo.

Uso (uv run -q --with websocket-client python editor9333.py <orden>):
  botones     -> lista botones de la barra de arriba (texto, title, aria-label, posición)
  guardar     -> hace clic en «Guardar» del editor y espera el aviso
  js <archivo.js> -> evalúa JS dentro del iframe del editor
"""
import itertools, json, sys, time, urllib.request
import websocket

PUERTO = 9333


def objetivo():
    ts = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PUERTO}/json/list", timeout=10))
    c = [t for t in ts if "page-builder.leadconnectorhq.com" in t.get("url", "")]
    if not c:
        raise SystemExit("no está abierto el editor (iframe page-builder)")
    return c[0]


class Editor:
    def __init__(self):
        self.t = objetivo()
        self.ws = websocket.create_connection(self.t["webSocketDebuggerUrl"], timeout=120, suppress_origin=True)
        self.ids = itertools.count(1)

    def cmd(self, method, **params):
        i = next(self.ids)
        self.ws.send(json.dumps({"id": i, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == i:
                if "error" in m:
                    raise RuntimeError(m["error"])
                return m.get("result", {})

    def js(self, expr):
        r = self.cmd("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        if r.get("exceptionDetails"):
            raise RuntimeError(str(r["exceptionDetails"])[:500])
        return r.get("result", {}).get("value")


BOTONES = r"""(() => [...document.querySelectorAll('button,[role=button],a')].map(b => {
  const r = b.getBoundingClientRect();
  return {t: (b.innerText||'').trim().slice(0,30), title: b.title||'', aria: b.getAttribute('aria-label')||'',
          id: b.id||'', cls: (b.className && b.className.baseVal === undefined ? b.className : '').toString().slice(0,60),
          x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width)};
}).filter(b => b.y >= 0 && b.y < 120 && b.w > 0))()"""

if __name__ == "__main__":
    e = Editor()
    orden = sys.argv[1]
    if orden == "botones":
        for b in e.js(BOTONES):
            print(b)
    elif orden == "js":
        print(json.dumps(e.js(open(sys.argv[2], encoding="utf-8").read()), ensure_ascii=False)[:4000])
