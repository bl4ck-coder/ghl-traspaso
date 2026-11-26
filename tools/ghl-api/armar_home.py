"""Arma el pageData nativo de GHL de la home de ADICIO a partir de W31/sitio/importar.html.

Entrada: importar.html (árbol data-ghl), ../datos/estilos-1920.json y estilos-390.json (medidos con
medir_estilos.py) y herr/plantillas-reales.json (elementos reales de la home publicada de ADICIO).
Salida: ../datos/home-pagedata.json + ../datos/home-mapa.json (nuestro id -> id GHL).

Uso: uv run -q --with beautifulsoup4 python armar_home.py [seccion ...]   (sin args: todas)
Notas:
- Texto y H exactos del archivo; dentro del texto solo quedan a/strong/em/u/br (TipTap borra el resto).
- Cada elemento lleva sus clases nuestras en Custom Class (extra.customClass), nunca dentro del texto.
- Imágenes: por ahora desde https://adicio-ghl-prueba.vercel.app/media/ (falta subirlas a Medios).
- sectionStyles se deja vacío: lo regenera el editor al guardar (se prueba en vivo).
"""
import copy, json, random, re, string, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

H = Path(__file__).resolve().parent
W31 = H.parents[1] / "31-adicio-home-ghl" / "sitio"
DAT = H.parent / "datos"
MEDIA = "https://adicio-ghl-prueba.vercel.app/media/"
LOC, FUNNEL, PAGE = "LOCATION_ID", "FUNNEL_ID", "PAGE_ID"

T = json.load(open(H / "plantillas-reales.json", encoding="utf-8"))
E19 = {o["id"]: o for o in json.load(open(DAT / "estilos-1920.json", encoding="utf-8"))}
E39 = {o["id"]: o for o in json.load(open(DAT / "estilos-390.json", encoding="utf-8"))}
soup = BeautifulSoup(open(W31 / "importar.html", encoding="utf-8").read(), "html.parser")

# --------------------------------------------------------------- utilidades
def rid(prefix):
    return prefix + "-" + "".join(random.choices(string.ascii_letters + string.digits, k=10))

def px(v):
    try:
        return round(float(str(v).replace("px", "")), 1)
    except ValueError:
        return 0

def hexcol(c):
    m = re.match(r"rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)", c or "")
    if not m:
        return c or "transparent"
    r, g, b = (int(float(x)) for x in m.groups()[:3])
    a = m.group(4)
    if a is not None and float(a) == 0:
        return "transparent"
    if a is not None and float(a) < 1:
        return f"rgba({r}, {g}, {b}, {a})"
    return f"#{r:02X}{g:02X}{b:02X}"

FUENTES = {"Bricolage Grotesque": "var(--bricolage-grotesque)", "Figtree": "var(--figtree)"}

def fam(f):
    """Fuente como la guarda GHL: var(--nombre) (el editor solo carga fuentes referidas así)."""
    n = (f or "").split(",")[0].strip().strip('"').strip("'") or "Figtree"
    return FUENTES.get(n, "var(--figtree)")

def V(v, unit=None):
    return {"value": v, "unit": unit} if unit else {"value": v}

def radius(o):
    vals = [o.get(k, "0px") for k in ("borderTopLeftRadius", "borderTopRightRadius",
                                       "borderBottomRightRadius", "borderBottomLeftRadius")]
    vals = [f"{min(px(v), 999):g}px" for v in vals]
    return vals[0] if len(set(vals)) == 1 else " ".join(vals)

def base(tname, prefix):
    e = copy.deepcopy(T[tname])
    i = rid(prefix)
    e["id"] = i
    if isinstance(e.get("extra"), dict) and "nodeId" in e["extra"]:
        e["extra"]["nodeId"] = "c" + i
    for k in ("mobileStyles", "mobileWrapper", "tabletStyles", "tabletWrapper"):
        if k in e:
            e[k] = {}
    if "customCss" in e:
        e["customCss"] = []
    e["child"] = []
    ex = e.get("extra")
    if isinstance(ex, dict):
        if "visibility" in ex:
            ex["visibility"] = V({"hideDesktop": False, "hideTablet": False, "hideMobile": False})
        if "customClass" in ex:
            ex["customClass"] = V([])
    return e

