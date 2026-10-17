/* Reading Compass — progressive enhancement of the original Jump to section card.
   No framework, no duplicate navigation. Original anchor links work without JS. */
(() => {
  'use strict';
  const slot = document.querySelector('.cv__toc-slot');
  const nav = slot?.querySelector('.cv__toc');
  const marker = slot?.querySelector('.compass__threshold');
  const trigger = nav?.querySelector('.compass__trigger');
  const list = nav?.querySelector('#compass-links');
  const tools = nav?.querySelector('.compass__tools');
  if (!slot || !nav || !marker || !trigger || !list || !tools) return;

  const currentText = trigger.querySelector('.compass__context');
  const percentage = trigger.querySelector('.compass__percentage');
  const fill = trigger.querySelector('.compass__track-fill');
  const returnButton = tools.querySelector('.compass__return');
  const shareButton = tools.querySelector('.compass__share');
  const status = tools.querySelector('.compass__status');
  const links = Array.from(list.querySelectorAll('a[href^="#"]'));
  const targets = links.map(link => ({
    link,
    section: document.getElementById(link.hash.slice(1))
  })).filter(x => x.section);
  if (!targets.length) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const breakpoint = window.matchMedia('(max-width: 900px)');
  let docked = false;
  let expanded = false;
  let fullHeight = 0;
  let activeId = '';
  let returnTo = null;
  let scheduled = false;
  let transitioning = false;
  let suppressReturn = false;
  let statusTimer;

  trigger.hidden = false;
  tools.hidden = false;
  nav.dataset.compassReady = '';
  trigger.setAttribute('aria-expanded', 'false');

  function measureCard() {
    if (docked) return;
    fullHeight = Math.ceil(nav.getBoundingClientRect().height);
    slot.style.setProperty('--compass-card-height', fullHeight + 'px');
  }

  function setExpanded(open, focusItem = false) {
    expanded = docked && open;
    nav.dataset.open = String(expanded);
    trigger.setAttribute('aria-expanded', String(expanded));
    if (expanded && focusItem) {
      (list.querySelector('a[aria-current="location"]') || links[0])?.focus({ preventScroll: true });
    }
  }

  function moveNav(shouldDock) {
    if (shouldDock === docked) return;
    const previous = nav.getBoundingClientRect();
    const visible = previous.bottom > 24 && previous.top < window.innerHeight - 24;
    const apply = () => {
      if (shouldDock) {
        // Keep one nav node: it is visibly transformed, not replaced by a
        // different pill. The mobile grid slot collapses as the card shrinks.
        measureCard();
        nav.dataset.docked = 'true';
        slot.dataset.morphed = 'true';
        document.body.appendChild(nav);
      } else {
        nav.removeAttribute('data-docked');
        slot.insertBefore(nav, marker);
        slot.removeAttribute('data-morphed');
      }
      docked = shouldDock;
      if (!docked) {
        setExpanded(false);
        measureCard();
      }
    };

    // Start the transition while the source card is still on-screen.
    // Reduced motion and deep links should change state immediately.
    if (!visible || reduceMotion.matches) {
      apply();
      return;
    }
    if (typeof document.startViewTransition === 'function' && !transitioning) {
      transitioning = true;
      try {
        const transition = document.startViewTransition(apply);
        transition.finished.catch(() => {}).finally(() => {
          transitioning = false;
          scheduleUpdate();
        });
        return;
      } catch (_) {
        transitioning = false;
      }
    }

    // Fallback for browsers without the View Transitions API: animate the
    // very same nav element from its measured card rectangle into the pill.
    apply();
    if (typeof nav.animate === 'function') {
      const next = nav.getBoundingClientRect();
      const dx = previous.left - next.left;
      const dy = previous.top - next.top;
      const sx = Math.max(.4, Math.min(4, previous.width / Math.max(next.width, 1)));
      const sy = Math.max(.4, Math.min(4, previous.height / Math.max(next.height, 1)));
      nav.animate([
        { transform: `translateX(-50%) translate(${dx}px, ${dy}px) scale(${sx}, ${sy})`,
          transformOrigin: '0 0', opacity: .85 },
        { transform: shouldDock ? 'translateX(-50%)' : 'none',
          transformOrigin: '0 0', opacity: 1 }
      ], { duration: 560, easing: 'cubic-bezier(.2,.8,.2,1)' });
    }
  }

  function updateActive() {
    const line = Math.min(180, window.innerHeight * 0.30);
    let chosen = null;
    // DOM order, not menu grouping order: reflects the section actually read.
    for (const candidate of [...targets].sort(
      (a, b) => a.section.compareDocumentPosition(b.section) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1
    )) {
      if (candidate.section.closest('details:not([open])')) continue;
      if (candidate.section.getBoundingClientRect().top <= line) chosen = candidate;
    }
    activeId = chosen?.section.id || '';
    for (const {link, section} of targets) {
      if (section.id === activeId) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
    const label = chosen?.link.textContent.trim() || 'Jump to sections';
    currentText.textContent = label;
    const available = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    const pct = available ? Math.min(100, Math.round(window.scrollY / available * 100)) : 100;
    percentage.textContent = pct + '%';
    fill.style.width = pct + '%';
    trigger.setAttribute('aria-label',
      'Jump to sections. Current: ' + label + '. Page progress: ' + pct + ' percent.');
  }

  function update() {
    scheduled = false;
    if (!transitioning) {
      // Dock when the top of the real Jump to card is still clearly
      // visible, not after its bottom has disappeared above the screen.
      // The gap between enter and exit is intentional scroll hysteresis.
      const boundary = slot.getBoundingClientRect().top;
      const enter = Math.max(150, Math.min(320, window.innerHeight * .45));
      const exit = enter + 130;
      if (!docked && boundary < enter) moveNav(true);
      else if (docked && boundary > exit) moveNav(false);
    }
    updateActive();
  }

  function scheduleUpdate() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(update);
  }

  function openDetailsFor(element) {
    for (let details = element.closest('details'); details;
      details = details.parentElement?.closest('details')) {
      details.open = true;
    }
  }

  function goTo(element, hash) {
    openDetailsFor(element);
    const behavior = reduceMotion.matches ? 'auto' : 'smooth';
    element.scrollIntoView({ behavior, block: 'start' });
    history.pushState(null, '', hash);
    scheduleUpdate();
  }

  for (const {link, section} of targets) {
    link.addEventListener('click', event => {
      // Keep regular anchor behaviour if JS was disabled or state is incomplete.
      event.preventDefault();
      if (!suppressReturn) {
        returnTo = {
          y: window.scrollY,
          url: location.pathname + location.search + location.hash
        };
        returnButton.hidden = false;
      }
      setExpanded(false);
      goTo(section, link.hash);
    });
  }

  trigger.addEventListener('click', () => {
    if (!docked) return;
    setExpanded(!expanded, !expanded);
  });

  returnButton.addEventListener('click', () => {
    if (!returnTo) return;
    const target = returnTo;
    returnTo = null;
    returnButton.hidden = true;
    suppressReturn = true;
    setExpanded(false);
    history.pushState(null, '', target.url);
    window.scrollTo({ top: target.y, behavior: reduceMotion.matches ? 'auto' : 'smooth' });
    suppressReturn = false;
    scheduleUpdate();
  });

  shareButton.addEventListener('click', async () => {
    const href = location.origin + location.pathname + location.search +
      (activeId ? '#' + encodeURIComponent(activeId) : '');
    try {
      await navigator.clipboard.writeText(href);
      status.textContent = 'Copied';
    } catch (_) {
      status.textContent = 'Copy unavailable';
    }
    clearTimeout(statusTimer);
    statusTimer = setTimeout(() => { status.textContent = ''; }, 2500);
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && expanded) {
      setExpanded(false);
      trigger.focus({ preventScroll: true });
      event.preventDefault();
    }
  });
  document.addEventListener('pointerdown', event => {
    if (expanded && !nav.contains(event.target)) setExpanded(false);
  });

  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', () => {
    if (!docked) measureCard();
    scheduleUpdate();
  }, { passive: true });
  breakpoint.addEventListener?.('change', () => {
    if (!docked) measureCard();
    scheduleUpdate();
  });

  const directHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const element = id && document.getElementById(id);
    if (element) {
      const closed = element.closest('details:not([open])');
      if (closed) {
        openDetailsFor(element);
        requestAnimationFrame(() => element.scrollIntoView({ block: 'start' }));
      }
    }
    scheduleUpdate();
  };
  window.addEventListener('hashchange', directHash);

  // Observe section intersections AND schedule cheap, rAF-throttled scroll updates.
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(scheduleUpdate, { rootMargin: '-15% 0px -65% 0px' });
    targets.forEach(({section}) => observer.observe(section));
  }
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(() => {
      if (!docked) measureCard();
      scheduleUpdate();
    });
    observer.observe(list);
  }

  measureCard();
  directHash();
  scheduleUpdate();
})();
