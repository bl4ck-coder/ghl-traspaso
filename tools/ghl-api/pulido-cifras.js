/* ADICIO CIFRAS ESTABLES 1 · conserva el signo cuando GHL vuelve a dibujar Equipo. */
(() => {
  const selector = '.s-equipo .cifra-numero p';
  let queued = false;
  function render() {
    queued = false;
    document.querySelectorAll(selector).forEach(p => {
      if (p.childElementCount) return; // No tocar el odómetro ni formato que el editor agregó.
      const m = p.textContent.trim().match(/^(\d+)([+%])$/);
      if (!m) return;
      const sign = document.createElement('span');
      sign.className = 'cifra-signo'; sign.textContent = m[2];
      p.replaceChildren(document.createTextNode(m[1]), sign);
    });
  }
  function relevant(node) {
    return node.nodeType === 1 && (node.matches('.s-equipo') || node.querySelector('.s-equipo'));
  }
  function start() {
    const root = document.querySelector('#preview-container');
    if (!root) return;
    render();
    new MutationObserver(records => {
      if (!queued && records.some(r => r.target.closest?.('.s-equipo') || [...r.addedNodes].some(relevant))) {
        queued = true; requestAnimationFrame(render);
      }
    }).observe(root, {childList:true, subtree:true, characterData:true});
    window.addEventListener('hydrationDone', render);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true});
  else start();
})();