def set_class(e, node, extra=()):
    cls = [c for c in (node.get("class") or []) if c] + list(extra)
    target = e["metaData"]["extra"] if "metaData" in e else e.get("extra")
    if isinstance(target, dict) and cls:
        target["customClass"] = V(cls)

ALLOWED = {"a", "strong", "b", "em", "i", "u", "br", "s"}

def clean_inline(node):
    """HTML del contenido de un nodo con solo las marcas que TipTap conserva."""
    out = []
    for c in node.children:
        if isinstance(c, NavigableString):
            out.append(str(c).replace("<", "&lt;"))
        elif isinstance(c, Tag):
            if c.name == "img":
                continue
            inner = clean_inline(c)
            if c.name == "a":
                href = c.get("href", "")
                ext = href.startswith("http")
                attrs = f' href="{href}"' + (' target="_blank" rel="noopener noreferrer"' if ext else "")
                out.append(f"<a{attrs}>{inner}</a>")
            elif c.name == "br":
                out.append("<br>")
            elif c.name in ALLOWED:
                t = {"b": "strong", "i": "em"}.get(c.name, c.name)
                out.append(f"<{t}>{inner}</{t}>")
            else:
                out.append(inner)
    return re.sub(r"\s+", " ", "".join(out)).strip()

def text_styles(e, o, o3, tag_family_default):
    st = e["styles"]
    fs = px(o["fontSize"]) or 18
    st["color"] = V(hexcol(o["color"]))
    st["fontFamily"] = V(fam(o["fontFamily"]))
    w = str(o["fontWeight"])
    st["fontWeight"] = {"value": "normal", "desktop": w}
    lh = px(o["lineHeight"])
    st["lineHeight"] = V(round(lh / fs, 2) if lh else 1.3, "em")
    st["letterSpacing"] = V(f"{px(o['letterSpacing']):g}", "px")
    st["textTransform"] = V(o["textTransform"] if o["textTransform"] in ("uppercase", "lowercase", "capitalize") else "none")
    st["textAlign"] = V(o["textAlign"] if o["textAlign"] in ("left", "center", "right") else "left")
    for side in ("Top", "Right", "Bottom", "Left"):
        st["padding" + side] = V(px(o["padding" + side]), "px")
    if "fontStyle" in o and o["fontStyle"] == "italic":
        st["fontStyle"] = V("italic")
    e["extra"]["desktopFontSize"] = V(fs, "px")
    e["extra"]["mobileFontSize"] = V(px(o3["fontSize"]) if o3 else fs, "px")
    if "typography" in e["extra"]:
        e["extra"]["typography"] = V(fam(o["fontFamily"]))
    for k in ("boldTextColor", "italicTextColor", "underlineTextColor", "linkTextColor", "iconColor"):
        if k in st:
            st[k] = V(hexcol(o["color"]))
    if o3 and o3["textAlign"] != o["textAlign"] and o3["textAlign"] in ("left", "center", "right"):
        e["mobileStyles"]["textAlign"] = V(o3["textAlign"])

def box_styles(st, o):
    """Fondo, borde redondeado, sombra y relleno de una sección / fila / columna."""
    bg = hexcol(o["backgroundColor"])
    st["backgroundColor"] = V(bg if bg != "transparent" else "var(--transparent)")
    bi = o.get("backgroundImage") or "none"
    st["background"] = V(bi if "gradient" in bi else "none")
    st["borderRadius"] = V(radius(o))
    st["boxShadow"] = V(o.get("boxShadow") or "none")
    if "backdropFilter" in st:
        st["backdropFilter"] = V(o.get("backdropFilter") or "none")
    bw = px(o.get("borderTopWidth"))
    if bw and o.get("borderTopStyle") not in (None, "none"):
        st["borderWidth"] = V(f"{bw:g}px"); st["borderStyle"] = V(o["borderTopStyle"])
        st["borderColor"] = V(hexcol(o["borderTopColor"]))
    for side in ("Top", "Right", "Bottom", "Left"):
        st["padding" + side] = V(px(o["padding" + side]), "px")

