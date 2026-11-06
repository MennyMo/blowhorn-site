/* Platform product pages (layouts/platform-page.html, docs/platform-pages.md).

   Without this file the page is complete: every activity type's intent is listed,
   the first type's illustration shows, the playground shows its first starter
   draft as a static preview (its controls stay hidden), the action matrix is a
   plain table and the setups rail is a native scroll area. With it (.is-enhanced
   on the page):

   - The activity type radios ([data-pp-choice]) swap every [data-pp-for] element
     (the illustration, the intent, the playground's preview title and post-only
     controls, the Activities illustration) and mark the matrix rows bound to the
     type ([data-pp-row]); no row is hidden. The change is announced in
     [data-pp-announce].
   - The playground ([data-pp-try]) is local only. The draft ([data-pp-try-text])
     is mirrored into the preview as text, never markup; a starter
     ([data-pp-try-starter]) selects its type and fills the draft; the counter
     ([data-pp-try-count]) shows the length against data-max and flags a thread
     past it; an image picked from the visitor's own computer
     ([data-pp-try-file]) is shown through an object URL that is released when it
     is removed or replaced. There is no form, and nothing here makes a request,
     reads storage or cookies, or talks to the extension.
   - The rail ([data-pp-rail]) gets previous and next buttons that page it by hand,
     never on a timer, and a count of the items in view (plain text; only a
     button press is announced, once, in [data-pp-rail-announce]). The buttons use
     aria-disabled, never disabled, so a focused button keeps focus at either end.

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
    if (!choices.length) return null;
    var announce = root.querySelector("[data-pp-announce]");

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

    /* Selecting a different radio (pointer, arrow keys or assistive technology)
       fires change. Clicking the radio that is already checked fires no change
       and needs nothing: the page already shows that type. */
    choices.forEach(function (input) {
      input.addEventListener("change", function () {
        if (!input.checked) return;
        select(input.value, intentOf(input.value));
      });
    });

    var initial = "";
    choices.forEach(function (input) { if (input.checked) initial = input.value; });
    select(initial || choices[0].value, "");
    root.classList.add("is-enhanced");
    return select;
  }

  function enhancePlayground(root, select) {
    var box = root.querySelector("[data-pp-try]");
    if (!box) return;
    var controls = box.querySelector("[data-pp-try-controls]");
    var text = box.querySelector("[data-pp-try-text]");
    var out = box.querySelector("[data-pp-try-out]");
    if (!controls || !text || !out) return;
    var count = box.querySelector("[data-pp-try-count]");
    var thread = box.querySelector("[data-pp-try-thread]");
    var file = box.querySelector("[data-pp-try-file]");
    var clear = box.querySelector("[data-pp-try-clear]");
    var media = box.querySelector("[data-pp-try-img]");
    var announce = box.querySelector("[data-pp-try-announce]");
    var postBox = box.querySelector("[data-pp-try-post]");
    var max = count ? parseInt(count.getAttribute("data-max"), 10) || 0 : 0;
    var over = false;
    var url = "";

    function say(message) {
      if (announce) announce.textContent = message;
    }

    /* The counter, the thread flag and the image belong to the post type: they
       sit in postBox, which the type selector hides for the others. */
    function postActive() {
      return !!postBox && !postBox.hidden;
    }

    /* The preview mirrors the draft as text, so nothing typed is ever markup.
       The counter is plain text, described to the draft only while it is shown;
       only crossing the thread length is announced, once each way, and only for
       the post type. */
    function render() {
      var value = text.value;
      out.textContent = value;
      if (!count) return;
      if (postActive()) text.setAttribute("aria-describedby", count.getAttribute("id"));
      else text.removeAttribute("aria-describedby");
      var n = Array.from(value).length;
      count.textContent = n + " / " + max;
      var now = postActive() && max > 0 && n > max;
      if (thread) thread.hidden = !now;
      if (now !== over) {
        over = now;
        if (now && thread) say(thread.textContent);
      }
      /* The thread message is about the post type only: off Post it must not be
         read as the current state of a reply. */
      if (!postActive() && thread && announce && announce.textContent === thread.textContent) say("");
    }

    function release() {
      if (url && window.URL && URL.revokeObjectURL) URL.revokeObjectURL(url);
      url = "";
    }

    function dropImage() {
      release();
      if (media) {
        media.textContent = "";
        media.hidden = true;
      }
      if (clear) clear.hidden = true;
    }

    text.addEventListener("input", render);
    /* A type change (after the selector's own handler has shown or hidden postBox)
       refreshes the description and the flag. */
    all(root, "[data-pp-choice]").forEach(function (input) {
      input.addEventListener("change", render);
    });

    all(box, "[data-pp-try-starter]").forEach(function (button) {
      button.addEventListener("click", function () {
        if (select) select(button.getAttribute("data-activity"), "");
        text.value = button.getAttribute("data-sample") || "";
        render();
        say(button.textContent + " is in your draft.");
      });
    });

    if (file && media && window.URL && URL.createObjectURL && document.createElement) {
      file.addEventListener("change", function () {
        var picked = file.files && file.files[0];
        dropImage();
        if (!picked) {
          file.value = "";
          return;
        }
        if (!/^image\//.test(picked.type || "")) {
          file.value = "";
          say(announce ? announce.getAttribute("data-not-image") || "" : "");
          return;
        }
        url = URL.createObjectURL(picked);
        var img = document.createElement("img");
        /* A format the browser cannot decode (HEIC, TIFF) must not leave a blank
           slot and a Remove button: drop it, clear the picker and say so. */
        img.addEventListener("error", function () {
          dropImage();
          file.value = "";
          say(announce ? announce.getAttribute("data-unreadable") || "" : "");
        });
        img.setAttribute("alt", "");
        img.setAttribute("src", url);
        media.appendChild(img);
        media.hidden = false;
        if (clear) clear.hidden = false;
      });
      if (clear) {
        clear.addEventListener("click", function () {
          dropImage();
          file.value = "";
          file.focus();
        });
      }
      /* A page kept in the back/forward cache comes back with its image, so only a
         page that is really going away releases the URL. */
      window.addEventListener("pagehide", function (event) {
        if (!event.persisted) release();
      });
    } else if (file) {
      /* No object URLs: hide the picker rather than offer something that fails. */
      var picker = file.closest ? file.closest("label") : null;
      if (picker) picker.hidden = true;
    }

    render();
    controls.hidden = false;
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
      if (announce) announce.textContent = "Showing " + describe(inView(left));
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
      var select = enhance(root);
      enhancePlayground(root, select);
      enhanceRail(root);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
