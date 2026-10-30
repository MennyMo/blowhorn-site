// Cookie notice and Google Consent Mode v2 (layouts/_partials/consent.html,
// layouts/_partials/analytics.html). The head has already queued
// consent 'default' (everything denied), 'js' and 'config'. This script asks
// once, remembers the answer in localStorage, and loads gtag.js only after
// the reader accepts. No third-party library.
(function () {
  var KEY = 'blowhorn-consent';
  var self = document.currentScript;
  var id = self && self.getAttribute('data-ga-id');
  var notice = document.getElementById('consent');
  var opener = null;
  var loaded = false;

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function remember(value) {
    try { localStorage.setItem(KEY, value); } catch (e) { /* private mode: ask again next visit */ }
  }

  function load() {
    if (loaded || !id) return;
    loaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    document.head.appendChild(s);
  }

  function grant() {
    window.gtag('consent', 'update', { analytics_storage: 'granted' });
    load();
    // assets/js/docs-attribution.js starts its events from here.
    document.dispatchEvent(new CustomEvent('blowhorn:consent', { detail: 'granted' }));
  }

  function deny() {
    window.gtag('consent', 'update', { analytics_storage: 'denied' });
  }

  function hide() {
    if (!notice) return;
    notice.hidden = true;
    if (opener) { opener.focus(); opener = null; }
  }

  function show(from) {
    if (!notice) return;
    opener = from || null;
    notice.hidden = false;
    if (from) notice.querySelector('.consent-button').focus();
  }

  function choose(value) {
    var was = stored();
    remember(value);
    if (value === 'granted') grant();
    else {
      deny();
      // gtag.js can't be unloaded; a reload drops it after a withdrawal.
      if (was === 'granted' && loaded) { window.location.reload(); return; }
    }
    hide();
  }

  if (typeof window.gtag !== 'function') return;

  if (stored() === 'granted') grant();

  if (notice) {
    notice.addEventListener('click', function (event) {
      var target = event.target.closest('[data-consent]');
      if (target) choose(target.getAttribute('data-consent'));
    });
    notice.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') choose('denied');
    });
  }

  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-consent-open]');
    if (target) { event.preventDefault(); show(target); }
  });

  if (!stored()) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () { notice = document.getElementById('consent'); show(); });
    } else {
      show();
    }
  }
})();
