/* Conserva los enlaces nativos de GHL. Solo adapta el disparador del menú. */
(() => {
  'use strict';
  const mobile = matchMedia('(max-width:1120px)');
  function install() {
    const nav = document.querySelector('.s-nav');
    const toggle = nav?.querySelector('.col-menu .nav-menu-mobile');
    const list = nav?.querySelector('.col-menu .nav-menu-desktop');
    if (!nav || !toggle || !list || nav.dataset.adicioMenuListo) return;
    nav.dataset.adicioMenuListo = '1';
    list.id ||= 'adicio-menu-nativo';
    toggle.setAttribute('role','button');
    toggle.tabIndex = 0;
    toggle.setAttribute('aria-controls',list.id);
    toggle.setAttribute('aria-label','Menú principal');
    const isOpen = () => nav.hasAttribute('data-adicio-menu-abierto');
    const set = on => {
      nav.toggleAttribute('data-adicio-menu-abierto',on);
      toggle.setAttribute('aria-expanded',String(on));
    };
    set(false);
    nav.addEventListener('click',e=>{
      if (!mobile.matches) return;
      if (toggle.contains(e.target)) {e.preventDefault();e.stopImmediatePropagation();set(!isOpen());}
      else if (list.contains(e.target) && e.target.closest('a')) set(false);
    },true);
    nav.addEventListener('keydown',e=>{
      if (!mobile.matches) return;
      if (toggle===e.target && (e.key==='Enter'||e.key===' ')) {e.preventDefault();set(!isOpen());}
    });
    document.addEventListener('keydown',e=>{
      if (e.key==='Escape'&&isOpen()) {set(false);toggle.focus();}
    });
    document.addEventListener('pointerdown',e=>{if (isOpen()&&!nav.contains(e.target)) set(false);});
    mobile.addEventListener('change',()=>set(false));
  }
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',install,{once:true});
  else install();
  document.addEventListener('hydrationDone',install);
})();
