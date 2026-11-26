/* ADICIO MAPA GHL v2. Mantiene la imagen nativa como respaldo. */
(() => {
  const names = ['caba', 'norte', 'costa'];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  function hooks() {
    for (const name of names) {
      document.querySelectorAll('.s-contacto .zona-' + name).forEach(n => { n.dataset.zona = name; });
    }
  }
  hooks();
  document.addEventListener('DOMContentLoaded', hooks, { once:true });
  window.addEventListener('hydrationDone', hooks);
  document.addEventListener('hydrationDone', hooks);
  function protect() {
  const box = document.querySelector('.s-contacto .mapa-caja');
  if (!box || reduce.matches || box.dataset.adicioMapGuard) return;
  box.dataset.adicioMapGuard = 'ready';
  let overlay = box.querySelector('svg.capa-mapa'), image = box.querySelector('img.mapa-img'), reattached = false;
  const observer = new MutationObserver(records => {
    if (reduce.matches) { observer.disconnect(); return; }
    for (const r of records) {
      for (const n of r.addedNodes) {
        if (n.nodeType === 1 && n.matches('svg.capa-mapa')) {
          overlay = n;
          image = box.querySelector('img.mapa-img');
        }
      }
    }
    if (!overlay || overlay.parentNode === box) return;
    // GHL may reconcile the column once on the visitor's first interaction.
    // Keep the same SVG (GSAP tweens and zone events point to this instance).
    if (!reattached && box.isConnected && box.querySelector('img.mapa-img') === image) {
      reattached = true;
      box.appendChild(overlay);
    } else {
      image?.classList.remove('capa-oculta');
      observer.disconnect();
    }
  });
  observer.observe(box, { childList:true });
  reduce.addEventListener('change', e => { if (e.matches) observer.disconnect(); }, {once:true});
  }
  protect();
  document.addEventListener('DOMContentLoaded', protect, {once:true});
  document.addEventListener('hydrationDone', protect);
})();