def bg_url(o):
    m = re.search(r'url\("?([^")]+)"?\)', o.get("backgroundImage") or "")
    if not m:
        return ""
    return MEDIA + m.group(1).split("/media/")[-1]

# --------------------------------------------------------------- árbol
def kids(n):
    out = []
    for c in n.find_all(recursive=False):
        if c.get("data-ghl"):
            out.append(c)
        else:
            out += kids(c)
    return out

MAPA = {}         # nuestro id -> id GHL
ANCLAS = []       # (elemento GHL, href) para resolver al final
FLAT = []         # elementos de la sección en curso

def leaf(node):
    g = node["data-ghl"]
    o, o3 = E19.get(node.get("id"), {}), E39.get(node.get("id"), {})
    if not o:
        return None
    if g == "headline" or (g == "faq" and node.name != "div"):
        tag = node.name if node.name in ("h1", "h2", "h3", "h4", "h5", "h6") else "h2"
        e = base("c-heading", "heading")
        e["tag"] = tag
        e["extra"]["text"] = V(f"<{tag}>{clean_inline(node)}</{tag}>")
        text_styles(e, o, o3, "Bricolage Grotesque")
    elif g == "paragraph" or (g == "list" and not node.find(attrs={"data-ghl": "column"})):
        e = base("c-paragraph", "paragraph")
        if node.name in ("ul", "ol"):
            lis = "".join(f"<li><p>{clean_inline(li)}</p></li>" for li in node.find_all("li", recursive=False))
            e["extra"]["text"] = V(f"<{node.name}>{lis}</{node.name}>")
        else:
            e["extra"]["text"] = V(f"<p>{clean_inline(node)}</p>")
        text_styles(e, o, o3, "Figtree")
    elif g == "button":
        e = base("c-button", "button")
        e["extra"]["nodeId"] = "c" + e["id"]
        txt = node.get_text(" ", strip=True) or node.get("aria-label") or node.get("title") or ""
        if not txt:
            img = node.find("img")
            txt = (img.get("alt") if img else "") or node.get("href", "").split("/")[2] if "//" in node.get("href", "") else "Enlace"
        e["extra"]["text"] = V(txt)
        href = node.get("href", "")
        if href.startswith("#"):
            e["extra"]["action"] = V("scroll-to-element")
            ANCLAS.append((e, href[1:]))
        elif href.startswith("tel:"):
            e["extra"]["action"] = V("call"); e["extra"]["phoneNumber"] = V(href[4:])
        elif href.startswith("mailto:"):
            e["extra"]["action"] = V("email"); e["extra"]["emailAddress"] = V(href[7:])
        else:
            e["extra"]["action"] = V("url")
            e["extra"]["visitWebsite"] = V({"url": href, "newTab": href.startswith("http")})
            e["extra"]["link"] = V(href)
        st = e["styles"]
        st["backgroundColor"] = V(hexcol(o["backgroundColor"]))
        st["color"] = V(hexcol(o["color"]))
        for k in ("boldTextColor", "italicTextColor", "underlineTextColor", "iconColor"):
            st[k] = V(hexcol(o["color"]))
        st["typography"] = V(fam(o["fontFamily"]))
        e["extra"]["typography"] = V(fam(o["fontFamily"]))
        st["fontWeight"] = V(str(o["fontWeight"]))
        st["fontSize"] = V(px(o["fontSize"]), "px")
        e["extra"]["desktopFontSize"] = V(px(o["fontSize"]), "px")
        e["extra"]["mobileFontSize"] = V(px(o3.get("fontSize")) or px(o["fontSize"]), "px")
        h = px(o["h"]) if "h" in o else 0
        fs = px(o["fontSize"])
        vp = max(0, round((o["h"] - fs * 1.2) / 2)) if o.get("h") else 14
        st["paddingTop"] = V(vp, "px"); st["paddingBottom"] = V(vp, "px")
        st["paddingLeft"] = V(px(o["paddingLeft"]), "px"); st["paddingRight"] = V(px(o["paddingRight"]), "px")
        st["borderRadius"] = V(min(px(o["borderTopLeftRadius"]), 999), "px")
        bw = px(o.get("borderTopWidth"))
        st["borderWidth"] = V(bw, "px"); st["borderStyle"] = V(o.get("borderTopStyle") if bw else "none")
        st["borderColor"] = V(hexcol(o.get("borderTopColor")))
        st["letterSpacing"] = V(px(o["letterSpacing"]), "px")
        st["textTransform"] = V(o["textTransform"] if o["textTransform"] != "none" else "none")
        st["boxShadow"] = V(o.get("boxShadow") or "none")
        e["wrapper"]["textAlign"] = V("left")
        e["mobileStyles"] = {k: copy.deepcopy(st[k]) for k in ("paddingTop", "paddingBottom", "paddingLeft", "paddingRight")}
    elif g == "image":
        e = base("c-image", "image")
        src = node.get("src", "")
        url = src if src.startswith("http") else MEDIA + src.split("media/")[-1]
        ip = e["extra"]["imageProperties"]["value"]
        ip.update({"url": url, "altText": node.get("alt", ""), "compression": False})
        st = e["styles"]
        st["width"] = V(round(o["w"]), "px")
        st["height"] = V("auto")
        st["borderRadius"] = V(radius(o))
        st["textAlign"] = V("left")
        st["boxShadow"] = V(o.get("boxShadow") or "none")
        if o3:
            e["mobileStyles"]["width"] = V(round(o3["w"]), "px")
    elif g == "faq":
        e = base("c-faq", "faq")
        items, i = [], 0
        for h3 in node.find_all(attrs={"data-ghl": "faq"}):
            if h3 is node:
                continue
            p = h3.find_next(attrs={"data-ghl": "paragraph"})
            i += 1
            items.append({"id": i, "heading": f"<h3>{clean_inline(h3)}</h3>", "text": f"<p>{clean_inline(p)}</p>",
                          "showImage": False, "image": "", "active": i == 1, "compression": True})
        e["extra"]["faqList"] = V(items)
    elif g == "nav":
        e = base("c-nav-menu-v2", "nav-menu")
        items = []
        for k, a in enumerate(node.find_all("a"), 1):
            href = a.get("href", "")
            if href.startswith("#"):
                href = "#" + ("section-" + href[1:] if href[1:] not in ("cobertura",) else "col-cobertura")
            items.append({"id": str(k), "title": a.get_text(" ", strip=True), "openInNewTab": False, "goTo": "url",
                          "url": href, "goToId": "", "megaMenu": False, "childs": [], "edit": False})
        e["extra"]["menuItems"] = V(items)
        e["extra"]["includeLogoInMenu"] = V(False)
        e["extra"]["text"] = V("")
        e["extra"]["typography"] = V("var(--figtree)")
        a0 = node.find("a"); oa = E19.get(a0.get("id") or "", {}) if a0 else {}
        e["extra"]["desktopFontSize"] = V(16, "px"); e["extra"]["mobileFontSize"] = V(18, "px")
        st = e["styles"]
        for k in ("color", "boldTextColor", "italicTextColor", "underlineTextColor", "iconColor", "submenuColor"):
            if k in st:
                st[k] = V("#14212E")
        for k in ("hoverTextColor",):
            if k in st:
                st[k] = V("#005EB8")
        for k in ("backgroundColor", "mobileBackgroundColor", "hoverBackgroundColor"):
            if k in st:
                st[k] = V("transparent")
        if "fontWeight" in st:
            st["fontWeight"] = V("600")
        if "mobilePopupBackgroundColor" in st:
            st["mobilePopupBackgroundColor"] = V("#FFFFFF")
        st["typography"] = V("var(--figtree)"); st["fontSize"] = V(16, "px")
        st["itemBorderStyle"] = V("none"); st["itemBorderWidth"] = V(0, "px")
        st["navMenuAlign"] = V("center"); st["navMenuItemSpacingX"] = V(8, "px")
        st["inlineColors"] = V(["#14212E"]); st["linkTextColor"] = V("#14212E")
    elif g == "form":
        e = base("c-form", "form")
    else:
        return None
    MAPA[node.get("id") or f"_{len(MAPA)}"] = e["id"]
    set_class(e, node)
    return e

