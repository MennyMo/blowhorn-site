/* Hero activity card. Pure helpers are exported for node:test.
   Items and the page envelope mirror EventFeedItem and EventFeedPage from
   meshery/schemas v1.3.116 (schemas/event_feed_page.schema.json).
   The feed URL is not in this file: the partial puts it in the card's
   data-feed-url from params.cloud_url, and boot turns it into the
   transport. With no URL the card shows the bundled examples. Live items
   stay in memory only until Cache-Control max-age, and never longer than
   30 seconds. They are not an offline fallback. This file does not
   persist anything. */
export const PLATFORMS = Object.freeze([
  "linkedin",
  "x",
  "reddit",
  "hacker-news",
  "slack",
  "bluesky",
  "github",
]);

export const LIMITS = Object.freeze({
  category: 500,
  action: 500,
  pageSize: 50,
  roleMin: 3,
  roleMax: 40,
  lineMin: 10,
  lineMax: 120,
  name: 80,
  organization: 255,
  network: 255,
  networks: 20,
  url: 500,
  profileUrl: 2048,
});

export const INTERVAL_MS = 7000;
export const SWAP_MS = 180;
export const MAX_LIVE_TTL_MS = 30000;
const RATE_LIMIT_FALLBACK_MS = 60000;
const HTTPS = "https:";
const DATE_TIME = /^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])[Tt]([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?([Zz]|[+-]([01][0-9]|2[0-3]):[0-5][0-9])$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const PLATFORM_SET = new Set(PLATFORMS);
const ITEM_KEYS = new Set([
  "id",
  "userId",
  "category",
  "action",
  "createdAt",
  "platform",
  "role",
  "line",
  "networks",
  "displayName",
  "avatarUrl",
  "organizationName",
  "publicProfileUrl",
  "visibility",
]);
const PAGE_KEYS = new Set(["page", "pageSize", "totalCount", "data", "example", "$schema"]);

const CONTROL = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g;

export function stripControls(value) {
  return String(value).replace(CONTROL, "").replace(/[\r\n\t]+/g, " ").replace(/ {2,}/g, " ").trim();
}

function fail(reason) {
  return { ok: false, reason };
}

export function isHttpsUrl(value, max = LIMITS.url) {
  if (typeof value !== "string") return false;
  const trimmed = value.trim();
  if (!trimmed || trimmed.length > max) return false;
  if (trimmed !== stripControls(trimmed)) return false;
  const lower = trimmed.toLowerCase();
  if (lower.startsWith("javascript:") || lower.startsWith("data:")) return false;
  let url;
  try {
    url = new URL(trimmed);
  } catch {
    return false;
  }
  return url.protocol === HTTPS && url.username === "" && url.password === "" && !!url.hostname;
}

function plain(value, min, max) {
  if (typeof value !== "string") return null;
  const text = stripControls(value);
  if (text.length < min || text.length > max) return null;
  if (text.includes("\u2014")) return null;
  return text;
}

export function validateItem(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return fail("type");
  for (const key of Object.keys(input)) {
    if (!ITEM_KEYS.has(key)) return fail("field");
  }
  const id = typeof input.id === "string" && UUID.test(input.id) ? input.id : null;
  const userId = typeof input.userId === "string" && UUID.test(input.userId) ? input.userId : null;
  const category = plain(input.category, 1, LIMITS.category);
  const action = plain(input.action, 1, LIMITS.action);
  const role = plain(input.role, LIMITS.roleMin, LIMITS.roleMax);
  const line = plain(input.line, LIMITS.lineMin, LIMITS.lineMax);
  if (!id || !userId || !category || !action || !role || !line) return fail("text");
  if (typeof input.platform !== "string" || !PLATFORM_SET.has(input.platform)) return fail("platform");
  if (input.visibility !== "public") return fail("visibility");
  if (typeof input.createdAt !== "string" || !DATE_TIME.test(input.createdAt)) return fail("createdAt");

  const item = {
    id,
    userId,
    category,
    action,
    platform: input.platform,
    role,
    line,
    createdAt: input.createdAt,
    visibility: "public",
    example: false,
  };

  if (input.networks !== undefined) {
    if (!Array.isArray(input.networks) || input.networks.length < 1 || input.networks.length > LIMITS.networks) {
      return fail("networks");
    }
    const networks = [];
    for (const entry of input.networks) {
      const name = plain(entry, 1, LIMITS.network);
      if (!name) return fail("networks");
      networks.push(name);
    }
    item.networks = networks;
  }

  if (input.displayName !== undefined) {
    const displayName = plain(input.displayName, 1, LIMITS.name);
    if (!displayName) return fail("displayName");
    item.displayName = displayName;
  }
  if (input.organizationName !== undefined) {
    const organizationName = plain(input.organizationName, 1, LIMITS.organization);
    if (!organizationName) return fail("organizationName");
    item.organizationName = organizationName;
  }
  if (input.avatarUrl !== undefined) {
    if (!isHttpsUrl(input.avatarUrl)) return fail("avatarUrl");
    item.avatarUrl = input.avatarUrl.trim();
  }
  if (input.publicProfileUrl !== undefined) {
    if (!isHttpsUrl(input.publicProfileUrl, LIMITS.profileUrl)) return fail("publicProfileUrl");
    item.publicProfileUrl = input.publicProfileUrl.trim();
  }
  return { ok: true, item };
}

export function sanitizeItem(input) {
  const result = validateItem(input);
  return result.ok ? result.item : null;
}

function isCount(value, min) {
  return Number.isInteger(value) && value >= min;
}

/* A page is valid when it is an EventFeedPage: page, pageSize and totalCount
   are integers in range and data is an array of at most pageSize items. The
   bundled examples carry `example: true` in place of the paging fields.
   An invalid page yields no items, so the caller falls back. */
export function normalizePayload(payload) {
  const empty = { items: [], example: false, dropped: 0, rawCount: 0, valid: false };
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return empty;
  for (const key of Object.keys(payload)) {
    if (!PAGE_KEYS.has(key)) return empty;
  }
  if (payload.example !== undefined && typeof payload.example !== "boolean") return empty;
  const example = payload.example === true;
  if (!Array.isArray(payload.data)) return empty;
  if (!example) {
    if (!isCount(payload.page, 0) || !isCount(payload.totalCount, 0)) return empty;
    if (!isCount(payload.pageSize, 1) || payload.pageSize > LIMITS.pageSize) return empty;
    if (payload.data.length > LIMITS.pageSize) return empty;
  }
  const items = [];
  let dropped = 0;
  for (const rawItem of payload.data) {
    const cleaned = sanitizeItem(rawItem);
    if (!cleaned) {
      dropped += 1;
      continue;
    }
    cleaned.example = example;
    items.push(cleaned);
  }
  return { items, example, dropped, rawCount: payload.data.length, valid: true };
}

export function parseMaxAge(header, capMs = MAX_LIVE_TTL_MS) {
  if (header == null) return 0;
  const match = /(?:^|,)\s*max-age\s*=\s*(\d+)/i.exec(String(header));
  if (!match) return 0;
  return Math.min(Number(match[1]) * 1000, capMs);
}

export function parseRetryAfter(header, nowMs) {
  if (header == null) return null;
  const trimmed = String(header).trim();
  if (!trimmed) return null;
  if (/^\d+$/.test(trimmed)) return nowMs + Number(trimmed) * 1000;
  const parsed = Date.parse(trimmed);
  if (Number.isNaN(parsed)) return null;
  return parsed;
}

function asPayload(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return { example: true, data: [] };
  return value;
}

export function createFeedSource(options = {}) {
  const fallback = asPayload(options.fallback);
  const timeoutMs = options.timeoutMs ?? 8000;
  const now = options.now ?? (() => Date.now());
  const setTimer = options.setTimer ?? ((fn, ms) => setTimeout(fn, ms));
  const clearTimer = options.clearTimer ?? ((id) => clearTimeout(id));
  const rateLimitFallbackMs = options.rateLimitFallbackMs ?? RATE_LIMIT_FALLBACK_MS;
  let retryNotBefore = 0;
  let memory = null;
  let timer = null;
  let epoch = 0;

  function exampleHold() {
    const normalized = normalizePayload(fallback);
    return { items: normalized.items, live: false, example: normalized.example, expiresAt: null };
  }

  function finishFallback(reason, replaceLive) {
    const normalized = normalizePayload(fallback);
    if (replaceLive) memory = exampleHold();
    return {
      items: normalized.items,
      example: normalized.example,
      reason,
      fromFallback: true,
      ttlMs: 0,
    };
  }

  function presentLive(hold) {
    return {
      items: hold.items,
      example: hold.example,
      reason: "live",
      fromFallback: false,
      ttlMs: Math.max(0, hold.expiresAt - now()),
    };
  }

  async function handleResponse(response, replaceLive) {
    const status = Number(response && response.status);
    if (status === 429) {
      const header = response.headers && response.headers.get ? response.headers.get("retry-after") : null;
      const until = parseRetryAfter(header, now());
      retryNotBefore = until == null ? now() + rateLimitFallbackMs : until;
      return finishFallback("rate-limit", replaceLive);
    }
    if (!status || status < 200 || status >= 300) return finishFallback("http", replaceLive);
    let payload;
    try {
      payload = await response.json();
    } catch {
      return finishFallback("malformed", replaceLive);
    }
    const normalized = normalizePayload(payload);
    if (!normalized.items.length) {
      return finishFallback(normalized.valid && normalized.rawCount === 0 ? "empty" : "invalid", replaceLive);
    }
    const liveItems = normalized.items.filter((item) => !item.example);
    const header = response.headers && response.headers.get ? response.headers.get("cache-control") : null;
    const ttlMs = liveItems.length ? parseMaxAge(header) : 0;
    if (!liveItems.length) {
      return {
        items: normalized.items,
        example: true,
        reason: "live",
        fromFallback: false,
        ttlMs: 0,
      };
    }
    if (ttlMs <= 0) return finishFallback("ttl", true);
    memory = {
      items: liveItems,
      live: true,
      example: false,
      expiresAt: now() + ttlMs,
    };
    return presentLive(memory);
  }

  function claimFresh() {
    if (!memory || !memory.live) return { fresh: null, expired: false };
    if (now() >= memory.expiresAt) {
      memory = null;
      return { fresh: null, expired: true };
    }
    return { fresh: memory, expired: false };
  }

  return {
    get memory() {
      return memory ? memory.items : null;
    },
    async load() {
      const gen = ++epoch;
      const claimed = claimFresh();
      if (claimed.fresh) return presentLive(claimed.fresh);
      const replaceLive = claimed.expired;
      const transport = Object.prototype.hasOwnProperty.call(options, "transport") ? options.transport : null;
      if (transport == null) return finishFallback("disabled", replaceLive);
      if (now() < retryNotBefore) return finishFallback("rate-limit", replaceLive);
      try {
        const response = await new Promise((resolve, reject) => {
          timer = setTimer(() => {
            const err = new Error("timeout");
            err.code = "TIMEOUT";
            reject(err);
          }, timeoutMs);
          Promise.resolve()
            .then(() => transport())
            .then(resolve, reject);
        });
        if (gen !== epoch) return finishFallback("destroyed", replaceLive);
        return await handleResponse(response, replaceLive);
      } catch (err) {
        if (gen !== epoch) return finishFallback("destroyed", replaceLive);
        if (err && err.code === "TIMEOUT") return finishFallback("timeout", replaceLive);
        return finishFallback("network", replaceLive);
      } finally {
        if (timer != null) {
          clearTimer(timer);
          timer = null;
        }
      }
    },
    destroy() {
      epoch += 1;
      if (timer != null) {
        clearTimer(timer);
        timer = null;
      }
    },
  };
}

export function createRotation(options = {}) {
  const count = options.count || 0;
  const intervalMs = options.intervalMs ?? INTERVAL_MS;
  const isReduced = options.isReduced ?? (() => false);
  const isHidden = options.isHidden ?? (() => false);
  const setTimer = options.setTimer ?? ((fn, ms) => setTimeout(fn, ms));
  const clearTimer = options.clearTimer ?? ((id) => clearTimeout(id));
  const onIndex = options.onIndex ?? (() => {});
  let index = 0;
  let timer = null;
  let hoverPaused = false;
  let hidePaused = false;
  let destroyed = false;

  function canRun() {
    return !destroyed && !hoverPaused && !hidePaused && !isReduced() && !isHidden() && count >= 2;
  }

  function clear() {
    if (timer != null) {
      clearTimer(timer);
      timer = null;
    }
  }

  function arm() {
    clear();
    if (!canRun()) return;
    timer = setTimer(() => {
      timer = null;
      index = (index + 1) % count;
      onIndex(index, { manual: false });
      arm();
    }, intervalMs);
  }

  function step(delta, manual) {
    if (count < 1) return index;
    index = (index + delta + count) % count;
    onIndex(index, { manual: !!manual });
    arm();
    return index;
  }

  return {
    start: arm,
    pause() {
      hoverPaused = true;
      clear();
    },
    resume() {
      hoverPaused = false;
      arm();
    },
    onVisibility() {
      hidePaused = isHidden();
      if (hidePaused) clear();
      else arm();
    },
    next() {
      return step(1, true);
    },
    prev() {
      return step(-1, true);
    },
    destroy() {
      destroyed = true;
      clear();
    },
    get index() {
      return index;
    },
    get armed() {
      return timer != null;
    },
  };
}

function slot(root, selector) {
  return root.querySelector(selector);
}

export function paintActivity(root, item, flags = {}) {
  const example = !!(flags.example || (item && item.example));
  const line = slot(root, "[data-activity-line]");
  const role = slot(root, "[data-activity-role]");
  const when = slot(root, "[data-activity-when]");
  const badge = slot(root, "[data-activity-examples]");
  const note = slot(root, "[data-activity-note]");
  if (line) line.textContent = item && item.line ? item.line : "";
  if (role) role.textContent = item && item.role ? item.role : "";
  if (when) when.textContent = example ? "Example activity" : (item && item.createdAt ? item.createdAt.slice(0, 10) : "");
  if (badge) badge.hidden = !example;
  if (note) note.hidden = !example;

  const linkSlot = slot(root, "[data-activity-link-slot]");
  if (!linkSlot) return;
  const showLink = !!(item && item.publicProfileUrl && isHttpsUrl(item.publicProfileUrl) && !example);
  let link = slot(root, "[data-activity-link]");
  if (!showLink) {
    linkSlot.hidden = true;
    if (link) link.removeAttribute("href");
    return;
  }
  const doc = root.ownerDocument;
  if (!link) {
    link = doc.createElement("a");
    link.setAttribute("data-activity-link", "");
    link.className = "ui";
    link.textContent = "Public profile";
    linkSlot.appendChild(link);
  }
  link.textContent = "Public profile";
  link.setAttribute("href", item.publicProfileUrl.trim());
  link.setAttribute("rel", "noopener noreferrer nofollow");
  link.setAttribute("target", "_blank");
  linkSlot.hidden = false;
}

export function paintEmpty(root) {
  paintActivity(root, { line: "No activity to show.", role: "", createdAt: "" }, { example: false });
  const badge = slot(root, "[data-activity-examples]");
  const note = slot(root, "[data-activity-note]");
  if (badge) badge.hidden = true;
  if (note) note.hidden = true;
  const when = slot(root, "[data-activity-when]");
  if (when) when.textContent = "";
}

function listen(bag, target, type, fn) {
  if (!target || !target.addEventListener) return;
  target.addEventListener(type, fn);
  bag.push([target, type, fn]);
}

export function mountActivityFeed(root, options = {}) {
  const doc = root.ownerDocument;
  const view = doc.defaultView || (typeof window !== "undefined" ? window : null);
  const matchMedia = options.matchMedia || (view && view.matchMedia ? view.matchMedia.bind(view) : null);
  const reducedQuery = matchMedia ? matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };
  let reduced = !!reducedQuery.matches;
  const source = options.source || createFeedSource({ transport: null, fallback: options.fallback });
  const setTimer = options.setTimer ?? ((fn, ms) => setTimeout(fn, ms));
  const clearTimer = options.clearTimer ?? ((id) => clearTimeout(id));
  const listeners = [];
  let items = [];
  let rotation = null;
  let swapTimer = null;
  let ttlTimer = null;
  let destroyed = false;

  function clearSwap() {
    if (swapTimer != null) {
      clearTimer(swapTimer);
      swapTimer = null;
    }
  }

  function clearTtl() {
    if (ttlTimer != null) {
      clearTimer(ttlTimer);
      ttlTimer = null;
    }
  }

  function show(index, animate) {
    const item = items[index];
    if (!item) {
      paintEmpty(root);
      return;
    }
    const apply = () => paintActivity(root, item, { example: item.example });
    clearSwap();
    if (!animate || reduced) {
      root.classList.remove("is-swap");
      apply();
      return;
    }
    root.classList.add("is-swap");
    swapTimer = setTimer(() => {
      swapTimer = null;
      if (destroyed) return;
      apply();
      root.classList.remove("is-swap");
    }, SWAP_MS);
  }

  function armRotation() {
    if (rotation) rotation.destroy();
    rotation = createRotation({
      count: items.length,
      intervalMs: options.intervalMs ?? INTERVAL_MS,
      isReduced: () => reduced,
      isHidden: () => !!doc.hidden,
      setTimer,
      clearTimer,
      onIndex: (index, meta) => show(index, !(meta && meta.manual)),
    });
    rotation.start();
  }

  listen(listeners, doc, "visibilitychange", () => {
    if (rotation) rotation.onVisibility();
  });
  listen(listeners, root, "mouseenter", () => rotation && rotation.pause());
  listen(listeners, root, "mouseleave", () => rotation && rotation.resume());
  listen(listeners, root, "focusin", () => rotation && rotation.pause());
  listen(listeners, root, "focusout", (event) => {
    if (root.contains(event.relatedTarget)) return;
    if (rotation) rotation.resume();
  });
  listen(listeners, slot(root, "[data-activity-prev]"), "click", () => {
    if (rotation) rotation.prev();
  });
  listen(listeners, slot(root, "[data-activity-next]"), "click", () => {
    if (rotation) rotation.next();
  });
  if (reducedQuery.addEventListener) {
    const onMotion = () => {
      reduced = !!reducedQuery.matches;
      if (rotation) rotation.onVisibility();
      if (reduced) root.classList.remove("is-swap");
    };
    listen(listeners, reducedQuery, "change", onMotion);
  }

  function showResult(result) {
    items = result.items || [];
    if (!items.length) paintEmpty(root);
    else show(0, false);
    root.classList.add("is-ready");
    armRotation();
    clearTtl();
    if (destroyed || !result.ttlMs) return;
    ttlTimer = setTimer(() => {
      ttlTimer = null;
      if (destroyed) return;
      Promise.resolve()
        .then(() => source.load())
        .then((next) => {
          if (!destroyed && next) showResult(next);
        });
    }, result.ttlMs);
  }

  const ready = Promise.resolve()
    .then(() => source.load())
    .then((result) => {
      if (destroyed) return result;
      showResult(result);
      return result;
    });

  return {
    ready,
    destroy() {
      destroyed = true;
      clearSwap();
      clearTtl();
      if (rotation) rotation.destroy();
      if (source.destroy) source.destroy();
      for (const [target, type, fn] of listeners) target.removeEventListener(type, fn);
      listeners.length = 0;
    },
  };
}

export function readEmbeddedFeed(doc) {
  const el = doc.getElementById("activity-feed-data");
  if (!el) return null;
  try {
    return JSON.parse(el.textContent);
  } catch {
    return null;
  }
}

/* The transport for a feed URL, or null when the card has none (the bundled
   examples only). Only an https URL is accepted. No cookies or credentials
   are sent. */
export function feedTransport(url, fetchFn) {
  if (!isHttpsUrl(url || "", LIMITS.profileUrl)) return null;
  const doFetch = fetchFn || (typeof fetch === "function" ? fetch.bind(globalThis) : null);
  if (!doFetch) return null;
  return () => doFetch(url, { headers: { accept: "application/json" }, credentials: "omit", referrerPolicy: "no-referrer" });
}

export function boot(doc) {
  const documentRef = doc || (typeof document !== "undefined" ? document : null);
  if (!documentRef || !documentRef.querySelector) return null;
  const rootEl = documentRef.documentElement;
  if (rootEl && rootEl.dataset && rootEl.dataset.activityFeedBoot === "off") return null;
  const root = documentRef.querySelector("[data-activity-feed]");
  if (!root) return null;
  const embedded = readEmbeddedFeed(documentRef);
  const fallback = embedded || { example: true, data: [] };
  const feedUrl = root.getAttribute("data-feed-url");
  return mountActivityFeed(root, {
    source: createFeedSource({ transport: feedTransport(feedUrl), fallback }),
  });
}

export const BlowhornActivityFeed = {
  PLATFORMS,
  LIMITS,
  INTERVAL_MS,
  validateItem,
  sanitizeItem,
  normalizePayload,
  parseRetryAfter,
  parseMaxAge,
  MAX_LIVE_TTL_MS,
  isHttpsUrl,
  createFeedSource,
  createRotation,
  paintActivity,
  paintEmpty,
  mountActivityFeed,
  readEmbeddedFeed,
  feedTransport,
  boot,
};

if (typeof globalThis !== "undefined") globalThis.BlowhornActivityFeed = BlowhornActivityFeed;

if (typeof document !== "undefined" && document.querySelector) {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => boot(), { once: true });
  else boot();
}
