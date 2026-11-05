// Site header menus (layouts/_partials/header.html). Each group is a
// disclosure: a button with aria-expanded that shows its panel. Click, Enter or
// Space toggles; Escape closes and returns focus; leaving the group with Tab or
// a click elsewhere closes it. A mouse may also open a group by hovering. Below
// 1080px the Menu button opens the whole nav as a sheet and groups expand in
// place. Without this script the CSS opens panels on hover and focus instead.
(function () {
  var header = document.querySelector('.site-header');
  if (!header) return;
  var nav = header.querySelector('.site-nav');
  var toggle = header.querySelector('.mm-toggle');
  var items = Array.prototype.slice.call(header.querySelectorAll('.mm-item'));
  var groups = items.filter(function (li) { return li.querySelector('.mm-trigger'); });
  var wide = window.matchMedia('(min-width: 1080px)');
  var hover = window.matchMedia('(hover: hover) and (pointer: fine)');
  var openTimer = null, closeTimer = null;

  header.classList.add('is-enhanced');
  if (toggle) toggle.hidden = false;

  function trig(li) { return li.querySelector('.mm-trigger'); }
  function setOpen(li, open) {
    var t = trig(li);
    t.setAttribute('aria-expanded', open ? 'true' : 'false');
    li.classList.toggle('is-open', open);
  }
  function closeAll(except) {
    groups.forEach(function (li) { if (li !== except) setOpen(li, false); });
  }
  function isOpen(li) { return trig(li).getAttribute('aria-expanded') === 'true'; }
  // The sheet fills the screen below the header. Anything above the header
  // (the announcement bar, until it scrolls away) moves its bottom edge, so
  // measure it while the sheet is open instead of assuming --header-h.
  var sheetFrame = 0;
  function fitSheet() {
    sheetFrame = 0;
    header.style.setProperty('--sheet-top', Math.max(0, Math.round(header.getBoundingClientRect().bottom)) + 'px');
  }
  function onSheetScroll() {
    if (!sheetFrame) sheetFrame = window.requestAnimationFrame(fitSheet);
  }
  function setSheet(open) {
    if (!toggle) return;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    header.classList.toggle('is-menu-open', open);
    if (open) {
      fitSheet();
      window.addEventListener('scroll', onSheetScroll, { passive: true });
    } else {
      window.removeEventListener('scroll', onSheetScroll);
      closeAll();
    }
  }

  groups.forEach(function (li) {
    var t = trig(li);
    t.addEventListener('click', function () {
      var open = !isOpen(li);
      if (wide.matches) closeAll(li);
      setOpen(li, open);
    });
    li.addEventListener('pointerenter', function (e) {
      if (e.pointerType !== 'mouse' || !wide.matches || !hover.matches) return;
      clearTimeout(closeTimer);
      clearTimeout(openTimer);
      openTimer = setTimeout(function () { closeAll(li); setOpen(li, true); }, 90);
    });
    li.addEventListener('pointerleave', function (e) {
      if (e.pointerType !== 'mouse' || !wide.matches || !hover.matches) return;
      clearTimeout(openTimer);
      closeTimer = setTimeout(function () { setOpen(li, false); }, 220);
    });
    li.addEventListener('focusout', function (e) {
      if (wide.matches && !li.contains(e.relatedTarget)) setOpen(li, false);
    });
  });

  if (toggle) {
    toggle.addEventListener('click', function () {
      setSheet(toggle.getAttribute('aria-expanded') !== 'true');
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = groups.filter(isOpen)[0];
    if (open) { setOpen(open, false); trig(open).focus(); return; }
    if (toggle && toggle.getAttribute('aria-expanded') === 'true') { setSheet(false); toggle.focus(); }
  });
  document.addEventListener('click', function (e) {
    if (header.contains(e.target)) {
      // Following a link inside a panel or the sheet (an in-page anchor too) closes the menu.
      if (e.target.closest('.site-nav a')) { closeAll(); setSheet(false); }
      return;
    }
    closeAll();
    setSheet(false);
  });
  var onChange = function () { closeAll(); setSheet(false); };
  if (wide.addEventListener) wide.addEventListener('change', onChange); else wide.addListener(onChange);
})();
