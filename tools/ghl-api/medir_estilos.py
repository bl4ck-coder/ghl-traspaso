"""Mide el estilo calculado de cada elemento [data-ghl] de la home (importar.html, servida en 8831)
a 1920x950 y 390x844. Sale: ../datos/estilos-1920.json y ../datos/estilos-390.json.
Uso: uv run -q --with playwright python medir_estilos.py
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8831/importar.html"
OUT = Path(__file__).resolve().parent.parent / "datos"
JS = r"""() => {
  const P = ['color','backgroundColor','backgroundImage','fontFamily','fontSize','fontWeight','fontStyle',
    'lineHeight','letterSpacing','textTransform','textAlign','paddingTop','paddingRight','paddingBottom',
    'paddingLeft','borderTopLeftRadius','borderTopRightRadius','borderBottomLeftRadius','borderBottomRightRadius',
    'borderTopWidth','borderTopStyle','borderTopColor','boxShadow','backdropFilter','opacity','display','gap',
    'justifyContent','alignItems','maxWidth','objectFit','marginTop','marginBottom'];
  const out = [];
  for (const el of document.querySelectorAll('[data-ghl]')) {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    const o = {id: el.id, ghl: el.dataset.ghl, tag: el.tagName.toLowerCase(),
      cls: [...el.classList], x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height)};
    for (const p of P) o[p] = cs[p];
    const h = el.matches('h1,h2,h3,h4,h5,h6') ? el : el.querySelector('h1,h2,h3,h4,h5,h6');
    o.htag = h ? h.tagName.toLowerCase() : null;
    out.push(o);
  }
  return out;
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge")
    for w, h in ((1920, 950), (390, 844)):
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(1500)
        data = pg.evaluate(JS)
        (OUT / f"estilos-{w}.json").write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
        print(w, len(data), "elementos; alto pagina", pg.evaluate("document.documentElement.scrollHeight"))
        pg.close()
    b.close()
