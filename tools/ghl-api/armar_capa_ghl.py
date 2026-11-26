"""Arma capa-ghl.js desde la capa aprobada (W31/sitio/capa/capa.js), adaptada a GHL.

Problema medido (24/11): GHL hidrata cada sección recién cuando se acerca a la pantalla y REEMPLAZA sus nodos.
La capa montaba todo una sola vez al cargar, así que en 8 secciones las animaciones quedaban sobre nodos ya
descartados (corazones, hilo, titulares, cifras, lema...). Cambio: los efectos por elemento se montan con
`nuevos()` (cada nodo una sola vez) y un MutationObserver los vuelve a montar sobre los nodos que trae la
hidratación. La lógica de cada efecto no cambia.
"""
from pathlib import Path

W = Path(__file__).resolve().parents[2]
src = (W / '31-adicio-home-ghl/sitio/capa/capa.js').read_text(encoding='utf-8')
s = src


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep("  function todos(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }",
    "  function todos(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }\n"
    "  // GHL reemplaza los nodos de cada sección al hidratarla: cada efecto se monta una vez por nodo vivo\n"
    "  var porEfecto = new Map(), vistos = new WeakSet(), montados = 0;\n"
    "  function nuevos(sel, raiz) {\n"
    "    if (!porEfecto.has(sel)) porEfecto.set(sel, new WeakSet());\n"
    "    var marcados = porEfecto.get(sel); return todos(sel, raiz).filter(function (e) {\n"
    "    if (marcados.has(e) || !e.isConnected) return false; marcados.add(e); montados++; return true; }); }")

rep("    var curva = 'power3.out';\n",
    "    var curva = 'power3.out';\n    var cifras = [], imanes = [], sumarImanes = function () {};\n")

# 2..9 -> función repetible
rep("    /* 2 · TITULARES", "    function elementos() {\n    /* 2 · TITULARES")
rep("    /* 10 · LA ESCENA RESPONDE", "    }\n    elementos();\n\n    /* 10 · LA ESCENA RESPONDE")
for a in ["todos('.anim-titular').forEach", "todos('.anim-placa').forEach", "todos('.anim-cifra').forEach",
          "todos('.anim-hilo').forEach", "todos('.anim-acordeon').forEach", "todos('.anim-corazon').forEach",
          "todos('.anim-lema').forEach"]:
    rep(a, a.replace('todos(', 'nuevos('))
rep("var sueltos = todos('.anim-entra, .anim-zona, .anim-cifra-caja, .anim-servicio')",
    "var sueltos = nuevos('.anim-entra, .anim-zona, .anim-cifra-caja, .anim-servicio')")
rep("    gsap.set(sueltos, { opacity: 0, y: 28 });\n    ST.batch(sueltos,",
    "    if (sueltos.length) { gsap.set(sueltos, { opacity: 0, y: 28 }); ST.batch(sueltos,")
rep("      onEnter: function (b) { gsap.to(b, { opacity: 1, y: 0, duration: 0.9, stagger: 0.07, ease: curva, overwrite: true }); } });\n\n    /* 4 ·",
    "      onEnter: function (b) { gsap.to(b, { opacity: 1, y: 0, duration: 0.9, stagger: 0.07, ease: curva, overwrite: true }); } }); }\n\n    /* 4 ·")
rep("    var cifras = [];\n", "")

# 5 · apilado: por elemento (sin matchMedia, que no se puede repetir)
i0 = s.index("    ST.matchMedia({\n      '(min-width: 981px)'")
i1 = s.index("    /* 6 · CIFRAS")
s = s[:i0] + """    var fichas = nuevos('.anim-apilar');
    if (fichas.length && escritorio.matches) {
      var tarjetas = todos('.anim-apilar');
      tarjetas.forEach(function (t, i) {
        var sig = tarjetas[i + 1];
        if (!sig || (fichas.indexOf(t) < 0 && fichas.indexOf(sig) < 0)) return;
        gsap.to(t, { scale: 0.94, ease: 'none',
          scrollTrigger: { trigger: sig, start: 'top 85%', end: 'top 150px', scrub: 0.6 } });
      });
      nuevos('.anim-pila').forEach(function (pila) {
        ST.create({ trigger: pila, start: 'top bottom', end: 'bottom top', toggleClass: { targets: pila, className: 'capa-apilando' } });
      });
    } else if (fichas.length) {
      gsap.set(fichas, { opacity: 0, y: 28 });
      ST.batch(fichas, { start: 'top 88%', once: true,
        onEnter: function (b) { gsap.to(b, { opacity: 1, y: 0, duration: 0.9, stagger: 0.07, ease: curva, overwrite: true }); } });
    }

""" + s[i1:]

# 12 · imanes: repetible
rep("    var imanes = [];\n", "")
rep("      imanes = todos('.anim-iman').map(function (el) {", "      var crearIman = function (el) {")
rep("        return m;\n      });", "        return m;\n      };\n"
    "      sumarImanes = function () { nuevos('.anim-iman').forEach(function (el) { imanes.push(crearIman(el)); }); };\n"
    "      sumarImanes();")

