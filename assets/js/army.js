// Blowhorn's army (home #how), chain of command. Pick who gives the order;
// Major Blowhorn yells at them, then hands the order to exactly one computer.
// Enlist or discharge computers (1 to 8). The rotation runs only while the section
// is in view, stops for good on first interaction and never runs under
// reduced motion; the bubble is announced only after the visitor acts.
(function () {
  var root = document.querySelector('.army');
  if (!root) return;
  var board = root.querySelector('.army-board');
  var wires = root.querySelector('.army-wires');
  var srcs = Array.prototype.slice.call(root.querySelectorAll('.army-src'));
  var major = root.querySelector('.army-major img');
  var yell = root.querySelector('.army-yell');
  var yellText = yell.querySelector('.bubble-text') || yell;
  var macs = root.querySelector('.army-macs');
  var note = root.querySelector('.army-fleet-note');
  var plats = root.querySelectorAll('.army-plats img');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Soldier art per slot, in the cast slot order (marketing/cast/README.md).
  var soldiers = (macs.getAttribute('data-soldiers') || '').split(' ').filter(Boolean);
  // Unit sizes: one combined count of computers plus amplifying profiles.
  function unit(n) {
    return n <= 1 ? 'recruit' : n <= 4 ? 'fireteam' : n <= 12 ? 'squad' : n <= 40 ? 'platoon' : n <= 150 ? 'company' : n <= 1000 ? 'battalion' : 'brigade';
  }
  function strength(n) {
    return n + (n === 1 ? ' computer enlisted, a lone recruit.' : ' computers enlisted, a ' + unit(n) + '.') + ' Each order goes to exactly one.';
  }
  var halted = false;
  var count = 3, job = 0, cur = 0, timer = null, visible = false, touched = false, run = 0;

  function shout(line) {
    yellText.textContent = line;
    yell.classList.remove('is-shout'); void yell.offsetWidth; yell.classList.add('is-shout');
  }
  function center(el) {
    var b = board.getBoundingClientRect(), r = el.getBoundingClientRect();
    return [r.left - b.left + r.width / 2, r.top - b.top + r.height / 2];
  }
  function curve(a, b) {
    var my = (a[1] + b[1]) / 2;
    return 'M' + a[0] + ',' + a[1] + ' C' + a[0] + ',' + my + ' ' + b[0] + ',' + my + ' ' + b[0] + ',' + b[1];
  }
  function wire() {
    // innerHTML on an <svg> element parses its children as SVG.
    var m = center(major), h = '';
    srcs.forEach(function (s, i) { h += '<path id="army-w-s' + i + '" d="' + curve(center(s), m) + '"/>'; });
    macs.querySelectorAll('.army-mac').forEach(function (x, i) { h += '<path id="army-w-m' + i + '" d="' + curve(m, center(x)) + '"/>'; });
    wires.innerHTML = h + '<circle class="army-packet" r="8" cx="-99" cy="-99"/>';
  }
  function fly(id, ms, token) {
    return new Promise(function (done) {
      var p = document.getElementById(id), pk = wires.querySelector('.army-packet');
      if (!p || !pk) return done();
      p.classList.add('is-live');
      if (reduce) return done();
      var L = p.getTotalLength(), t0 = performance.now();
      pk.classList.add('is-flying');
      (function step(t) {
        if (token !== run) return done();
        var k = Math.min(1, (t - t0) / ms), pt = p.getPointAtLength(L * k);
        pk.setAttribute('cx', pt.x); pk.setAttribute('cy', pt.y);
        if (k < 1) requestAnimationFrame(step); else { pk.classList.remove('is-flying'); done(); }
      })(t0);
    });
  }
  function drawMacs(claim, added) {
    if (halted) claim = -1;
    var fallback = macs.querySelector('.army-mac .soldier'), html = '';
    for (var m = 0; m < count; m++) {
      var src = soldiers.length ? soldiers[m % soldiers.length] : fallback.getAttribute('src');
      html += '<li class="army-mac' + (m === claim ? ' is-on' : '') + (added && m === count - 1 ? ' is-new' : '') + '"><img class="soldier" src="' + src + '" alt="" width="44" height="44">' +
        '<span class="army-mac-name">Computer ' + (m + 1) + '</span><span class="army-mac-tag">' + (halted ? 'halted' : m === claim ? 'on it' : 'standing by') + '</span></li>';
    }
    macs.innerHTML = html;
    wire();
  }
  function order(i) {
    var token = ++run, s = srcs[i];
    cur = i;
    srcs.forEach(function (x, j) {
      x.setAttribute('aria-pressed', j === i);
      document.getElementById(x.getAttribute('aria-controls')).hidden = j !== i;
    });
    wires.querySelectorAll('path').forEach(function (p) { p.classList.remove('is-live'); });
    drawMacs(-1);
    shout(s.dataset.line);
    fly('army-w-s' + i, 700, token).then(function () {
      if (token !== run) return;
      var k = job++ % count;
      return new Promise(function (r) { setTimeout(r, reduce ? 0 : 900); }).then(function () {
        if (token !== run) return;
        shout('"' + s.dataset.order + '." Computer ' + (k + 1) + ', that one\'s yours. Everyone else, as you were.');
        return fly('army-w-m' + k, 800, token).then(function () {
          if (token !== run) return;
          drawMacs(k);
          document.getElementById('army-w-m' + k).classList.add('is-live');
          plats.forEach(function (im) { im.classList.remove('is-hit'); void im.offsetWidth; im.classList.add('is-hit'); });
        });
      });
    });
  }
  function stop() {
    touched = true; clearInterval(timer); timer = null;
    yell.setAttribute('aria-live', 'polite');
  }
  function auto() {
    if (reduce || touched || halted || timer || !visible) return;
    timer = setInterval(function () { order((cur + 1) % srcs.length); }, 6500);
  }
  function say(line) { stop(); run++; shout(line); }

  srcs.forEach(function (s, i) {
    s.addEventListener('click', function () {
      stop();
      if (halted) { shout("We're halted, Commander. Your orders wait until you say resume."); return; }
      order(i);
    });
  });
  root.querySelector('[data-army="enlist"]').addEventListener('click', function () {
    if (count >= 8) { say("Eight computers. That's a squad, not a hobby. Carry on."); return; }
    var was = unit(count);
    count++; drawMacs(-1, true);
    say(unit(count) !== was
      ? 'Computer ' + count + ', fall in. ' + count + ' computers make a ' + unit(count) + ' now. One order, one computer per job.'
      : 'Computer ' + count + ', welcome to the reserves. One order, one computer per job. Coordinated so the same post isn\'t sent from two computers.');
    note.textContent = strength(count);
  });
  root.querySelector('[data-army="discharge"]').addEventListener('click', function () {
    if (count <= 1) { say('One computer is the minimum. I need someone to yell at.'); return; }
    count--; drawMacs(-1);
    say('Computer ' + (count + 1) + ', honorably discharged. The queue carries on without you.');
    note.textContent = strength(count);
  });
  // Commander in Chief: halt freezes the whole army (schedule pause --all).
  var haltBtn = root.querySelector('[data-army="halt"]');
  haltBtn.addEventListener('click', function () {
    stop(); run++;
    halted = !halted;
    board.classList.toggle('is-halted', halted);
    haltBtn.setAttribute('aria-pressed', halted);
    haltBtn.querySelector('.army-halt-text').textContent = halted ? 'Resume' : 'Halt';
    root.querySelector('[data-army-cmd="halt"]').hidden = halted;
    root.querySelector('[data-army-cmd="resume"]').hidden = !halted;
    drawMacs(-1);
    shout(halted
      ? 'Commander says halt, the whole army halts. No questions. A post already in flight finishes first. Nothing else moves.'
      : 'Commander says resume. Anything that fell due runs once, not once per missed slot. Carry on.');
  });
  root.addEventListener('focusin', function () { clearInterval(timer); timer = null; });
  root.addEventListener('pointerenter', function () { clearInterval(timer); timer = null; });
  root.addEventListener('pointerleave', auto);
  if ('ResizeObserver' in window) new ResizeObserver(wire).observe(board); else window.addEventListener('resize', wire);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      visible = es[0].isIntersecting;
      if (visible) auto(); else { clearInterval(timer); timer = null; }
    }, { threshold: 0.35 }).observe(root);
  }
  root.classList.add('is-ready');
  wire();
})();
