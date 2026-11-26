/* ADICIO CAPA GHL v2 · capa de animación (se pega una sola vez en GHL: código de seguimiento del Body del sitio).
   Contrato: se engancha solo por clases anim-*; nunca oculta contenido antes de que GSAP esté listo;
   arranca en DOMContentLoaded o en hydrationDone (GHL), una sola vez; con reduced-motion no anima nada.
   Idea: el trazo continuo del corazón de ADICIO es el hilo que entra, recorre el cuidado y cierra la página. */
(function () {
  'use strict';
  if (window.__adicioCapa) return;
  window.__adicioCapa = { estado: 'esperando' };

  var CDN = 'https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/';
  var LIBS = ['gsap.min.js', 'ScrollTrigger.min.js', 'SplitText.min.js'];
  // integridad (SRI) de los archivos fijos @3.13.0: si el CDN los cambia, no se ejecutan y la página queda quieta y completa
  var SRI = {
    'gsap.min.js': 'sha384-HOvlOYPIs/zjoIkWUGXkVmXsjr8GuZLV+Q+rcPwmJOVZVpvTSXQChiN4t9Euv9Vc',
    'ScrollTrigger.min.js': 'sha384-P8VzCVnT9NBUkMrpcIZrJbA7EBjJvh/fJS6PmP+4nLIM284DtsImIv8D0fFjIkeh',
    'SplitText.min.js': 'sha384-xb96EMJeax+NLXMC88ZBa1xAeAW+kn+horHh/zFlbMLG2UPWhMJJSlv7fi57hS+Q'
  };
  // el trazo del isotipo (3 arcos r=320 y 3 diagonales a 45°), redibujado del logo de 4500 px
  var TRAZO = 'M636 194A320 320 0 0 0 184 646L444 906A320 320 0 0 0 896 906L1151 646A320 320 0 0 0 699 194L444 454A320 320 0 0 0 444 906';
  var quieto = window.matchMedia('(prefers-reduced-motion: reduce)');
  var arrancada = false;

  function cargar(src) {
    return new Promise(function (ok, mal) {
      if (src.indexOf('gsap.min') > -1 && window.gsap) return ok();
      var s = document.createElement('script');
      s.src = CDN + src; s.async = false; s.onload = ok; s.onerror = mal;
      s.integrity = SRI[src]; s.crossOrigin = 'anonymous';
      document.head.appendChild(s);
    });
  }
  function todos(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }
  // GHL reemplaza los nodos de cada sección al hidratarla: cada efecto se monta una vez por nodo vivo
  var porEfecto = new Map(), vistos = new WeakSet(), montados = 0;
  function nuevos(sel, raiz) {
    if (!porEfecto.has(sel)) porEfecto.set(sel, new WeakSet());
    var marcados = porEfecto.get(sel); return todos(sel, raiz).filter(function (e) {
    if (marcados.has(e) || !e.isConnected) return false; marcados.add(e); montados++; return true; }); }

  // corazón dibujable: se pone encima de un elemento y toma sus colores del degradado de marca
  var nCorazon = 0;
  function corazon(contenedor, opciones) {
    var id = 'adicio-deg-' + (++nCorazon);
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '10 20 1320 1060');
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    svg.setAttribute('class', 'capa-corazon ' + (opciones.clase || ''));
    svg.innerHTML = '<defs><linearGradient id="' + id + '" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0" stop-color="#005EB8"/><stop offset="1" stop-color="#00C49A"/></linearGradient></defs>' +
      '<path d="' + TRAZO + '" fill="none" stroke="url(#' + id + ')" stroke-width="' + (opciones.grosor || 124) + '"/>';
    contenedor.appendChild(svg);
    var path = svg.querySelector('path');
    var largo = path.getTotalLength();
    path.style.strokeDasharray = largo;
    path.style.strokeDashoffset = largo;
    return { svg: svg, path: path, largo: largo };
  }

    /* GHL mantiene las preguntas editables, pero dibuja divs, no details/summary. */
    function preguntasGhl() {
      todos('.s-faq .hl-faq-child-heading').forEach(function (h, i) {
        var p = h.nextElementSibling;
        if (!p || !p.matches('.hl-faq-child-panel')) return;
        h.tabIndex = 0;
        h.setAttribute('role', 'button');
        if (!p.id) p.id = 'adicio-respuesta-' + i;
        h.setAttribute('aria-controls', p.id);
        h.setAttribute('aria-expanded', String(h.parentNode.classList.contains('active')));
      });
    }
    function instalarPreguntasGhl() {
      document.addEventListener('click', alternarPregunta, true);
      document.addEventListener('keydown', alternarPregunta, true);
      preguntasGhl();
      var zona = document.querySelector('.s-faq');
      if (zona) new MutationObserver(preguntasGhl).observe(zona, { childList: true, subtree: true });
    }
    function alternarPregunta(e) {
      if (e.type === 'keydown' && (e.repeat || (e.key !== 'Enter' && e.key !== ' '))) return;
      var h = e.target.closest && e.target.closest('.s-faq .hl-faq-child-heading');
      if (!h) return;
      var p = h.nextElementSibling, d = h.parentNode;
      if (!p || !p.matches('.hl-faq-child-panel')) return;
      e.preventDefault(); e.stopImmediatePropagation();
      var abre = h.getAttribute('aria-expanded') !== 'true';
      h.setAttribute('aria-expanded', String(abre));
      d.classList.toggle('active', abre);
      var actual = p.getBoundingClientRect().height, opacidad = +getComputedStyle(p).opacity;
      var gsap = window.gsap, ST = window.ScrollTrigger;
      gsap && gsap.killTweensOf(p);
      p.style.overflow = 'hidden';
      p.style.transition = 'none';
      p.style.height = 'auto';
      var objetivo = abre ? p.getBoundingClientRect().height : 0;
      if (!gsap || quieto.matches) {
        p.style.height = abre ? 'auto' : '0px';
        p.style.opacity = abre ? '1' : '0';
        if (ST) ST.refresh();
        return;
      }
      gsap.fromTo(p, {height: actual, opacity: opacidad}, {
        height: objetivo, opacity: abre ? 1 : 0, duration: abre ? 0.8 : 0.65, ease: 'power4.inOut',
        onComplete: function () { if (abre) p.style.height = 'auto'; if (ST) ST.refresh(); }
      });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', instalarPreguntasGhl, {once:true}); else instalarPreguntasGhl();

  function arrancar() {
    if (arrancada) return;
    arrancada = true;
    if (quieto.matches) { document.documentElement.classList.add('capa-quieta'); window.__adicioCapa.estado = 'quieta'; return; }
    LIBS.reduce(function (p, l) { return p.then(function () { return cargar(l); }); }, Promise.resolve())
      .then(function () { // SplitText mide líneas: espera las fuentes (máximo 2 s)
        var f = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
        return Promise.race([f, new Promise(function (ok) { setTimeout(ok, 2000); })]);
      })
      .then(montar)
      .catch(function () { window.__adicioCapa.estado = 'sin-gsap'; }); // sin GSAP la página queda como está, completa
  }

  function montar() {
    var gsap = window.gsap, ST = window.ScrollTrigger, Split = window.SplitText;
    gsap.registerPlugin(ST, Split);
    var raiz = document.documentElement;
    raiz.classList.add('capa-activa');
    var escritorio = window.matchMedia('(min-width: 981px)');
    var punteroFino = window.matchMedia('(pointer: fine)');
    var curva = 'power3.out';
    var cifras = [], imanes = [], sumarImanes = function () {};

    /* 1 · ACTO DE ENTRADA: el corazón se dibuja de un solo trazo detrás de la foto y la portada se asienta */
    var escena = document.querySelector('.anim-escena');
    // la portada ya está pintada cuando llega GSAP: no se la esconde para volver a mostrarla (se leía como un parpadeo,
    // medido en la grabación a 390). El acto de entrada es el trazo del corazón y la foto que se asienta, sin desaparecer.
    var tarde = true;
    window.__adicioCapa.entrada = 'trazo';
    if (escena) {
      var marco = escena.querySelector('.anim-paralaje');
      var tl = gsap.timeline({ defaults: { ease: curva } });
      if (marco) {
        marco.classList.add('capa-sin-fondo');
        var c = corazon(marco, { clase: 'capa-corazon-hero' });
        // el corazón dibujado reemplaza al del fondo ya completo (sin que se vea el cambio); el acto es una luz
        // que recorre el trazo continuo de punta a punta
        gsap.set(c.path, { strokeDashoffset: 0 });
        var luz = c.path.cloneNode();
        luz.setAttribute('stroke', '#ffffff'); luz.setAttribute('stroke-linecap', 'round'); luz.setAttribute('stroke-width', '70');
        luz.style.strokeDasharray = (c.largo * 0.16) + ' ' + c.largo; luz.style.strokeDashoffset = c.largo * 0.16; luz.style.opacity = 0.75;
        c.svg.appendChild(luz);
        tl.to(luz, { strokeDashoffset: -c.largo, duration: 2.2, ease: 'power2.inOut' }, 0.15)
          .to(luz, { opacity: 0, duration: 0.4 }, 2.0);
        var foto = marco.querySelector('.anim-foto');
        if (foto) tl.from(foto, { scale: 1.035, duration: 1.6, ease: 'power2.out' }, 0);
        // el trazo se desarma al bajar y se rearma al subir (reversible)
        gsap.to(c.path, { strokeDashoffset: c.largo * 0.62, ease: 'none',
          scrollTrigger: { trigger: escena, start: 'top top', end: 'bottom top', scrub: 0.8 } });
        if (foto) gsap.to(foto, { yPercent: -5, ease: 'none',
          scrollTrigger: { trigger: escena, start: 'top top', end: 'bottom top', scrub: 0.8 } });
      }
      var h1 = escena.querySelector('.anim-titular');
      if (h1 && !tarde) {
        var s1 = new Split(h1, { type: 'lines', mask: 'lines', linesClass: 'capa-linea' });
        tl.from(s1.lines, { yPercent: 105, duration: 1, stagger: 0.09, onComplete: function () { s1.revert(); } }, 0.2);
      }
      if (!tarde) {
        tl.from(todos('.anim-entra', escena), { opacity: 0, y: 24, duration: 0.9, stagger: 0.08 }, 0.55);
        tl.from(todos('.anim-pilar', escena), { opacity: 0, y: 36, duration: 0.9, stagger: 0.08 }, 0.8);
      }
    }

    function elementos() {
    /* 2 · TITULARES: entran por líneas con máscara (el texto queda igual al terminar) */
    nuevos('.anim-titular').forEach(function (t) {
      if (escena && escena.contains(t)) return;
      var s = new Split(t, { type: 'lines', mask: 'lines', linesClass: 'capa-linea' });
      gsap.from(s.lines, { yPercent: 105, duration: 1, stagger: 0.08, ease: curva,
        scrollTrigger: { trigger: t, start: 'top 85%', once: true }, onComplete: function () { s.revert(); } });
    });

    /* 3 · BLOQUES QUE ENTRAN (en tandas) */
    var sueltos = nuevos('.anim-entra, .anim-zona, .anim-cifra-caja, .anim-servicio').filter(function (e) { return !(escena && escena.contains(e)); });
    if (sueltos.length) { gsap.set(sueltos, { opacity: 0, y: 28 }); ST.batch(sueltos, { start: 'top 88%', once: true,
      onEnter: function (b) { gsap.to(b, { opacity: 1, y: 0, duration: 0.9, stagger: 0.07, ease: curva, overwrite: true }); } }); }

    /* 4 · PAPEL QUE SE ASIENTA: las secciones oscuras llegan como una placa que se abre a todo el ancho */
    nuevos('.anim-placa').forEach(function (p) {
      gsap.fromTo(p, { scale: 0.94, borderRadius: 56 }, { scale: 1, borderRadius: 0, ease: 'none',
        scrollTrigger: { trigger: p, start: 'top bottom', end: 'top 25%', scrub: 0.6 } });
    });

    /* 5 · SERVICIOS APILADOS (ronda 34, pedido de Nacho «volvé a como estaba antes»): en escritorio cada ficha se fija
       y la siguiente sube y se apila encima, de a una; la de abajo se aleja apenas. En el celular las fichas son más altas
       que la pantalla (foto + texto): fijarlas taparía el texto antes de leerlo, así que ahí entran de a una al llegar. */
    var fichas = nuevos('.anim-apilar');
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

    /* 6 · CIFRAS COMO ODÓMETRO: los dígitos ruedan hasta el número del cliente y el contenido vuelve a ser el original
       (con su signo aparte: «20+», «500+», «50+», «98%») */
    nuevos('.anim-cifra').forEach(function (el) {
      var original = Array.prototype.map.call(el.childNodes, function (n) { return n.cloneNode(true); }), texto = el.textContent;
      var volver = function () { el.replaceChildren.apply(el, original.map(function (n) { return n.cloneNode(true); })); };
      cifras.push(volver);
      ST.create({ trigger: el, start: 'top 88%', once: true, onEnter: function () {
        el.textContent = '';
        var leer = document.createElement('span'); leer.className = 'capa-sr'; leer.textContent = texto; el.appendChild(leer);
        var cols = [];
        texto.split('').forEach(function (ch) {
          var caja = document.createElement('span'); caja.className = 'capa-odo'; caja.setAttribute('aria-hidden', 'true');
          if (/\d/.test(ch)) {
            var col = document.createElement('span'); col.className = 'capa-odo-col';
            col.textContent = '0123456789'.split('').join('\n');
            caja.appendChild(col); cols.push({ col: col, n: +ch });
          } else { caja.className += ' cifra-signo'; caja.textContent = ch; }
          el.appendChild(caja);
        });
        cols.forEach(function (c, i) {
          gsap.fromTo(c.col, { yPercent: 0 }, { yPercent: -c.n * 10, duration: 1.6 + i * 0.25, ease: 'power4.out', delay: 0.1 });
        });
        gsap.delayedCall(2.4, volver);
      } });
    });

    /* 7 · EL HILO: el trazo de la marca baja por el recorrido del cuidado y enciende cada paso al llegar */
    todos('.anim-hilo').filter(function (h) { return h.isConnected && !h.querySelector(':scope > .capa-hilo'); }).forEach(function (h) {
      var pasos = todos('.anim-paso', h);
      if (pasos.length < 2) return;
      var linea = document.createElement('span');
      linea.className = 'capa-hilo'; linea.setAttribute('aria-hidden', 'true');
      h.appendChild(linea);
      function ubicar() {
        var r = h.getBoundingClientRect();
        var i0 = (pasos[0].querySelector('img') || pasos[0]).getBoundingClientRect();
        var i1 = (pasos[pasos.length - 1].querySelector('img') || pasos[pasos.length - 1]).getBoundingClientRect();
        linea.style.left = (i0.left + i0.width / 2 - r.left - 2) + 'px';
        linea.style.top = (i0.top + i0.height / 2 - r.top) + 'px';
        linea.style.height = (i1.top - i0.top) + 'px';
      }
      ubicar();
      ST.addEventListener('refreshInit', ubicar);
      gsap.fromTo(linea, { scaleY: 0 }, { scaleY: 1, ease: 'none',
        scrollTrigger: { trigger: h, start: 'top 60%', end: 'bottom 60%', scrub: 0.8 } });
      pasos.forEach(function (p) {
        if (vistos.has(p)) return; vistos.add(p); montados++;
        ST.create({ trigger: p, start: 'top 60%', end: 'bottom 60%', toggleClass: { targets: p, className: 'capa-encendido' } });
        gsap.fromTo(p, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, ease: curva, scrollTrigger: { trigger: p, start: 'top 90%', once: true } });
      });
    });

    /* 8 · PREGUNTAS: abrir y cerrar con la altura animada (nunca de golpe) */
    nuevos('.anim-acordeon').forEach(function (d) {
      var sum = d.querySelector('summary');
      var cuerpo = d.querySelector('summary + *');
      if (!sum || !cuerpo) return;
      var andando = false;
      sum.addEventListener('click', function (e) {
        e.preventDefault();
        if (andando) return;
        andando = true;
        if (!d.open) {
          d.open = true;
          gsap.fromTo(cuerpo, { height: 0, opacity: 0 }, { height: cuerpo.scrollHeight, opacity: 1, duration: 0.8, ease: 'power4.inOut',
            onComplete: function () { cuerpo.style.height = ''; andando = false; ST.refresh(); } });
          gsap.fromTo(cuerpo.children, { y: -10 }, { y: 0, duration: 0.8, ease: 'power3.out' });
        } else {
          gsap.to(cuerpo, { height: 0, opacity: 0, duration: 0.65, ease: 'power4.inOut',
            onComplete: function () { d.open = false; cuerpo.style.height = ''; cuerpo.style.opacity = ''; andando = false; ST.refresh(); } });
        }
      });
    });

    /* 9 · EL CORAZÓN VUELVE: en novedades se dibuja al llegar; en el pie cierra la página y el lema sube letra por letra */
    nuevos('.anim-corazon').forEach(function (img) {
      var caja = document.createElement('span'); caja.className = 'capa-corazon-caja'; caja.setAttribute('aria-hidden', 'true');
      img.parentNode.insertBefore(caja, img);
      caja.appendChild(img);
      var c = corazon(caja, { clase: 'capa-corazon-encima' });
      img.classList.add('capa-oculta');
      var enPie = !!img.closest('.anim-pie');
      gsap.to(c.path, { strokeDashoffset: 0, ease: enPie ? 'none' : 'power2.inOut', duration: enPie ? undefined : 1.6,
        scrollTrigger: enPie ? { trigger: caja, start: 'top 95%', end: 'top 45%', scrub: 0.8 } : { trigger: caja, start: 'top 85%', once: true } });
    });
    nuevos('.anim-lema').forEach(function (l) {
      var s = new Split(l, { type: 'chars, words', mask: 'chars', aria: 'none' }); // un <p> no admite aria-label (axe)
      gsap.from(s.chars, { yPercent: 110, duration: 0.9, stagger: 0.025, ease: 'power4.out',
        scrollTrigger: { trigger: l, start: 'top 90%', once: true }, onComplete: function () { s.revert(); } });
    });

    }
    elementos();

    /* 10 · LA ESCENA RESPONDE AL PUNTERO: corrimiento chico y con inercia (foto y trazo a distinta profundidad) */
    if (punteroFino.matches) {
      todos('.anim-paralaje').forEach(function (m) {
        var foto = m.querySelector('.anim-foto');
        var trazo = m.querySelector('.capa-corazon');
        var fx = foto && gsap.quickTo(foto, 'x', { duration: 1.1, ease: 'power3.out' });
        var fy = foto && gsap.quickTo(foto, 'y', { duration: 1.1, ease: 'power3.out' });
        var tx = trazo && gsap.quickTo(trazo, 'x', { duration: 1.4, ease: 'power3.out' });
        var ty = trazo && gsap.quickTo(trazo, 'y', { duration: 1.4, ease: 'power3.out' });
        var sec = m.closest('section') || m;
        sec.addEventListener('pointermove', function (e) {
          var r = sec.getBoundingClientRect();
          var px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
          if (fx) { fx(px * 14); fy(py * 10); }
          if (tx) { tx(px * -22); ty(py * -16); }
        });
        sec.addEventListener('pointerleave', function () { if (fx) { fx(0); fy(0); } if (tx) { tx(0); ty(0); } });
      });
    }

    /* 11 · MENÚ: al bajar se compacta y el vidrio se vuelve más denso */
    var navs = function () { var pie = document.querySelector('.anim-pie'); var fuera = !!pie && pie.getBoundingClientRect().top < innerHeight * 0.15;
      todos('.anim-nav').forEach(function (n) { if (n.classList.contains('capa-compacto') !== (scrollY > 80)) n.classList.toggle('capa-compacto', scrollY > 80);
        if (n.classList.contains('capa-nav-fuera') !== fuera) n.classList.toggle('capa-nav-fuera', fuera); }); };
    todos('.anim-nav').forEach(function (n) {
      ST.create({ start: 80, end: 'max', onUpdate: function () { navs(); }, onToggle: function () { navs(); } });
      var pie = document.querySelector('.anim-pie');
      if (pie) ST.create({ trigger: pie, start: 'top 15%', end: 'max', onToggle: function () { navs(); } });
    });

    /* 12 · IMÁN CON RESORTE (ronda 34, m3 y m9–m14): las tarjetas del héroe y los CTA principales siguen al puntero unos
       pocos px y al salir vuelven con un rebote chico. Resorte amortiguado propio (no una curva): parte de donde está, así
       que no salta al entrar ni vibra. ζ 0,45 y ω 10 rad/s, con tope de 0,9 px por cuadro de 60 Hz → sobrepaso de ≈ 20 %.
       Tarjeta: 8 px y hasta 2,2° de inclinación; botón: 5 px y sin inclinación (misma familia, más chico).
       Escribe `translate` y `rotate` (no `transform`), así se suma a lo que GSAP ya mueve. Táctil: no corre (no hay mouse). */
    if (punteroFino.matches) {
      // tope de velocidad: si el mouse salta de un borde al otro, el resorte no pasa de 0,9 px por cuadro (ni de 0,25° de giro)
      var OMEGA = 10, ZETA = 0.45, VMAX = 54, GMAX = 15, andandoIman = false, tPrevio = 0;
      var tope = function (v, i, max) { var r = Math.sqrt(v[i] * v[i] + v[i + 1] * v[i + 1]); if (r > max) { v[i] *= max / r; v[i + 1] *= max / r; } };
      var crearIman = function (el) {
        var tarjeta = !el.matches('a, button');
        el.classList.add('capa-iman');
        var m = { el: el, amp: tarjeta ? 8 : 5, giro: tarjeta ? 2.2 : 0,
          p: [0, 0, 0, 0], v: [0, 0, 0, 0], obj: [0, 0, 0, 0] }; // x, y (px) · giro alrededor de x e y (grados)
        el.addEventListener('pointermove', function (e) {
          if (e.pointerType !== 'mouse') return;
          var r = el.getBoundingClientRect();
          var nx = Math.max(-1, Math.min(1, (e.clientX - r.left - r.width / 2) / (r.width / 2)));
          var ny = Math.max(-1, Math.min(1, (e.clientY - r.top - r.height / 2) / (r.height / 2)));
          m.obj = [nx * m.amp, ny * m.amp * 0.6, -ny * m.giro, nx * m.giro];
          moverImanes();
        });
        el.addEventListener('pointerleave', function () { m.obj = [0, 0, 0, 0]; moverImanes(); });
        // con teclado: al enfocar con Tab sube unos px con el mismo resorte y al salir vuelve con el rebote
        el.addEventListener('focus', function () { if (el.matches(':focus-visible')) { m.obj = [0, -m.amp * 0.6, 0, 0]; moverImanes(); } });
        el.addEventListener('blur', function () { m.obj = [0, 0, 0, 0]; moverImanes(); });
        return m;
      };
      sumarImanes = function () { imanes.forEach(function (m) { if (!m.el.classList.contains('capa-iman')) m.el.classList.add('capa-iman'); });
        nuevos('.anim-iman, .s-novedades .suscripcion button.button-element').forEach(function (el) { imanes.push(crearIman(el)); }); };
      sumarImanes();
      var pintar = function (m) {
        var s = m.el.style, ax = m.p[2], ay = m.p[3], ang = Math.sqrt(ax * ax + ay * ay);
        s.translate = m.p[0].toFixed(2) + 'px ' + m.p[1].toFixed(2) + 'px';
        s.rotate = ang > 0.005 ? (ax / ang).toFixed(4) + ' ' + (ay / ang).toFixed(4) + ' 0 ' + ang.toFixed(3) + 'deg' : '';
      };
      var cuadro = function (t) {
        // el primer cuadro puede traer una marca anterior a performance.now(): nunca un paso negativo ni mayor a 50 ms
        var dt = (t - tPrevio) / 1000; tPrevio = t; if (!(dt > 0)) dt = 1 / 60; else if (dt > 0.05) dt = 0.05;
        var vivos = 0;
        imanes.forEach(function (m) {
          var quieto = true, k;
          for (var n = 0, h = dt / 4; n < 4; n++) { // 4 subpasos: estable aunque un cuadro llegue tarde
            for (k = 0; k < 4; k++) m.v[k] += (-OMEGA * OMEGA * (m.p[k] - m.obj[k]) - 2 * ZETA * OMEGA * m.v[k]) * h;
            tope(m.v, 0, VMAX); tope(m.v, 2, GMAX);
            for (k = 0; k < 4; k++) m.p[k] += m.v[k] * h;
          }
          for (k = 0; k < 4; k++) if (Math.abs(m.p[k] - m.obj[k]) > 0.01 || Math.abs(m.v[k]) > 0.02) quieto = false;
          if (quieto) { m.p = m.obj.slice(); m.v = [0, 0, 0, 0]; }
          if (!quieto || m.pintado !== m.p.join()) { pintar(m); m.pintado = m.p.join(); }
          if (!quieto) vivos++;
        });
        if (vivos) requestAnimationFrame(cuadro); else andandoIman = false;
      };
      var moverImanes = function () {
        if (andandoIman || !imanes.length) return;
        andandoIman = true; tPrevio = performance.now(); requestAnimationFrame(cuadro);
      };
      window.__adicioCapa.iman = { omega: OMEGA, zeta: ZETA, vmax: VMAX, n: imanes.length };
    }

    /* 14 · EL MAPA DE COBERTURA SE ENCIENDE (ronda 34b): la capa trae el mismo SVG del mapa (la imagen nativa que se
       edita en GHL) y lo pone en línea encima para animarlo: la costa real se dibuja, el AMBA se marca en su lugar, la lupa
       sale de ese punto y crece, y las zonas se encienden de a una en el orden de la lista (CABA, Corredor Norte, la Costa
       Atlántica que se traza) con un pulso. El agua se mueve apenas. Al pasar por cada zona de la lista, el mapa la destaca.
       La imagen nativa queda completa si el archivo no se puede leer o se cambia por otra imagen. */
    todos('.anim-mapa').forEach(function (caja) {
      var img = caja.querySelector('img');
      if (!img || !window.fetch || !window.DOMParser) return;
      var ns = 'http://www.w3.org/2000/svg', svg, tl, vivos = [], disparadores = [];
      var volverImagen = function () {
        if (tl) tl.kill();
        vivos.forEach(function (a) { a.kill(); });
        disparadores.forEach(function (s) { s.kill(); });
        if (svg) { svg.remove(); svg = null; }
        img.classList.remove('capa-oculta');
        window.__adicioCapa.mapa = 'imagen';
      };
      window.__adicioCapa.mapa = 'imagen';
      fetch(img.currentSrc || img.src).then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); }).then(function (txt) {
        if (quieto.matches) return;
        var dibujo = new DOMParser().parseFromString(txt, 'image/svg+xml').documentElement;
        if (!dibujo || dibujo.localName !== 'svg' || dibujo.getAttribute('viewBox') !== '0 0 400 500') return;
        // El <img> se puede reemplazar en el editor. Solo se inserta en línea el dibujo vectorial del mapa.
        var elementos = /^(svg|defs|g|path|rect|circle|use|clipPath|pattern|linearGradient|radialGradient|stop|filter|feDropShadow)$/;
        var atributos = /^(xmlns|id|viewBox|width|height|d|x[12]?|y[12]?|rx|cx|cy|r|dx|dy|fill(-opacity)?|stroke(-width|-opacity|-linecap|-linejoin)?|href|clip-path|patternUnits|gradientUnits|offset|stop-color|stop-opacity|filter|stdDeviation|flood-color|flood-opacity)$/;
        var valido = [dibujo].concat(todos('*', dibujo)).every(function (el) {
          return el.namespaceURI === ns && elementos.test(el.localName) && Array.from(el.attributes).every(function (a) {
            if (!atributos.test(a.name)) return false;
            if (a.name === 'href') return /^#[\w-]+$/.test(a.value);
            if (/^(fill|stroke|filter|clip-path)$/.test(a.name)) return /^(none|#[0-9a-f]{3,8}|url\(#[\w-]+\))$/i.test(a.value);
            return true;
          });
        });
        if (!valido || !dibujo.querySelector('path#tierra-borde') || !dibujo.querySelector('#lupa')) return;
        svg = document.importNode(dibujo, true);
        svg.removeAttribute('width'); svg.removeAttribute('height');
        svg.setAttribute('class', 'capa-mapa'); svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', img.getAttribute('alt') || ''); svg.setAttribute('focusable', 'false');
        caja.appendChild(svg);
        var antesDeLlegar = caja.getBoundingClientRect().top >= window.innerHeight;
        var q = function (s) { return svg.querySelector(s); };
        var borde = q('#tierra-borde'), lupa = q('#lupa'), origen = q('#lupa-origen'), aro = q('#lupa-origen circle');
        var zonas = ['caba', 'norte', 'costa'].map(function (z) { return { z: q('#z-' + z), pin: q('#pin-' + z) }; });
        tl = gsap.timeline({ paused: true, defaults: { ease: curva }, onComplete: function () { svg.classList.add('capa-listo'); } });
        // un trazo que se dibuja y al terminar queda como estaba (sin guiones); oculto hasta su turno (el remate redondo se vería)
        var trazar = function (el, dur, pos, ease) {
          var L = el.getTotalLength(); gsap.set(el, { strokeDasharray: L + ' ' + L, strokeDashoffset: L, visibility: 'hidden' });
          tl.set(el, { visibility: 'visible' }, pos);
          tl.to(el, { strokeDashoffset: 0, duration: dur, ease: ease || 'power2.inOut', clearProps: 'strokeDasharray,strokeDashoffset' }, pos);
        };
        if (borde) trazar(borde, 1.8, 0);
        if (origen) tl.from(origen, { opacity: 0, scale: 0.4, transformOrigin: '50% 50%', duration: 0.7, ease: 'back.out(1.8)', clearProps: 'opacity,transform' }, 0.35);
        todos('#lupa-lineas path', svg).forEach(function (l) { trazar(l, 0.6, 0.8, 'power1.out'); });
        if (lupa && aro) tl.from(lupa, { scale: 0.16, opacity: 0, svgOrigin: aro.getAttribute('cx') + ' ' + aro.getAttribute('cy'), duration: 1.05,
          ease: 'power3.out', clearProps: 'opacity,transform' }, 0.9);
        zonas.forEach(function (o, i) {
          var t = 1.6 + i * 0.4;
          if (o.z && i < 2) tl.from(o.z, { opacity: 0, duration: 0.7, clearProps: 'opacity' }, t);
          if (o.z && i === 2) todos('path', o.z).forEach(function (p) { trazar(p, 1.3, t, 'power2.out'); });
          if (o.pin) tl.from(o.pin, { scale: 0, transformOrigin: '50% 50%', duration: 0.65, ease: 'back.out(2.2)', clearProps: 'transform' }, t + (i === 2 ? 0.9 : 0.25));
        });
        // vida chica: un anillo por zona que se abre y se apaga (desfasados) y las olas que corren despacio
        zonas.forEach(function (o, i) {
          var c = o.pin && o.pin.querySelector('circle'); if (!c) return;
          var p = document.createElementNS(ns, 'circle');
          ['cx', 'cy'].forEach(function (a) { p.setAttribute(a, c.getAttribute(a)); });
          p.setAttribute('r', '8'); p.setAttribute('fill', 'none'); p.setAttribute('stroke', c.getAttribute('fill'));
          p.setAttribute('stroke-width', '2.5'); p.setAttribute('class', 'capa-pulso'); p.style.opacity = 0;
          o.pin.insertBefore(p, o.pin.firstChild);
          vivos.push(gsap.fromTo(p, { attr: { r: 8 }, opacity: 0.75 }, { attr: { r: 24 }, opacity: 0, duration: 2.4, ease: 'power2.out',
            repeat: -1, repeatDelay: 1.2, delay: 3.4 + i * 0.8, paused: true }));
        });
        var olas = q('#m-olas');
        if (olas) vivos.push(gsap.fromTo(olas, { attr: { patternTransform: 'translate(0 0)' } }, { attr: { patternTransform: 'translate(26 0)' },
          duration: 7, ease: 'none', repeat: -1, paused: true }));
        var seguir = function (si) { vivos.forEach(function (a) { si ? a.play() : a.pause(); }); };
        if (antesDeLlegar) {
          disparadores.push(ST.create({ trigger: caja, start: 'top 78%', once: true, onEnter: function () { tl.play(); } }));
        } else {
          tl.progress(1); // Si el visitante ya ve el mapa, no esconder sus zonas para volver a encenderlas.
        }
        var visible = ST.create({ trigger: caja, start: 'top bottom', end: 'bottom top', onToggle: function (s) { seguir(s.isActive); } });
        disparadores.push(visible);
        seguir(visible.isActive);
        // Revisión F · R34b-01: además del mouse, la zona se destaca al tocarla/clic (queda fija hasta tocar fuera,
        // tocarla de nuevo o Escape) y con el teclado (Tab la enfoca, Enter o Espacio la dejan fija).
        var lis = todos('[data-zona]', caja.closest('.cobertura-cuerpo') || caja.parentElement);
        var fija = null;
        var mostrar = function (z) {
          if (!svg) return;
          if (z) svg.setAttribute('data-foco', z); else svg.removeAttribute('data-foco');
          lis.forEach(function (o) { var on = !!fija && o.getAttribute('data-zona') === fija; o.classList.toggle('capa-zona-fija', on); var bt = o.querySelector('.zona-nombre'); if (bt) bt.setAttribute('aria-pressed', on ? 'true' : 'false'); });
        };
        var fijar = function (z) { fija = (fija === z) ? null : z; mostrar(fija); };
        lis.forEach(function (li) {
          var z = li.getAttribute('data-zona');
          // R34b F2: el botón accesible es el nombre de la zona (un li no puede ser role=button sin romper la lista);
          // el resto (mouse, toque, clic) sigue en el li.
          var bt = li.querySelector('.zona-nombre') || li;
          if (!bt.hasAttribute('tabindex')) bt.setAttribute('tabindex', '0');
          bt.setAttribute('role', 'button'); bt.setAttribute('aria-pressed', 'false');
          var det = bt.nextElementSibling; if (det && det.id) bt.setAttribute('aria-describedby', det.id);
          li.addEventListener('pointerenter', function (e) { if (e.pointerType !== 'touch') mostrar(z); });
          li.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'touch') mostrar(fija); });
          li.addEventListener('click', function () { fijar(z); });
          bt.addEventListener('focus', function () { mostrar(z); });
          bt.addEventListener('blur', function () { mostrar(fija); });
          bt.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fijar(z); }
            else if (e.key === 'Escape') { fija = null; mostrar(null); }
          });
        });
        document.addEventListener('pointerdown', function (e) {
          if (fija && !(e.target.closest && e.target.closest('[data-zona]'))) { fija = null; mostrar(null); }
        });
        var calmar = function (e) { if (e.matches) volverImagen(); };
        if (quieto.addEventListener) quieto.addEventListener('change', calmar); else if (quieto.addListener) quieto.addListener(calmar);
        img.classList.add('capa-oculta');
        window.__adicioCapa.mapa = 'en línea';
      }).catch(volverImagen);
    });

    /* 15 · CONTACTO: cada ícono saluda una vez al llegar (el teléfono suena, el sobre salta, el pin cae); al pasar el mouse, de nuevo */
    var datos = function () { nuevos('.datos').forEach(function (lista) {
      ST.create({ trigger: lista, start: 'top 80%', once: true, onEnter: function () {
        todos('.dato', lista).forEach(function (d, i) {
          gsap.delayedCall(0.25 + i * 0.22, function () { d.classList.add('capa-saluda');
            d.addEventListener('animationend', function () { d.classList.remove('capa-saluda'); }, { once: true }); });
        });
      } });
    }); };
    datos();

    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ST.refresh(); });
    window.addEventListener('load', function () { ST.refresh(); });
    window.__adicioCapa.estado = 'activa';

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

    /* 13 · REDUCIR MOVIMIENTO EN VIVO (RA31-07): todo termina en su estado legible y la capa se apaga */
    var alCambiar = function (e) {
      if (!e.matches) return;
      gsap.globalTimeline.getChildren(true, true, false).forEach(function (tw) { tw.progress(1); });
      ST.getAll().forEach(function (st) { st.kill(true); });
      gsap.killTweensOf('*');
      gsap.set(todos('[class*="anim-"]'), { clearProps: 'transform,opacity,scale,x,y' });
      todos('.capa-hilo').forEach(function (h) { h.style.transform = 'none'; });
      cifras.forEach(function (volver) { volver(); });
      imanes.forEach(function (m) { m.obj = [0, 0, 0, 0]; m.p = [0, 0, 0, 0]; m.v = [0, 0, 0, 0]; m.el.style.translate = ''; m.el.style.rotate = ''; });
      imanes = [];
      todos('.capa-mapa').forEach(function (s) { s.removeAttribute('data-foco'); });
      raiz.classList.remove('capa-activa'); raiz.classList.add('capa-quieta');
      window.__adicioCapa.estado = 'quieta';
    };
    if (quieto.addEventListener) quieto.addEventListener('change', alCambiar); else if (quieto.addListener) quieto.addListener(alCambiar);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arrancar); else arrancar();
  window.addEventListener('hydrationDone', arrancar);
  document.addEventListener('hydrationDone', arrancar);
})();
