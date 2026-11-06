/* Platform product pages (layouts/platform-page.html, docs/platform-pages.md).

   Without this file the page is complete: every activity type's intent is listed,
   the first type's illustration shows, the examples rail is a native scroll area
   and the breakdowns are native <details>. With it (.is-enhanced on the page):

   - The activity type radios ([data-pp-choice]) swap every [data-pp-for] element
     (the illustration, the intent, Start's context, the breakdown's "Your pick"
     marks and the Activities illustration) and mark the bound breakdown rows
     ([data-pp-row]). The change is announced in [data-pp-announce].
   - The rail ([data-pp-rail]) gets previous and next buttons that page it by hand,
     never on a timer, and a count of the examples in view (plain text; only a
     button press is announced, once, in [data-pp-rail-announce]). The buttons use
     aria-disabled, never disabled, so a focused button keeps focus at either end.
     The rail is still a native scroller, so a focused example scrolls into view.
   - Each example's "Preview above" button ([data-pp-try]) selects the example's
     type, puts its sample text in the illustration and moves focus there.

   No library and no request to another host. Motion is CSS; under reduced motion
   nothing here scrolls smoothly. Tested through platform_page_harness.js by
   check_platform_pages.py (make check-platform-pages) and test_platform_pages.py. */
(function () {
  "use strict";

  function all(root, sel) {
    return Array.prototype.slice.call(root.querySelectorAll(sel));
  }

  function reduced() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function enhance(root) {
    var choices = all(root, "[data-pp-choice]");
    if (!choices.length) return;
    var announce = root.querySelector("[data-pp-announce]");
    var stage = root.querySelector("[data-pp-stage]");

    function labelOf(id) {
      var label = "";
      choices.forEach(function (input) {
        if (input.value === id) label = input.getAttribute("data-label") || "";
      });
      return label;
    }

    function intentOf(id) {
      var text = "";
      all(root, "[data-pp-intent]").forEach(function (el) {
        if (el.getAttribute("data-pp-for") === id) text = el.textContent;
      });
      return text;
    }

    function select(id, say) {
      var known = choices.some(function (input) { return input.value === id; });
      if (!known) return;
      root.setAttribute("data-pp-type", id);
      choices.forEach(function (input) { input.checked = input.value === id; });
      all(root, "[data-pp-for]").forEach(function (el) {
        el.hidden = el.getAttribute("data-pp-for") !== id;
      });
      all(root, "[data-pp-row]").forEach(function (el) {
        el.classList.toggle("is-picked", el.getAttribute("data-pp-row") === id);
      });
      if (announce && say) announce.textContent = say;
    }

    /* Picking a type by hand returns every illustration to its own scene,
       whatever an example's preview put there. */
    function restoreScenes() {
      all(root, "[data-pp-sample]").forEach(function (slot) {
        slot.textContent = "";
        slot.hidden = true;
      });
      all(root, "[data-pp-original]").forEach(function (p) { p.hidden = false; });
    }

    choices.forEach(function (input) {
      input.addEventListener("change", function () {
        if (!input.checked) return;
        restoreScenes();
        select(input.value, intentOf(input.value));
      });
    });

    all(root, "[data-pp-try]").forEach(function (button) {
      button.hidden = false;
      button.addEventListener("click", function () {
        var card = null;
        all(root, "[data-pp-example]").forEach(function (el) {
          if (el.getAttribute("data-pp-example") === button.getAttribute("data-pp-try")) card = el;
        });
        if (!card) return;
        var type = card.getAttribute("data-activity");
        var sample = card.querySelector("[data-pp-sample-text]");
        var title = card.querySelector("[data-pp-example-title]");
        all(root, "[data-pp-scene-text]").forEach(function (box) {
          var mine = box.getAttribute("data-pp-scene-text") === type;
          var slot = box.querySelector("[data-pp-sample]");
          if (!slot) return;
          if (mine && sample) {
            slot.textContent = sample.textContent;
            slot.hidden = false;
          } else {
            slot.textContent = "";
            slot.hidden = true;
          }
          all(box, "[data-pp-original]").forEach(function (p) { p.hidden = mine && !!sample; });
        });
        select(type, (title ? title.textContent : "") + ", shown in the preview as " + labelOf(type) + ".");
        if (stage) {
          if (stage.scrollIntoView) stage.scrollIntoView({ behavior: reduced() ? "auto" : "smooth", block: "center" });
          stage.focus({ preventScroll: true });
        }
      });
    });

    var initial = "";
    choices.forEach(function (input) { if (input.checked) initial = input.value; });
    select(initial || choices[0].value, "");
    root.classList.add("is-enhanced");
  }

  function enhanceRail(root) {
    var rail = root.querySelector("[data-pp-rail]");
    var controls = root.querySelector("[data-pp-rail-controls]");
    var prev = root.querySelector("[data-pp-prev]");
    var next = root.querySelector("[data-pp-next]");
    var count = root.querySelector("[data-pp-rail-count]");
    var announce = root.querySelector("[data-pp-rail-announce]");
    if (!rail || !controls || !prev || !next) return;
    var slides = all(rail, "[data-pp-slide]");
    if (slides.length < 2) return;

    function origin() { return slides[0].offsetLeft; }

    /* A slide is in view when at least 60% of it is inside the scroller. */
    function inView(at) {
      var left = at === undefined ? rail.scrollLeft : at;
      var right = left + rail.clientWidth;
      var first = -1;
      var last = -1;
      slides.forEach(function (slide, i) {
        var start = slide.offsetLeft - origin();
        var end = start + slide.offsetWidth;
        var seen = Math.min(end, right) - Math.max(start, left);
        if (seen >= slide.offsetWidth * 0.6) {
          if (first < 0) first = i;
          last = i;
        }
      });
      if (first < 0) { first = 0; last = 0; }
      return { first: first, last: last };
    }

    function atStart() { return rail.scrollLeft <= 1; }
    function atEnd() { return rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 1; }

    function describe(v) {
      return (v.first === v.last ? String(v.first + 1) : (v.first + 1) + "-" + (v.last + 1)) + " of " + slides.length;
    }

    /* The count is plain text, kept current as the rail scrolls by any means. It
       is not a live region: a swipe would otherwise announce every frame. */
    function update() {
      var fits = rail.scrollWidth <= rail.clientWidth + 1;
      controls.hidden = fits;
      if (count) count.textContent = describe(inView());
      prev.setAttribute("aria-disabled", atStart() ? "true" : "false");
      next.setAttribute("aria-disabled", atEnd() ? "true" : "false");
    }

    /* A button press scrolls to a known place, so the new range is announced
       once, from where the rail will land, not from its scroll events. */
    function go(index) {
      var i = Math.max(0, Math.min(slides.length - 1, index));
      var max = Math.max(0, rail.scrollWidth - rail.clientWidth);
      var left = Math.min(max, slides[i].offsetLeft - origin());
      if (announce) announce.textContent = "Showing examples " + describe(inView(left));
      rail.scrollTo({ left: left, behavior: reduced() ? "auto" : "smooth" });
    }

    prev.addEventListener("click", function () {
      if (prev.getAttribute("aria-disabled") === "true") return;
      var v = inView();
      go(v.first - (v.last - v.first + 1));
    });
    next.addEventListener("click", function () {
      if (next.getAttribute("aria-disabled") === "true") return;
      go(inView().last + 1);
    });

    var pending = false;
    function schedule() {
      if (pending) return;
      pending = true;
      window.requestAnimationFrame(function () {
        pending = false;
        update();
      });
    }
    rail.addEventListener("scroll", schedule);
    window.addEventListener("resize", schedule);
    update();
  }

  function init() {
    all(document, "[data-platform-page]").forEach(function (root) {
      enhance(root);
      enhanceRail(root);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