def column(node, items, o, width_pct=100, margin=(0, 0), nested=False):
    c = base("c-column", "col")
    if node is not None and node.get("id") == "cobertura":
        c["id"] = "col-cobertura"
    st = c["styles"]
    if o:
        box_styles(st, o)
        url = bg_url(o)
        if url:
            c["extra"]["bgImage"] = V({"mediaType": "image", "url": url, "opacity": "1", "options": "bgCover",
                                       "svgCode": "", "videoUrl": "", "videoThumbnail": "", "videoLoop": True})
    else:
        for side in ("Top", "Right", "Bottom", "Left"):
            st["padding" + side] = V(0, "px")
    st["width"] = V(round(width_pct, 2), "%")
    c["wrapper"]["marginLeft"] = V(margin[0], "px"); c["wrapper"]["marginRight"] = V(margin[1], "px")
    c["mobileWrapper"] = {"marginLeft": V(0, "px"), "marginRight": V(0, "px")}
    c["extra"]["columnLayout"] = V("column")
    c["extra"]["justifyContentColumnLayout"] = V("flex-start")
    if nested:
        c["class"]["nestedColumn"] = V("c-nested-column")
    if node is not None:
        set_class(c, node)
        if node.get("id"):
            MAPA[node["id"]] = c["id"]
    c["child"] = [x["id"] for x in items]
    return c

