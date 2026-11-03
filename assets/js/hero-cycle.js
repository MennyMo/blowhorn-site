/* Home hero review: type the letters c-y-c-l-e, in order, to move to
   the next hero in place. No modifier key, and no typing inside a
   form field, a text box, or an editable area counts: those keys are
   left alone. Letters must arrive within 2 seconds of each other, or
   the sequence resets. The hero order is the one the pre-paint picker
   exposed as window.blowhornHeroes; without it, the order falls back
   to the data-hero-only spans on the page. The URL is updated in
   place (?hero=<id>), so a reload or a shared link shows the same
   hero, and the existing picker then handles its art and media. */
(function () {
  "use strict";
  var SEQUENCE = "cycle";
  var TIMEOUT_MS = 2000;
  var progress = 0;
  var timer = null;

  function heroIds() {
    if (window.blowhornHeroes && window.blowhornHeroes.length) {
      return window.blowhornHeroes;
    }
    var seen = {};
    var ids = [];
    document.querySelectorAll("[data-hero-only]").forEach(function (el) {
      var id = el.getAttribute("data-hero-only");
      if (id && !seen[id]) { seen[id] = true; ids.push({ id: id }); }
    });
    return ids;
  }

  function cycleHero() {
    var heroes = heroIds();
    if (heroes.length < 2) return;
    var current = document.documentElement.getAttribute("data-hero");
    var index = -1;
    heroes.forEach(function (hero, i) {
      if (hero.id === current) index = i;
    });
    var next = heroes[(index + 1) % heroes.length];
    document.documentElement.setAttribute("data-hero", next.id);
    if (next.art) document.documentElement.setAttribute("data-hero-art", next.art);
    if (next.media) document.documentElement.setAttribute("data-hero-media", next.media);
    try {
      var url = new URL(window.location.href);
      url.searchParams.set("hero", next.id);
      window.history.replaceState(null, "", url.toString());
    } catch (e) {}
  }

  function reset() {
    progress = 0;
    if (timer) { clearTimeout(timer); timer = null; }
  }

  document.addEventListener("keydown", function (event) {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    var target = event.target;
    if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.tagName === "SELECT" || target.isContentEditable)) return;
    if (!event.key || event.key.length !== 1) { reset(); return; }
    var key = event.key.toLowerCase();
    if (key === SEQUENCE[progress]) {
      progress += 1;
    } else if (key === SEQUENCE[0]) {
      progress = 1;
    } else {
      reset();
      return;
    }
    if (timer) clearTimeout(timer);
    if (progress >= SEQUENCE.length) {
      reset();
      cycleHero();
      return;
    }
    timer = setTimeout(reset, TIMEOUT_MS);
  });
})();
