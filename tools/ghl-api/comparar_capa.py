"""Compara la capa de animación en el original (8831) y la vista previa de GHL: estado, disparadores y
qué clases anim-* reciben movimiento (estilo en línea de GSAP) al recorrer la página. No escribe nada."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

U = {'O': 'http://127.0.0.1:8831/', 'G': 'https://sites.leadconnectorhq.com/preview/PAGE_ID'}
JS = r"""() => {
  const st = window.ScrollTrigger ? ScrollTrigger.getAll() : [];
  const cls = {};
  for (const n of document.querySelectorAll('[class*="anim-"]')) {
    for (const c of n.classList) if (c.startsWith('anim-')) {
      cls[c] = cls[c] || [0, 0];
      cls[c][0]++;
      const s = n.getAttribute('style') || '';
      if (/transform|opacity|clip-path|translate|visibility/.test(s) || n.querySelector('[style*="transform"],svg path[style]')) cls[c][1]++;
    }
  }
  return {capa: window.__adicioCapa && window.__adicioCapa.estado, gsap: !!window.gsap, split: !!window.SplitText,
          triggers: st.length, html: document.documentElement.className.slice(0, 120),
          errores: window.__errs || [], cls};
}"""

out = {}
with sync_playwright() as w:
    b = w.chromium.launch(channel='msedge')
    for k, u in U.items():
        for ancho in (1920, 412):
            p = b.new_page(viewport={'width': ancho, 'height': 950 if ancho > 500 else 915})
            errs = []
            p.on('pageerror', lambda e: errs.append(str(e)[:160]))
            p.goto(u, wait_until='networkidle'); p.wait_for_timeout(3000)
            h = p.evaluate('document.documentElement.scrollHeight')
            for y in range(0, h, 500):
                p.mouse.wheel(0, 500); p.wait_for_timeout(90)
            p.wait_for_timeout(1500)
            r = p.evaluate(JS); r['pageerrors'] = errs
            out[f'{k}-{ancho}'] = r
            p.close()
    b.close()
Path(sys.argv[1]).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
for k, r in out.items():
    print(k, {x: r[x] for x in ('capa', 'gsap', 'split', 'triggers', 'pageerrors')})
o, g = out['O-1920']['cls'], out['G-1920']['cls']
for c in sorted(set(o) | set(g)):
    print(f'{c:22} orig {o.get(c)}  ghl {g.get(c)}')