def stack_margins(parent_o, items_nodes):
    """marginTop de cada hijo apilado = distancia vertical medida al anterior."""
    prev_bottom = None
    for el, nd in items_nodes:
        o = E19.get(nd.get("id") or "", {})
        if not o or el is None:
            continue
        top = o["y"]
        if prev_bottom is None and parent_o:
            gap = top - (parent_o["y"] + px(parent_o.get("paddingTop")))
        else:
            gap = top - prev_bottom if prev_bottom is not None else 0
        gap = max(0, round(gap))
        tgt = el.get("wrapper") if "wrapper" in el else None
        if tgt is not None and gap:
            tgt["marginTop"] = V(gap, "px")
        prev_bottom = o["y"] + o["h"]

def build_column(node, width_pct=100, margin=(0, 0)):
    """Columna GHL a partir de un nodo column (o de cualquier nodo que haga de columna)."""
    o = E19.get(node.get("id") or "", {})
    children, pairs, nested = [], [], False
    loose = []
    def flush_loose():
        if loose:
            r = build_row(None, list(loose), forced_o=None)
            children.append(r); pairs.append((r, loose[0])); loose.clear()
    for k in kids(node):
        g = k["data-ghl"]
        if g == "row" or (g == "list" and k.find(attrs={"data-ghl": "column"})):
            r = build_row(k)
            nested = True
            children.append(r); pairs.append((r, k))
        elif g == "column":
            # columna dentro de columna -> fila de una columna
            r = build_row(None, [k])
            nested = True
            children.append(r); pairs.append((r, k))
        elif g == "form":
            # el formulario nativo; su botón lo trae GHL
            e = leaf(k)
            if e:
                FLAT.append(e); children.append(e); pairs.append((e, k))
        else:
            e = leaf(k)
            if e:
                FLAT.append(e); children.append(e); pairs.append((e, k))
    stack_margins(o, pairs)
    c = column(node, children, o, width_pct, margin, nested)
    FLAT.append(c)
    return c

