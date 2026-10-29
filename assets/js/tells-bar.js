// The Blowhorn Tells announcement bar (layouts/_partials/tells-bar.html).
// Shows the close button, and on Dismiss hides the bar and remembers that in
// localStorage under the bar's data-key; tells-bar-head.html reads the same
// key before first paint on the next page. Focus moves to the header's home
// link so a keyboard reader is not left on a removed button.
(function () {
  var bar = document.querySelector('[data-tells-bar]');
  if (!bar) return;
  var close = bar.querySelector('.tells-bar-close');
  var key = bar.getAttribute('data-key');
  if (!close || !key) return;
  close.hidden = false;
  close.addEventListener('click', function () {
    try {
      window.localStorage.setItem(key, 'dismissed');
    } catch (e) { /* storage blocked: hidden for this page only, shown again on the next */ }
    document.documentElement.setAttribute('data-tells-bar', 'off');
    var home = document.querySelector('.site-header .brand');
    if (home) home.focus();
  });
})();
