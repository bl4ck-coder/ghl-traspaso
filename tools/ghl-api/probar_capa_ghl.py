"""Prueba capa-ghl.js en la vista previa SIN guardar nada: bloquea la capa vieja y carga la nueva.
Mide clases capa-* después de recorrer la página entera (con la hidratación de GHL) y saca capturas."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright

U = 'https://sites.leadconnectorhq.com/preview/PAGE_ID'
capa = Path(sys.argv[1]).read_text(encoding='utf-8') if len(sys.argv) > 1 else None
out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
J = r"""()=>{const c={};for(const n of document.querySelectorAll('*'))for(const k of n.classList||[])if(k.startsWith('capa-'))c[k]=(c[k]||0)+1;
return {c, est: JSON.stringify(window.__adicioCapa||null).slice(0,200)}}"""
with sync_playwright() as w:
    b = w.chromium.launch(channel='msedge')
    for ancho, alto in ((1920, 950), (412, 915)):
        p = b.new_page(viewport={'width': ancho, 'height': alto})
        errs = []; p.on('pageerror', lambda e: errs.append(str(e)[:200]))
        if capa:
            p.add_init_script("window.__adicioCapa={estado:'bloqueada'}")
        p.goto(U, wait_until='networkidle'); p.wait_for_timeout(1200)
        if capa:
            p.evaluate("delete window.__adicioCapa")
            p.add_script_tag(content=capa)
        p.wait_for_timeout(2500)
        h = p.evaluate('document.documentElement.scrollHeight')
        for y in range(0, h, 400):
            p.mouse.wheel(0, 400); p.wait_for_timeout(140)
        p.wait_for_timeout(2500)
        r = p.evaluate(J); r['errores'] = errs
        print(ancho, json.dumps(r, ensure_ascii=False))
        if out:
            out.mkdir(parents=True, exist_ok=True)
            for sel in ('.s-como', '.s-novedades', '.s-pie', '.s-equipo', '.s-faq'):
                el = p.query_selector(sel)
                if el:
                    el.scroll_into_view_if_needed(); p.wait_for_timeout(1800)
                    p.screenshot(path=str(out / f'{ancho}{sel.replace(".", "-")}.png'))
        p.close()
    b.close()