def build_row(node, cols_nodes=None, forced_o=None):
    """Fila GHL. node = nodo fila (o None para una fila sintética con cols_nodes)."""
    r = base("c-row", "row")
    st = r["styles"]
    o = E19.get(node.get("id"), {}) if node is not None else {}
    for side in ("Top", "Right", "Bottom", "Left"):
        st["padding" + side] = V(0, "px")
    if o:
        bg = hexcol(o["backgroundColor"])
        st["backgroundColor"] = V(bg if bg != "transparent" else "var(--transparent)")
        bi = o.get("backgroundImage") or "none"
        st["background"] = V(bi if "gradient" in bi else "none")
        st["borderRadius"] = V(radius(o)); st["boxShadow"] = V(o.get("boxShadow") or "none")
        if "backdropFilter" in st:
            st["backdropFilter"] = V(o.get("backdropFilter") or "none")
        # relleno propio de la fila salvo el lateral de página (64px), que pone la sección (1170)
        st["paddingTop"] = V(px(o["paddingTop"]), "px"); st["paddingBottom"] = V(px(o["paddingBottom"]), "px")
        if bg != "transparent" or "gradient" in bi:
            st["paddingLeft"] = V(px(o["paddingLeft"]), "px"); st["paddingRight"] = V(px(o["paddingRight"]), "px")
        set_class(r, node)
        MAPA[node.get("id")] = r["id"]
    r["wrapper"]["marginRight"] = V(0, "px")
    r["extra"]["rowWidth"] = V(100, "%")
    members = cols_nodes if cols_nodes is not None else kids(node)
    if not members:
        return None
    # ancho útil de la fila y separación entre columnas medidos
    boxes = [E19.get(m.get("id") or "", {}) for m in members]
    if o:
        inner = o["w"] - px(o["paddingLeft"]) - px(o["paddingRight"])
    else:
        xs = [b for b in boxes if b]
        inner = (max(b["x"] + b["w"] for b in xs) - min(b["x"] for b in xs)) if xs else 1152
    same_line = []
    if boxes and all(boxes):
        y0 = boxes[0]["y"]
        same_line = [b for b in boxes if abs(b["y"] - y0) < 30]
    gap = px(o.get("gap")) if o and o.get("gap") not in (None, "normal") else 0
    if len(same_line) > 1 and not gap:
        s = sorted(same_line, key=lambda b: b["x"])
        gap = max(0, round(min(s[i + 1]["x"] - (s[i]["x"] + s[i]["w"]) for i in range(len(s) - 1))))
    cols = []
    for m, b in zip(members, boxes):
        multi = len(same_line) > 1
        pct = (b["w"] / inner * 100) if (b and inner and multi) else 100
        if multi:
            pct = max(5, pct - 0.4)
        mg = (round(gap / 2), round(gap / 2)) if multi else (0, 0)
        if m.get("data-ghl") == "column":
            c = build_column(m, pct, mg)
        else:
            # elemento suelto en la fila (botón, imagen, párrafo): su propia columna
            e = leaf(m)
            if e is None:
                continue
            FLAT.append(e)
            c = column(None, [e], {}, pct, mg)
            FLAT.append(c)
        cols.append(c)
    r["child"] = [c["id"] for c in cols]
    FLAT.append(r)
    return r

