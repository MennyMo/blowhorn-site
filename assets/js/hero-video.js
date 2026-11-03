// The Signal hero film (layouts/_partials/hero-video.html, data/hero.json
// media.video, placement inline-expand). It sits small beside the hero copy
// on its poster with a Play the film button. A click grows the frame in one
// FLIP motion from its spot to 90% of the window width (full width on small
// screens), centered and fitted to the window height, as a modal dialog over
// a dimmed backdrop, then plays it: with sound when playback.sound is true
// (the click is the user gesture browsers need for audio). Escape, the
// backdrop or Close pauses it and shrinks it back to exactly its spot, and
// focus returns to the Play button. While open, focus is trapped in the
// dialog and the page does not scroll. Under prefers-reduced-motion it opens
// and closes without the motion. Without JavaScript the native controls stay.
(function () {
  var fig = document.querySelector('[data-hero-film]');
  if (!fig || fig.offsetParent === null) return;
  var frame = fig.querySelector('[data-film="frame"]');
  var video = frame.querySelector('video');
  var q = function (n) { return frame.querySelector('[data-film="' + n + '"]'); };
  var start = q('start'), startLabel = q('start-label'), bar = q('bar'), closeBtn = q('close');
  var sound = q('sound'), soundLabel = q('sound-label');
  var pause = q('pause'), pauseLabel = q('pause-label');
  var cfg = fig.dataset;
  var withSound = cfg.sound === 'true';
  var root = document.documentElement;
  var open = false, busy = false, backdrop = null, unlocked = false;

  function reduced() {
    try { return window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
  }

  video.removeAttribute('controls');
  // The poster stands in (frame background) while the video primes.
  function posterUp() { frame.style.setProperty('--hero-film-poster', 'url("' + video.poster + '")'); }
  posterUp();
  video.loop = cfg.loop === 'true';
  video.muted = !withSound;
  start.hidden = false;
  fig.classList.add('is-waiting');

  function sync() {
    sound.setAttribute('aria-pressed', String(!video.muted));
    soundLabel.textContent = video.muted ? 'Sound on' : 'Sound off';
    frame.classList.toggle('is-sound', !video.muted);
    pause.setAttribute('aria-pressed', String(video.paused));
    pauseLabel.textContent = video.paused ? 'Play' : 'Pause';
    frame.classList.toggle('is-paused', video.paused);
  }
  function playing(on, label) {
    start.hidden = on;
    bar.hidden = !on;
    if (label) startLabel.textContent = label;
    fig.classList.toggle('is-waiting', !on);
    frame.classList.toggle('is-waiting', !on);
  }
  function play() {
    var p = video.play();
    if (p && p.catch) p.catch(function () { playing(false, 'Play the film'); });
  }

  // The expanded rect: 90% of the window width (all of it on small
  // screens), 16:9, no taller than the window, centered.
  function target() {
    var vw = root.clientWidth, vh = window.innerHeight;
    var small = vw <= 640;
    var w = small ? vw : vw * 0.9;
    var h = w * 9 / 16, maxH = vh - (small ? 0 : 48);
    if (h > maxH) { h = maxH; w = h * 16 / 9; }
    return { left: (vw - w) / 2, top: (vh - h) / 2, width: w, height: h };
  }
  function place(r) {
    frame.style.left = r.left + 'px';
    frame.style.top = r.top + 'px';
    frame.style.width = r.width + 'px';
    frame.style.height = r.height + 'px';
  }
  // Transform that draws the frame (laid out at rect to) over rect from.
  // Per-axis scale: the inline frame is taller than 16:9 (it stretches to
  // the hero copy's height), the expanded frame is 16:9.
  function invert(from, to) {
    return 'translate(' + (from.left - to.left) + 'px,' + (from.top - to.top) + 'px) scale(' + (from.width / to.width) + ',' + (from.height / to.height) + ')';
  }
  function animate(fromT, toT, done) {
    if (reduced()) { frame.style.transform = toT; done(); return; }
    frame.classList.remove('is-moving');
    frame.style.transform = fromT;
    frame.getBoundingClientRect();
    frame.classList.add('is-moving');
    frame.style.transform = toT;
    var finished = false;
    function end(e) {
      if (finished || (e && (e.target !== frame || e.propertyName !== 'transform'))) return;
      finished = true;
      frame.removeEventListener('transitionend', end);
      frame.classList.remove('is-moving');
      done();
    }
    frame.addEventListener('transitionend', end);
    setTimeout(end, 900);
  }

  function lockScroll(on) {
    if (on) {
      var gap = window.innerWidth - root.clientWidth;
      root.classList.add('hero-film-locked');
      if (gap > 0) document.body.style.paddingRight = gap + 'px';
    } else {
      root.classList.remove('hero-film-locked');
      document.body.style.paddingRight = '';
    }
  }

  function openFilm() {
    if (open || busy) return;
    busy = true;
    var from = frame.getBoundingClientRect();
    fig.style.height = from.height + 'px';
    backdrop = document.createElement('div');
    backdrop.className = 'hero-film-backdrop';
    backdrop.addEventListener('click', closeFilm);
    document.body.appendChild(backdrop);
    document.body.appendChild(frame);
    frame.setAttribute('role', 'dialog');
    frame.setAttribute('aria-modal', 'true');
    frame.setAttribute('aria-labelledby', 'hero-art-title');
    frame.classList.add('is-open');
    lockScroll(true);
    var to = target();
    place(to);
    closeBtn.hidden = false;
    start.hidden = true;
    open = true;
    if (withSound) video.muted = false;
    frame.classList.add('is-priming');
    // Start it inside the click so browsers count the gesture for sound,
    // then hold it until the frame has grown.
    if (!unlocked) {
      var p = video.play();
      if (p && p.then) p.then(function () { unlocked = true; if (busy) video.pause(); }, function () {});
    }
    backdrop.getBoundingClientRect();
    backdrop.classList.add('is-on');
    animate(invert(from, to), 'none', function () {
      busy = false;
      frame.classList.remove('is-priming');
      if (video.ended || (!video.loop && video.currentTime >= video.duration)) video.currentTime = 0;
      playing(true);
      play();
      sync();
      closeBtn.focus();
    });
  }

  function closeFilm() {
    if (!open || busy) return;
    busy = true;
    video.pause();
    var to = frame.getBoundingClientRect();
    var home = fig.getBoundingClientRect();
    backdrop.classList.remove('is-on');
    closeBtn.hidden = true;
    animate('none', invert(home, to), function () {
      fig.appendChild(frame);
      frame.classList.remove('is-open');
      frame.removeAttribute('role');
      frame.removeAttribute('aria-modal');
      frame.removeAttribute('aria-labelledby');
      frame.style.cssText = '';
      posterUp();
      fig.style.height = '';
      if (backdrop) backdrop.remove();
      backdrop = null;
      lockScroll(false);
      open = false;
      busy = false;
      playing(false, video.currentTime > 0 && !video.ended ? 'Resume the film' : 'Play the film');
      start.focus();
    });
  }

  start.addEventListener('click', function () {
    if (!open) { openFilm(); return; }
    video.currentTime = 0;
    playing(true);
    play();
    closeBtn.focus();
  });
  closeBtn.addEventListener('click', closeFilm);
  sound.addEventListener('click', function () { video.muted = !video.muted; sync(); });
  pause.addEventListener('click', function () {
    if (video.paused) play(); else video.pause();
    sync();
  });
  video.addEventListener('click', function () {
    if (!open || busy) return;
    if (video.paused) play(); else video.pause();
  });
  video.addEventListener('ended', function () {
    if (video.loop || !open) return;
    if (cfg.end === 'poster') video.load();
    playing(false, 'Watch again');
    start.focus();
  });
  ['play', 'pause', 'volumechange'].forEach(function (ev) { video.addEventListener(ev, sync); });

  // Capture phase, so Escape closes only the film, not the cookie notice too.
  window.addEventListener('keydown', function (e) {
    if (!open) return;
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); closeFilm(); return; }
    if (e.key !== 'Tab') return;
    var items = [].filter.call(frame.querySelectorAll('button'), function (b) { return !b.hidden && b.offsetParent !== null; });
    if (!items.length) { e.preventDefault(); return; }
    var first = items[0], last = items[items.length - 1];
    if (!frame.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
    else if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }, true);
  window.addEventListener('resize', function () { if (open && !busy) place(target()); });
  sync();
})();
