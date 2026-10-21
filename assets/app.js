'use strict';
(() => {
  const dawIds = ['ableton', 'logic', 'cubase', 'flstudio', 'protools'];
  const operationEls = [...document.querySelectorAll('[data-operation]')];
  const operationIds = operationEls.map(el => el.dataset.operation);
  const routes = [...operationIds, 'unterricht', 'woerterbuch', 'quellen'];
  const all = selector => [...document.querySelectorAll(selector)];
  const read = (key, fallback) => { try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; } };
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  let storedProgress;
  try { storedProgress = JSON.parse(read('daw-basics-progress-v1', '[]')); } catch { storedProgress = []; }
  const done = new Set((Array.isArray(storedProgress) ? storedProgress : []).filter(id => operationIds.includes(id)));
  const queryDaw = new URLSearchParams(location.search).get('daw');
  let daw = dawIds.includes(queryDaw) ? queryDaw : read('daw-basics-daw', 'ableton');
  if (!dawIds.includes(daw)) daw = 'ableton';
  let compare = false;
  let current = operationIds[0];
  let statusTimer;
  function notice(text) {
    const el = document.querySelector('.status');
    el.textContent = text;
    el.hidden = false;
    clearTimeout(statusTimer);
    statusTimer = setTimeout(() => { el.hidden = true; }, 3500);
  }
  function updateDaw(id, updateURL = true) {
    if (!dawIds.includes(id)) return;
    daw = id;
    save('daw-basics-daw', daw);
    all('.daw-button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.daw === daw)));
    all('.daw-tab').forEach(button => {
      const selected = button.dataset.daw === daw;
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
    });
    all('.daw-panel').forEach(panel => {
      panel.hidden = !compare && panel.dataset.daw !== daw;
      panel.classList.toggle('print-selected', panel.dataset.daw === daw);
      if (compare) panel.removeAttribute('role'); else panel.setAttribute('role', 'tabpanel');
    });
    all('.instruction-section').forEach(section => section.classList.toggle('compare-mode', compare));
    all('.compare-toggle').forEach(input => { input.checked = compare; });
    const label = document.querySelector(`.daw-button[data-daw="${daw}"]`).textContent;
    document.querySelector('.print-daw').textContent = `DAW Basics · Anleitung für ${label} · MUK / Elektronische Musik · 21.10.2026`;
    document.getElementById('print-guide').title = `Alle 20 Schritte für ${label} drucken`;
    if (updateURL) {
      const url = new URL(location.href);
      url.searchParams.set('daw', daw);
      history.replaceState(null, '', url);
    }
  }
  function updateProgress() {
    all('[data-complete]').forEach(input => { input.checked = done.has(input.dataset.complete); });
    all('.operation-link').forEach(link => link.classList.toggle('done', done.has(link.hash.slice(1))));
    document.getElementById('progress-label').textContent = `${done.size} / ${operationIds.length}`;
    document.getElementById('progress-fill').style.width = `${done.size / operationIds.length * 100}%`;
    document.querySelector('[role="progressbar"]').setAttribute('aria-valuenow', String(done.size));
    save('daw-basics-progress-v1', JSON.stringify([...done]));
  }
  function showRoute(id, scroll = false, focus = false) {
    current = routes.includes(id) ? id : operationIds[0];
    all('.operation, .page-view').forEach(el => { el.hidden = el.id !== current; });
    all('.operation-link').forEach(link => {
      if (link.hash.slice(1) === current) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
    all('.nav-extras a').forEach(link => {
      if (link.hash.slice(1) === current) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    document.getElementById('step-select').value = current;
    const target = document.getElementById(current);
    const title = target.querySelector('h2');
    document.title = `${title.textContent} · DAW Basics · MUK`;
    if (scroll) target.scrollIntoView({behavior: 'instant', block: 'start'});
    if (focus) { title.tabIndex = -1; title.focus({preventScroll: true}); }
  }
  function navigate(id, shouldFocus = false) {
    if (!routes.includes(id)) return;
    if (location.hash !== `#${id}`) history.pushState(null, '', `?daw=${daw}#${id}`);
    showRoute(id, true, shouldFocus);
  }
  document.addEventListener('click', async event => {
    const button = event.target.closest('.daw-button, .daw-tab');
    if (button) { updateDaw(button.dataset.daw); return; }
    const anchor = event.target.closest('a[href]');
    if (anchor?.classList.contains('skip')) {
      event.preventDefault();
      showRoute(current, true, true);
      return;
    }
    if (anchor && !event.metaKey && !event.ctrlKey && !event.shiftKey && event.button === 0) {
      const url = new URL(anchor.href, location.href);
      if (url.origin === location.origin && url.pathname === location.pathname) {
        if (routes.includes(url.hash.slice(1))) {
          event.preventDefault();
          if (url.searchParams.has('daw')) updateDaw(url.searchParams.get('daw'));
          navigate(url.hash.slice(1), event.detail === 0);
        } else if (anchor.getAttribute('href') === '#') {
          event.preventDefault();
          history.pushState(null, '', `?daw=${daw}`);
          showRoute(operationIds[0]);
          window.scrollTo({top: 0, behavior: 'instant'});
        }
      }
    }
    const share = event.target.closest('[data-share]');
    if (share) {
      const url = new URL(location.href);
      url.hash = share.dataset.share;
      url.searchParams.set('daw', daw);
      try { await navigator.clipboard.writeText(url.href); notice('Link zu diesem Schritt und deiner DAW kopiert.'); }
      catch { window.prompt('Schritt-Link kopieren:', url.href); }
    }
  });
  all('.daw-tabs').forEach(list => list.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let i = dawIds.indexOf(daw);
    if (event.key === 'Home') i = 0;
    else if (event.key === 'End') i = dawIds.length - 1;
    else i = (i + (event.key === 'ArrowRight' ? 1 : -1) + dawIds.length) % dawIds.length;
    updateDaw(dawIds[i]);
    list.querySelector(`[data-daw="${daw}"]`).focus();
  }));
  document.addEventListener('change', event => {
    if (event.target.matches('.compare-toggle')) { compare = event.target.checked; updateDaw(daw, false); }
    if (event.target.matches('[data-complete]')) {
      const id = event.target.dataset.complete;
      if (event.target.checked) done.add(id); else done.delete(id);
      updateProgress();
    }
  });
  document.getElementById('step-select').addEventListener('change', event => navigate(event.target.value));
  document.getElementById('print-guide').addEventListener('click', () => window.print());
  document.getElementById('reset-progress').addEventListener('click', () => {
    if (!done.size) { notice('Es sind noch keine Schritte abgehakt.'); return; }
    if (window.confirm('Alle Häkchen in diesem Browser zurücksetzen?')) { done.clear(); updateProgress(); notice('Häkchen zurückgesetzt.'); }
  });
  document.getElementById('operation-search').addEventListener('input', event => {
    const term = event.target.value.trim().toLocaleLowerCase('de');
    let matches = 0;
    all('.operation-link').forEach(link => {
      link.hidden = !link.dataset.search.toLocaleLowerCase('de').includes(term);
      if (!link.hidden) matches++;
    });
    all('.nav-group').forEach(group => { group.hidden = ![...group.querySelectorAll('.operation-link')].some(a => !a.hidden); });
    document.getElementById('search-empty').hidden = matches > 0;
  });
  function onHistory() {
    const id = new URLSearchParams(location.search).get('daw');
    if (dawIds.includes(id)) updateDaw(id, false);
    if (!location.hash) { showRoute(operationIds[0]); window.scrollTo({top: 0, behavior: 'instant'}); }
    else if (routes.includes(location.hash.slice(1))) showRoute(location.hash.slice(1), true);
  }
  window.addEventListener('popstate', onHistory);
  window.addEventListener('hashchange', onHistory);
  updateDaw(daw, false);
  updateProgress();
  showRoute(location.hash.slice(1));
  document.documentElement.classList.replace('no-js', 'js-ready');
  if (routes.includes(location.hash.slice(1))) requestAnimationFrame(() => showRoute(location.hash.slice(1), true));
})();