def build_section(node, seq):
    global FLAT
    FLAT = []
    o, o3 = E19.get(node.get("id"), {}), E39.get(node.get("id"), {})
    s = base("section", "section")
    sid = "section-" + (node.get("id") if node.get("id") and not re.match(r"a\d+$", node["id"]) else
                        {"a001": "cabecera", "a192": "pie"}.get(node.get("id"), rid("x")[2:]))
    s["id"] = sid
    md = s["metaData"]
    md["id"] = sid
    md.pop("_id", None); md.pop("prebuiltSectionTemplate", None)
    md["extra"]["elementScreenshot"] = V([])
    st = md["styles"]
    box_styles(st, o)
    st["paddingLeft"] = V(0, "%"); st["paddingRight"] = V(0, "%")
    md["mobileStyles"] = {"paddingTop": V(px(o3.get("paddingTop", 0)), "px"),
                          "paddingBottom": V(px(o3.get("paddingBottom", 0)), "px")}
    md["extra"]["bgImage"] = V({"mediaType": "image", "url": bg_url(o), "opacity": "1", "options": "full-center",
                                "svgCode": "", "videoUrl": "", "videoThumbnail": "", "videoLoop": True,
                                "showSvgToggle": False})
    md["extra"]["allowRowMaxWidth"] = V(False)   # False = contenido a 1170 px (medido en la home real)
    set_class(s, node)
    MAPA[node.get("id")] = sid
    rows, pairs, loose = [], [], []
    for k in kids(node):
        g = k["data-ghl"]
        if g == "row":
            r = build_row(k)
        elif g == "column":
            r = build_row(None, [k])
        else:
            r = build_row(None, [k])
        if r:
            rows.append(r); pairs.append((r, k))
    stack_margins(o, pairs)
    md["child"] = [r["id"] for r in rows]
    # orden pre-orden (padre antes que hijos), como espera el render
    byid = {e["id"]: e for e in FLAT}
    ordered = []
    def walk(ids):
        for i in ids:
            e = byid.get(i)
            if e is not None:
                ordered.append(e); walk(e.get("child", []))
    walk(md["child"])
    s["elements"] = ordered
    s["sequence"] = seq
    s["pageId"], s["funnelId"], s["locationId"] = PAGE, FUNNEL, LOC
    s["general"] = {"colors": [], "fontsForPreview": [], "rootVars": {}, "sectionStyles": "", "customFonts": []}
    return s

def main(only):
    secs = [n for n in soup.body.find_all(attrs={"data-ghl": "section"}) if n.find_parent(attrs={"data-ghl": "section"}) is None]
    if only:
        secs = [n for n in secs if n.get("id") in only]
    sections = [build_section(n, i) for i, n in enumerate(secs)]
    for e, target in ANCLAS:
        gid = MAPA.get(target) or ("section-" + target)
        e["extra"]["scrollToElement"] = V(gid if gid.startswith(("section-", "col-")) else gid)
    env = json.load(open(H / "templates.json", encoding="utf-8"))["envelope"]
    pd = copy.deepcopy(env)
    pd["sections"] = sections
    pd["popups"] = []; pd["popupsList"] = []
    pd["fontsForPreview"] = ["'Bricolage Grotesque'", "'Figtree'"]
    g = pd["general"]["general"]
    g["fontsToLoad"] = ["Bricolage Grotesque", "Figtree", "Inter"]; g["fontsToLoadForPreview"] = ["Bricolage Grotesque", "Figtree"]
    ty = pd.setdefault("settings", {}).setdefault("settings", {}).setdefault("typography", {}).setdefault("fonts", {})
    ty["headlineFont"] = {"id": "headlinefont", "text": "Fuente del título", "value": {"text": "Bricolage Grotesque", "value": "var(--bricolage-grotesque)"}}
    ty["contentFont"] = {"id": "contentfont", "text": "Fuente del contenido", "value": {"text": "Figtree", "value": "var(--figtree)"}}
    pd["trackingCode"] = {"head": '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" '
                          'href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800'
                          '&family=Figtree:wght@400;500;600;700&display=swap">', "body": ""}
    json.dump(pd, open(DAT / "home-pagedata.json", "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(MAPA, open(DAT / "home-mapa.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = sum(len(s["elements"]) for s in sections)
    print("secciones", len(sections), [s["id"] for s in sections], "elementos", n, "bytes", len(json.dumps(pd)))

if __name__ == "__main__":
    main(sys.argv[1:])