# 15 · contacto: repetible
rep("    todos('.datos').forEach(function (lista) {", "    var datos = function () { nuevos('.datos').forEach(function (lista) {")
rep("      } });\n    });\n\n    if (document.fonts", "      } });\n    }); };\n    datos();\n\n    if (document.fonts")

# hilo: GHL conserva la columna pero le borra la línea inyectada -> se vuelve a montar si falta
rep("nuevos('.anim-hilo').forEach(function (h) {",
    "todos('.anim-hilo').filter(function (h) { return h.isConnected && !h.querySelector(':scope > .capa-hilo'); }).forEach(function (h) {")
# pasos: cada uno entra una sola vez y siempre termina visible (fromTo, no from: un segundo from tomaba opacidad 0 como final)
rep("      pasos.forEach(function (p) {\n        ST.create({ trigger: p, start: 'top 60%', end: 'bottom 60%', toggleClass: { targets: p, className: 'capa-encendido' } });\n        gsap.from(p, { y: 30, opacity: 0, duration: 0.9, ease: curva, scrollTrigger: { trigger: p, start: 'top 90%', once: true } });\n      });",
    "      pasos.forEach(function (p) {\n        if (vistos.has(p)) return; vistos.add(p); montados++;\n        ST.create({ trigger: p, start: 'top 60%', end: 'bottom 60%', toggleClass: { targets: p, className: 'capa-encendido' } });\n        gsap.fromTo(p, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, ease: curva, scrollTrigger: { trigger: p, start: 'top 90%', once: true } });\n      });")
# imanes: el nodo sigue (con sus eventos) pero Vue le pisa la clase -> se repone
rep("      sumarImanes = function () { nuevos('.anim-iman')",
    "      sumarImanes = function () { imanes.forEach(function (m) { if (!m.el.classList.contains('capa-iman')) m.el.classList.add('capa-iman'); });\n        nuevos('.anim-iman')")
# menú: toggleClass solo actúa al cruzar; si Vue pisa la clase, se repone por posición
rep("      ST.create({ start: 80, end: 'max', toggleClass: { targets: n, className: 'capa-compacto' } });",
    "      ST.create({ start: 80, end: 'max', onUpdate: function () { navs(); }, onToggle: function () { navs(); } });")
rep("      if (pie) ST.create({ trigger: pie, start: 'top 15%', end: 'max', toggleClass: { targets: n, className: 'capa-nav-fuera' } });",
    "      if (pie) ST.create({ trigger: pie, start: 'top 15%', end: 'max', onToggle: function () { navs(); } });")
rep("    /* 11 · MENÚ: al bajar se compacta y el vidrio se vuelve más denso */\n",
    "    /* 11 · MENÚ: al bajar se compacta y el vidrio se vuelve más denso */\n"
    "    var navs = function () { var pie = document.querySelector('.anim-pie'); var fuera = !!pie && pie.getBoundingClientRect().top < innerHeight * 0.15;\n"
    "      todos('.anim-nav').forEach(function (n) { if (n.classList.contains('capa-compacto') !== (scrollY > 80)) n.classList.toggle('capa-compacto', scrollY > 80);\n"
    "        if (n.classList.contains('capa-nav-fuera') !== fuera) n.classList.toggle('capa-nav-fuera', fuera); }); };\n")

# vigía de hidratación
rep("    window.__adicioCapa.estado = 'activa';\n",
    """    window.__adicioCapa.estado = 'activa';

    /* 16 · GHL HIDRATA POR SECCIÓN: al llegar nodos nuevos, se montan sus efectos (los ya montados no se tocan) */
    var espera = 0, rondas = 0;
    var remontar = function () {
      if (!raiz.classList.contains('capa-activa')) return;
      var antes = montados;
      var hilos = todos('.capa-hilo').length;
      elementos(); sumarImanes(); datos(); navs();
      if (montados > antes || todos('.capa-hilo').length > hilos) { rondas++; window.__adicioCapa.remontes = rondas; ST.refresh(); }
    };
    new MutationObserver(function (ms) {
      for (var i = 0; i < ms.length; i++) if (ms[i].addedNodes.length || ms[i].removedNodes.length) { clearTimeout(espera); espera = setTimeout(remontar, 60); return; }
    }).observe(document.body, { childList: true, subtree: true });
""")
# El botón de suscripción se genera dentro de un formulario nativo y no hereda las clases de la página.
rep("nuevos('.anim-iman').forEach", "nuevos('.anim-iman, .s-novedades .suscripcion button.button-element').forEach")
faq = Path(__file__).with_name('faq-ghl-fragment.js').read_text(encoding='utf-8')
# FAQ stays keyboard-accessible even if GSAP is blocked or motion is reduced.
faq = faq.replace("      gsap && gsap.killTweensOf(p);", "      var gsap = window.gsap, ST = window.ScrollTrigger;\n      gsap && gsap.killTweensOf(p);")
faq = faq.replace("    instalarPreguntasGhl();", "    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', instalarPreguntasGhl, {once:true}); else instalarPreguntasGhl();")
rep("  function arrancar() {", faq + "\n  function arrancar() {")
rep("/* ADICIO · capa de animación", "/* ADICIO CAPA GHL v2 · capa de animación")
out = Path(__file__).with_name('capa-ghl.js')
out.write_text(s, encoding='utf-8')
print(out, len(s))
