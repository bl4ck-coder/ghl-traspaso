"""Resume cada paginas/<id>.json en paginas/_resumen/<id>.json y un índice paginas/_indice.json.
Por página: sitio, nombre, url, estado, SEO, código, y por sección: nombre + elementos (tipo, H, texto, acciones, ids conectados)."""
import json, glob, re, html
from pathlib import Path

INV = Path(__file__).resolve().parent.parent
sitios = {Path(f).stem: json.load(open(f, encoding="utf-8")) for f in glob.glob(str(INV / "sitios" / "*.json"))}
paso = {}
for sid, s in sitios.items():
    for st in s["steps"]:
        for pg in st.get("pages", []):
            paso[pg] = (sid, s["name"], st)


def txt(v):
    if isinstance(v, dict):
        v = v.get("value", "")
    v = re.sub(r"<[^>]+>", " ", str(v or ""))
    return re.sub(r"\s+", " ", html.unescape(v)).strip()


def val(e, k):
    x = (e.get("extra") or {}).get(k)
    return x.get("value") if isinstance(x, dict) else x


def resumen_elem(e):
    t = e.get("meta") or e.get("type")
    o = {"tipo": t, "id": e["id"]}
    cc = val(e, "customClass")
    if cc:
        o["clase"] = cc
    if t in ("heading", "sub-heading", "paragraph", "bulletList"):
        tx = val(e, "text") if t != "bulletList" else val(e, "text") or val(e, "listItems")
        o["texto"] = txt(tx)[:300]
        m = re.search(r"<(h[1-6])", str(tx or ""))
        o["tag"] = e.get("tag") or (m.group(1) if m else None) or e.get("tagName")
    elif t == "button":
        o["texto"] = txt(val(e, "text"))[:120]
        o["accion"] = val(e, "action")
        for k in ("visitWebsite", "stepPath", "scrollToElement", "phoneNumber", "emailAddress", "productId", "popupId", "saleAction"):
            v = val(e, k)
            if v not in (None, "", {}, []):
                o[k] = v
    elif t == "image":
        ip = val(e, "imageProperties") or {}
        o["src"] = ip.get("url") if isinstance(ip, dict) else ip
        o["alt"] = ip.get("altText") if isinstance(ip, dict) else None
    elif t in ("form", "survey"):
        o.update({k: val(e, k) for k in (e.get("extra") or {}) if k not in ("nodeId", "visibility", "customClass")})
    elif t == "calendar":
        o["calendarId"] = val(e, "calendarId"); o["accion"] = val(e, "action"); o["visitWebsite"] = val(e, "visitWebsite")
    elif t == "order-form":
        ex = e["extra"]
        o["pasos"] = [{"id": s.get("id"), "titulo": s.get("headline"), "campos": [f.get("id") for f in s.get("fields", [])]} for s in (val(e, "steps") or [])]
        for k in ("render", "productOrder", "saleAction", "stepPath", "visitWebsite", "bumps", "orderFormTheme", "showOrderBump", "enableCouponCodes", "termsAndConditions"):
            o[k] = val(e, k)
    elif t == "faq":
        o["preguntas"] = [{"p": txt(q.get("heading")), "r": txt(q.get("text"))[:400]} for q in (val(e, "faqList") or [])]
    elif t in ("custom-code", "blog", "blog-subscribe-form", "nav-menu-v2", "nav-menu", "logo-showcase", "image-slider", "video", "svg", "divider"):
        ex = {k: v for k, v in (e.get("extra") or {}).items() if k not in ("nodeId", "visibility")}
        o["extra"] = json.loads(json.dumps(ex, ensure_ascii=False))
        if t == "custom-code":
            code = str(val(e, "customCode") or val(e, "code") or ex)
            o["extra"] = {"largo": len(code), "inicio": code[:400]}
    if e.get("customCss"):
        o["css_elem"] = str(e["customCss"])[:300]
    return o


indice = []
(INV / "paginas" / "_resumen").mkdir(exist_ok=True)
for f in sorted(glob.glob(str(INV / "paginas" / "*.json"))):
    pid = Path(f).stem
    if pid.startswith("_"):
        continue
    r = json.load(open(f, encoding="utf-8"))
    doc, pd = r["doc"], r["pageData"] or {}
    sid, sname, st = paso.get(pid, (None, None, {}))
    secciones = []
    for s in pd.get("sections", []):
        md = s.get("metaData", {}) or {}
        els = [resumen_elem(e) for e in s["elements"] if e.get("type") == "element"]
        secciones.append({"id": s["id"], "nombre": md.get("title") or md.get("name") or (md.get("extra") or {}).get("name", {}).get("value") if isinstance((md.get("extra") or {}).get("name"), dict) else md.get("title"),
                          "global": bool(md.get("isGlobal") or s.get("isGlobal")), "elementos": els})
    tipos = {}
    for s in secciones:
        for e in s["elementos"]:
            tipos[e["tipo"]] = tipos.get(e["tipo"], 0) + 1
    vh = sorted([x for x in doc.get("versionHistory") or [] if isinstance(x, dict)], key=lambda x: str(x.get("updatedAt", "")))
    res = {
        "sitio": sname, "sitioId": sid, "paso": st.get("name"), "pasoId": st.get("id"), "tipoPaso": st.get("type"), "rutaPaso": st.get("url"),
        "pagina": doc.get("name"), "pageId": pid, "urlDoc": doc.get("url"), "version": doc.get("version"), "pageVersion": doc.get("pageVersion"),
        "actualizada": doc.get("updatedAt"), "productosPaso": st.get("products"), "productosDoc": doc.get("products"),
        "seo": doc.get("meta"), "schemaMarkupId": (vh[-1].get("schemaMarkupId") if vh else None),
        "ultimaVersion": {k: vh[-1].get(k) for k in ("pageType", "updatedAt", "integrations", "publishedAt", "isPublished", "type") if vh and k in vh[-1]} if vh else None,
        "historial": [{k: x.get(k) for k in ("pageType", "updatedAt", "version", "pageVersion", "schemaMarkupId") if k in x} for x in vh][-6:],
        "trackingCodePagina": pd.get("trackingCode"), "pageStyles": str(pd.get("pageStyles") or "")[:3000],
        "fuentes": (pd.get("general") or {}).get("general", {}).get("fontsToLoad"),
        "popups": len(pd.get("popupsList") or []), "tipos": tipos, "secciones": secciones,
    }
    (INV / "paginas" / "_resumen" / f"{pid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    indice.append({k: res[k] for k in ("sitio", "paso", "tipoPaso", "rutaPaso", "pageId", "urlDoc", "actualizada", "tipos", "schemaMarkupId")} | {"seoTitulo": (res["seo"] or {}).get("title"), "secciones": len(secciones), "ultimaVersion": res["ultimaVersion"]})
(INV / "paginas" / "_indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
for i in indice:
    print(i["sitio"][:22] if i["sitio"] else None, "|", i["paso"], "|", i["rutaPaso"], "|", i["pageId"], "|", i["secciones"], "|", {k: v for k, v in i["tipos"].items() if k not in ("paragraph", "heading", "sub-heading", "image")})
