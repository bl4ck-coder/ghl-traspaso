/* ADICIO PULIDO 1 JS · signo chico de las cifras; el número sigue editable en GHL. */
(() => {
  const run = () => document.querySelectorAll('.s-equipo .cifra-numero p').forEach(p => {
    if (p.querySelector('.cifra-signo')) return;
    const m = p.textContent.trim().match(/^(\d+)([+%])$/);
    if (!m) return;
    p.textContent = m[1];
    const s = document.createElement('span'); s.className = 'cifra-signo'; s.textContent = m[2]; p.append(s);
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  window.addEventListener('hydrationDone', run); setTimeout(run, 1500);
})();
