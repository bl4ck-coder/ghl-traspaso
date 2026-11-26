"""Captura la vista previa de «ADICIO 2» y el original (8831) lado a lado. Uso: python vista.py [sufijo] [alto_max]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
O = Path(__file__).resolve().parent.parent / "capturas"; O.mkdir(exist_ok=True)
suf = sys.argv[1] if len(sys.argv) > 1 else "v"
hmax = int(sys.argv[2]) if len(sys.argv) > 2 else 2200
URLS = {"ghl": "https://sites.leadconnectorhq.com/preview/PAGE_ID", "orig": "http://127.0.0.1:8831/importar.html"}
with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge")
    for w, h in ((1920, 950), (390, 844)):
        shots = []
        for k, u in URLS.items():
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto(u, wait_until="networkidle", timeout=90000)
            pg.mouse.wheel(0, 400); pg.wait_for_timeout(2500); pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(800)
            f = O / f"{suf}-{k}-{w}.png"
            pg.screenshot(path=str(f), full_page=True)
            shots.append(Image.open(f).convert("RGB")); pg.close()
        hh = min(max(s.height for s in shots), hmax if w > 500 else hmax * 2)
        out = Image.new("RGB", (w * 2 + 20, hh), "white")
        for i, s in enumerate(shots):
            out.paste(s.crop((0, 0, w, min(s.height, hh))), (i * (w + 20), 0))
        if w > 500:
            out = out.resize((out.width // 2, out.height // 2))
        out.save(O / f"{suf}-par-{w}.jpg", quality=82)
        print(w, [s.size for s in shots], O / f"{suf}-par-{w}.jpg")
    b.close()
