"""Maneja la ventana VISIBLE de Chromium (puerto 9333) por CDP directo a la pestaña de Bizurai.

Uso (uv run -q --with websocket-client python cdp9333.py <orden> [arg]):
  estado            -> url y título de la pestaña de bizurai
  foto <archivo>    -> captura de pantalla de la pestaña
  ir <url>          -> navega la pestaña
  js <archivo.js>   -> evalúa el JS del archivo (con await) e imprime el resultado
Importable: from cdp9333 import Pestana
"""
import base64, itertools, json, sys, urllib.request
import websocket

PUERTO = 9333


def pestanas():
    return json.load(urllib.request.urlopen(f"http://127.0.0.1:{PUERTO}/json/list", timeout=10))


class Pestana:
    def __init__(self, filtro="bizurai"):
        cand = [t for t in pestanas() if t.get("type") == "page" and filtro in t.get("url", "")]
        if not cand:
            cand = [t for t in pestanas() if t.get("type") == "page"]
        self.info = cand[0]
        self.ws = websocket.create_connection(self.info["webSocketDebuggerUrl"], timeout=120,
                                              suppress_origin=True)
        self._ids = itertools.count(1)

    def cmd(self, method, **params):
        i = next(self._ids)
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
            raise RuntimeError(r["exceptionDetails"].get("exception", {}).get("description") or r["exceptionDetails"])
        return r.get("result", {}).get("value")

    def foto(self, ruta):
        d = self.cmd("Page.captureScreenshot", format="png")["data"]
        open(ruta, "wb").write(base64.b64decode(d))
        return ruta

    def ir(self, url):
        return self.cmd("Page.navigate", url=url)


if __name__ == "__main__":
    orden = sys.argv[1]
    p = Pestana()
    if orden == "estado":
        print(p.js("location.href"), "|", p.js("document.title"))
    elif orden == "foto":
        print(p.foto(sys.argv[2]))
    elif orden == "ir":
        print(p.ir(sys.argv[2]))
    elif orden == "js":
        print(json.dumps(p.js(open(sys.argv[2], encoding="utf-8").read()), ensure_ascii=False)[:4000])
