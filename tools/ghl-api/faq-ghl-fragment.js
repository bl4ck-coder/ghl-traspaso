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
    instalarPreguntasGhl();
