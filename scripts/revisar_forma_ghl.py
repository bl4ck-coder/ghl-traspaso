"""Revisa si una página nuestra tiene «forma GHL» antes de pasarla a Sitios (ruta B: esqueleto nativo + clases + islas).

Uso:
  uv run -q --with beautifulsoup4 python revisar_forma_ghl.py PAGINA.html [estilos.css ...] [--gate capa-activa] [--json salida.json]

Sale con código 1 si hay errores (cosas que GHL rompe o borra), 0 si solo hay avisos.
Reglas y por qué: references/forma-ghl.md (cada id R1..R12 está explicado ahí).
Los CSS se leen de los archivos pasados y de los <style> de la página.
"""
import argparse, json, re, sys
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup

BANDAS_GHL = {767, 768, 1024, 1025}
INLINE = {"span", "a", "strong", "em", "b", "i", "u", "mark", "small", "sup", "sub", "br", "code"}
TEXTO = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]


def reglas_css(css):
    """Devuelve (selector, cuerpo, media) de cada regla, sin comentarios."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, pila = [], 0, []
    tok = re.compile(r"([^{};]+)\{|\}")
    buf_media = []
    pos = 0
    while True:
        m = tok.search(css, pos)
        if not m:
            break
        if m.group(0) == "}":
            if pila:
                pila.pop()
            pos = m.end()
            continue
        sel = m.group(1).strip()
        if sel.startswith("@media") or sel.startswith("@supports") or sel.startswith("@layer") or sel.startswith("@container"):
            pila.append(sel)
            pos = m.end()
            continue
        if sel.startswith("@"):
            # @keyframes, @font-face: saltar el bloque entero
            prof, j = 1, m.end()
            while j < len(css) and prof:
                prof += css[j] == "{"
                prof -= css[j] == "}"
                j += 1
            pos = j
            continue
        fin = css.find("}", m.end())
        cuerpo = css[m.end():fin]
        media = " ".join(p for p in pila if p.startswith("@media"))
        out.append((sel, cuerpo, media))
        pos = fin + 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pagina")
    ap.add_argument("css", nargs="*")
    ap.add_argument("--gate", default="capa-activa|js-lista|is-ready",
                    help="regex de la clase que pone el JS cuando la capa arrancó (ocultar solo debajo de ella)")
    ap.add_argument("--json")
    a = ap.parse_args()

    html = Path(a.pagina).read_text(encoding="utf-8", errors="replace")
    sopa = BeautifulSoup(html, "html.parser")
    css = "\n".join(Path(c).read_text(encoding="utf-8", errors="replace") for c in a.css)
    css += "\n".join(s.get_text() for s in sopa.find_all("style"))
    reglas = reglas_css(css)
    gate = re.compile(a.gate)
    H = []  # (nivel, regla, mensaje, ejemplos)

    def hall(nivel, regla, msg, ej=None):
        H.append({"nivel": nivel, "regla": regla, "mensaje": msg, "ejemplos": (ej or [])[:5]})

    # R1 · marcas dentro del texto (TipTap las borra al editar)
    def es_texto(t):
        # un <li> que contiene bloques o imágenes es una tarjeta, no un texto
        return not (t.name == "li" and t.find(["p", "div", "img", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "figure", "svg"]))
    def dentro_de_texto(e):
        if e.name not in INLINE or not e.get_text(strip=True):
            return False  # un enlace que solo envuelve un ícono es un elemento imagen/botón en GHL
        t = e.find_parent(TEXTO)
        return bool(t) and es_texto(t)
    ej = []
    for d in sopa.find_all(True):
        attrs = [k for k in d.attrs if k in ("class", "id") or k.startswith("data-")]
        if attrs and dentro_de_texto(d):
            ej.append(f"<{d.find_parent(TEXTO).name}> › <{d.name} {' '.join(attrs)}>: {d.get_text(' ', strip=True)[:40]}")
    if ej:
        hall("error", "R1", f"{len(ej)} marcas (class/id/data-*) dentro de títulos o párrafos. El editor de texto de GHL las borra al editar; "
             "subí la clase al elemento o partí el texto con JS en vivo.", ej)

    # R2 · ganchos de animación en elementos en línea
    ej = [f"<{e.name} class='{' '.join(e.get('class'))}'>" for e in sopa.find_all(True)
          if any(c.startswith("anim-") for c in e.get("class", [])) and dentro_de_texto(e)]
    if ej:
        hall("error", "R2", f"{len(ej)} ganchos anim-* dentro del texto. En GHL la Custom Class va en el elemento (cae en .text-output).", ej)

    # R3 · anclas href="#..."
    anc = [x.get("href") for x in sopa.find_all("a", href=True) if x["href"].startswith("#") and len(x["href"]) > 1]
    if anc:
        hall("aviso", "R3", f"{len(anc)} enlaces a anclas. En GHL son la acción «scroll-to-element» con el id de la sección: anotalos en el manifiesto.",
             sorted(set(anc)))

    # R4 · grid y superposiciones
    grid = [s for s, c, m in reglas if re.search(r"display\s*:\s*(inline-)?grid", c)]
    span = [s for s, c, m in reglas if re.search(r"grid-(column|row|area)\s*:|grid-template-areas", c)]
    if grid:
        hall("aviso", "R4", f"{len(grid)} reglas con display:grid ({len(span)} con celdas que abarcan). GHL solo tiene filas y columnas en %: "
             "rediseñalo como fila/columnas o marcá ese bloque como isla de código.", grid[:5] + span[:3])
    absol = [s for s, c, m in reglas if re.search(r"position\s*:\s*absolute", c) and not re.search(r"::?(before|after)", s)]
    if absol:
        hall("aviso", "R4", f"{len(absol)} reglas con position:absolute sobre elementos (no pseudo). Superposiciones: sin campo en GHL, van por clase en CSS global.", absol)

    # R5 · cortes de ancho
    anchos = Counter(int(n) for _, _, m in reglas for n in re.findall(r"(\d{3,4})px", m))
    raros = sorted(w for w in anchos if w not in BANDAS_GHL)
    if raros:
        hall("aviso", "R5", f"{len(anchos)} cortes de ancho distintos; GHL tiene 3 franjas (≤767, 768–1024, ≥1025). "
             f"Fuera de esas: {raros}. Lo editable sigue esas 3; el resto solo en CSS global por clase.", [str(w) for w in raros])
    nclamp = len(re.findall(r"clamp\(", css))
    if nclamp:
        hall("info", "R5", f"{nclamp} clamp() en el CSS. Un tamaño de letra editable en GHL son 2 números fijos (escritorio y celular).")

    # R6 · etiquetas que GHL no tiene
    sem = Counter(e.name for e in sopa.find_all(["details", "summary", "table", "address", "dl", "figure", "blockquote"]))
    if sem:
        hall("aviso", "R6", "Etiquetas sin elemento nativo (GHL publica todo como div): "
             + ", ".join(f"{k}×{v}" for k, v in sem.items()) + ". FAQ → elemento FAQ nativo; cita → párrafo con clase.", list(sem))

    # R7 · imágenes que una captura deja en blanco
    vagas = [i.get("src", "")[-50:] for i in sopa.find_all("img") if i.get("loading") == "lazy" or i.get("decoding") == "async"]
    if vagas:
        hall("error", "R7", f"{len(vagas)} imágenes con loading=lazy o decoding=async: una captura sin scroll las deja en blanco (import por imagen o por visión).", vagas)
    sinalt = [i.get("src", "")[-50:] for i in sopa.find_all("img") if i.get("alt") is None]
    if sinalt:
        hall("aviso", "R7", f"{len(sinalt)} imágenes sin atributo alt.", sinalt)
    deco = [i for i in sopa.find_all("img") if i.get("alt") is not None and not i["alt"].strip()]
    if deco:
        hall("info", "R7", f"{len(deco)} imágenes decorativas (alt vacío): en GHL dejá su alt vacío también.")

    # R8 · títulos
    hs = [int(h.name[1]) for h in sopa.find_all(re.compile(r"^h[1-6]$"))]
    if hs.count(1) != 1:
        hall("error", "R8", f"La página tiene {hs.count(1)} H1 (tiene que ser exactamente 1).")
    saltos = [f"H{x}→H{y}" for x, y in zip(hs, hs[1:]) if y > x + 1]
    if saltos:
        hall("aviso", "R8", f"{len(saltos)} saltos de nivel de título.", saltos)

    # R9 · CSS atado a ids
    porid = [s for s, c, m in reglas if re.search(r"#[A-Za-z][\w-]*", s)]
    if porid:
        hall("aviso", "R9", f"{len(porid)} reglas por id. Los ids nuestros no llegan a GHL y los de GHL cambian al duplicar: "
             "la clase es el ancla principal; el id de GHL solo como respaldo generado después de crear la página.", porid)

    # R10 · contenido oculto sin JS (falla segura)
    oculto = [s for s, c, m in reglas if re.search(r"opacity\s*:\s*0(?![.\d])|visibility\s*:\s*hidden", c)
              and not gate.search(s) and not re.search(r"::?(before|after)|:hover|:focus|\[hidden\]|sr-only|visually-hidden", s)]
    if oculto:
        hall("aviso", "R10", f"{len(oculto)} reglas ocultan contenido sin depender de la clase que pone el JS ({a.gate}). "
             "Si el JS no corre (Optimizar JS, falla), eso queda invisible.", oculto)

    # R11 · texto dentro de imágenes de fondo con contenido
    bg = [s for s, c, m in reglas if re.search(r"background(-image)?\s*:[^;]*url\(", c)]
    if bg:
        hall("info", "R11", f"{len(bg)} fondos con url(): si llevan texto, ese texto no se puede editar ni lo lee Google.", bg)

    # R12 · scripts de la página
    scr = [s.get("src") or "(en línea)" for s in sopa.find_all("script") if (s.get("type") or "") not in ("application/ld+json",)]
    if scr:
        hall("info", "R12", f"{len(scr)} scripts en la página. En GHL van en el código del sitio (Body), arrancan con hydrationDone y no pueden ser necesarios para ver el contenido.", scr)
    ld = sopa.find_all("script", type="application/ld+json")
    if ld:
        hall("info", "R12", f"{len(ld)} bloques JSON-LD: en GHL van al campo schemaMarkup de la página, no al código.")

    orden = {"error": 0, "aviso": 1, "info": 2}
    H.sort(key=lambda h: (orden[h["nivel"]], h["regla"]))
    cuenta = Counter(h["nivel"] for h in H)
    print(f"{a.pagina}\n  errores {cuenta['error']} · avisos {cuenta['aviso']} · info {cuenta['info']}")
    for h in H:
        print(f"  [{h['nivel']}] {h['regla']} {h['mensaje']}")
        for e in h["ejemplos"]:
            print(f"        · {e}")
    if a.json:
        Path(a.json).write_text(json.dumps({"pagina": a.pagina, "hallazgos": H}, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(1 if cuenta["error"] else 0)


if __name__ == "__main__":
    main()
