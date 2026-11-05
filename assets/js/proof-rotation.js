/* Rotating social proof, solutions pages only (layouts/solution.html).
   One testimonial at a time: auto-advance every 8 seconds, pause on
   hover or focus, never auto-advance under prefers-reduced-motion.
   Previous/Next still work by hand in that case. With no JavaScript,
   the first quote stays visible and the nav stays hidden. */
(function () {
  "use strict";
  document.querySelectorAll("[data-proof-rotate]").forEach(function (root) {
    var items = root.querySelectorAll(".proof-rotate-item");
    if (items.length < 2) return;
    var current = 0;
    var timer = null;
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function show(index) {
      items[current].classList.remove("is-current");
      items[current].setAttribute("aria-hidden", "true");
      current = (index + items.length) % items.length;
      items[current].classList.add("is-current");
      items[current].removeAttribute("aria-hidden");
    }
    function stop() {
      if (timer) { clearInterval(timer); timer = null; }
    }
    function start() {
      if (reduced || timer) return;
      timer = setInterval(function () { show(current + 1); }, 8000);
    }

    root.classList.add("is-rotating");
    var prev = root.querySelector("[data-proof-prev]");
    var next = root.querySelector("[data-proof-next]");
    if (prev) prev.addEventListener("click", function () { stop(); show(current - 1); start(); });
    if (next) next.addEventListener("click", function () { stop(); show(current + 1); start(); });
    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", start);
    start();
  });
})();
