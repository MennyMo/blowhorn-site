import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  PLATFORMS,
  INTERVAL_MS,
  validateItem,
  sanitizeItem,
  normalizePayload,
  parseRetryAfter,
  parseMaxAge,
  MAX_LIVE_TTL_MS,
  createFeedSource,
  createRotation,
  paintActivity,
  mountActivityFeed,
  boot,
  feedTransport,
} from "./activity-feed.js";

const sourceText = readFileSync(new URL("./activity-feed.js", import.meta.url), "utf8");
const examples = JSON.parse(readFileSync(new URL("../../data/activity_feed.examples.json", import.meta.url), "utf8"));

const UID = "7c9e6679-7425-40de-944b-e07fc1f90ae7";
const EID = (n) => `00000000-0000-4000-8000-${String(n).padStart(12, "0")}`;

function item(over = {}) {
  return {
    id: EID(1),
    userId: UID,
    category: "schedule",
    action: "completed",
    createdAt: "2026-10-02T08:15:00Z",
    visibility: "public",
    platform: "linkedin",
    role: "Solo founder",
    line: "Example: a solo founder shared a launch post on LinkedIn",
    ...over,
  };
}

// The bundled collection: an envelope marked example, no paging fields.
function payload(data, extra = {}) {
  return { example: true, data, ...extra };
}

// A live EventFeedPage.
function live(data, extra = {}) {
  return { page: 0, pageSize: 20, totalCount: data.length, data, ...extra };
}

function response(status, body, headers = {}) {
  return new Response(typeof body === "string" ? body : JSON.stringify(body), {
    status,
    headers,
  });
}

function element(tag) {
  const node = {
    tag,
    hidden: false,
    textContent: "",
    className: "",
    attrs: {},
    children: [],
    parentNode: null,
    ownerDocument: null,
    classList: null,
    listeners: [],
  };
  node.classList = {
    set: new Set(),
    add(name) { this.set.add(name); },
    remove(name) { this.set.delete(name); },
    contains(name) { return this.set.has(name); },
  };
  node.setAttribute = (key, value) => { node.attrs[key] = String(value); };
  node.removeAttribute = (key) => { delete node.attrs[key]; };
  node.appendChild = (child) => {
    child.parentNode = node;
    node.children.push(child);
  };
  node.addEventListener = (type, fn) => node.listeners.push({ type, fn });
  node.removeEventListener = (type, fn) => {
    node.listeners = node.listeners.filter((entry) => entry.type !== type || entry.fn !== fn);
  };
  node.contains = (target) => {
    if (target === node) return true;
    return node.children.some((child) => child.contains && child.contains(target));
  };
  node.querySelector = (selector) => walk(node, selector);
  Object.defineProperty(node, "innerHTML", {
    configurable: true,
    get() { throw new Error("innerHTML read"); },
    set() { throw new Error("innerHTML write"); },
  });
  return node;
}

function walk(node, selector) {
  const attr = selector.startsWith("[") ? selector.slice(1, -1) : "";
  if (attr && node.attrs[attr] !== undefined) return node;
  for (const child of node.children) {
    const found = walk(child, selector);
    if (found) return found;
  }
  return null;
}

function card() {
  const doc = {
    hidden: false,
    listeners: [],
    addEventListener(type, fn) { this.listeners.push({ type, fn }); },
    removeEventListener(type, fn) {
      this.listeners = this.listeners.filter((entry) => entry.type !== type || entry.fn !== fn);
    },
    createElement: (tag) => {
      const node = element(tag);
      node.ownerDocument = doc;
      return node;
    },
    getElementById() { return null; },
    querySelector() { return null; },
  };
  const root = element("aside");
  root.ownerDocument = doc;
  root.attrs["data-activity-feed"] = "";
  const line = element("p");
  line.attrs["data-activity-line"] = "";
  const role = element("p");
  role.attrs["data-activity-role"] = "";
  const when = element("p");
  when.attrs["data-activity-when"] = "";
  const badge = element("p");
  badge.attrs["data-activity-examples"] = "";
  const note = element("p");
  note.attrs["data-activity-note"] = "";
  const linkSlot = element("p");
  linkSlot.attrs["data-activity-link-slot"] = "";
  linkSlot.hidden = true;
  const prev = element("button");
  prev.attrs["data-activity-prev"] = "";
  const next = element("button");
  next.attrs["data-activity-next"] = "";
  for (const child of [line, role, when, badge, note, linkSlot, prev, next]) root.appendChild(child);
  return { doc, root, line, role, when, badge, note, linkSlot, prev, next };
}

test("bundled examples stay inside the contract", () => {
  assert.equal(examples.example, true);
  assert.equal(examples.items, undefined);
  assert.ok(examples.data.length >= 60 && examples.data.length <= 80);
  const roles = new Set([
    "Solo founder",
    "Agency",
    "Open source maintainer",
    "DevRel",
    "Marketing manager",
    "Community manager",
    "Founder",
  ]);
  assert.equal(normalizePayload(examples).items.length, examples.data.length);
  for (const entry of examples.data) {
    assert.equal(validateItem(entry).ok, true);
    assert.equal(entry.category, "schedule");
    assert.equal(entry.action, "completed");
    assert.equal(entry.visibility, "public");
    assert.ok(PLATFORMS.includes(entry.platform));
    assert.ok(roles.has(entry.role));
    assert.match(entry.line, /^Example: /);
    assert.equal(entry.displayName, undefined);
    assert.equal(entry.avatarUrl, undefined);
    assert.equal(entry.publicProfileUrl, undefined);
    assert.equal(entry.line.includes("\u2014"), false);
    assert.ok(entry.createdAt < "2026-11-05");
    assert.doesNotMatch(entry.line, /just now|ago|followers|likes|impressions/i);
  }
});

test("sanitize accepts a clean example and strips control characters", () => {
  const cleaned = sanitizeItem(item({ line: "Example: a solo founder\u0000 shared a launch post on LinkedIn" }));
  assert.equal(cleaned.line, "Example: a solo founder shared a launch post on LinkedIn");
  assert.equal(cleaned.example, false);
});

test("validation rejects XSS urls, bad schemes, oversize text and unknown platforms", () => {
  const xss = "<img src=x onerror=alert(1)>";
  const text = sanitizeItem(item({ line: `Example: ${xss} on LinkedIn today` }));
  assert.equal(text.line.includes(xss), true);
  assert.equal(validateItem(item({ publicProfileUrl: "javascript:alert(1)" })).ok, false);
  assert.equal(validateItem(item({ publicProfileUrl: "JavaScript:alert(1)" })).ok, false);
  assert.equal(validateItem(item({ avatarUrl: "data:text/html,<script>alert(1)</script>" })).ok, false);
  assert.equal(validateItem(item({ publicProfileUrl: "http://example.com/a" })).ok, false);
  assert.equal(validateItem(item({ publicProfileUrl: "https://user:pass@example.com/a" })).ok, false);
  assert.equal(validateItem(item({ line: "x".repeat(121) })).ok, false);
  assert.equal(validateItem(item({ role: "A" })).ok, false);
  assert.equal(validateItem(item({ platform: "youtube" })).ok, false);
  assert.equal(validateItem(item({ platform: "LinkedIn" })).ok, false);
  assert.equal(validateItem(item({ extra: true })).ok, true); // unknown keys ignored
  assert.equal(validateItem(item({ visibility: "private" })).ok, false);
  assert.equal(validateItem(item({ completedAt: "2026-10-02T08:15:00Z" })).ok, true); // legacy key ignored
  assert.equal(validateItem(item({ id: "example-1" })).ok, false);
  assert.equal(validateItem(item({ userId: "example-account-1" })).ok, false);
  assert.equal(validateItem(item({ createdAt: "yesterday" })).ok, false);
  assert.equal(validateItem(item({ category: undefined })).ok, false);
  assert.equal(validateItem(item({ action: "" })).ok, false);
  assert.equal(validateItem("nope").ok, false);
});

test("paint uses textContent and a hardened profile link", () => {
  const view = card();
  const xss = "<img src=x onerror=alert(1)>";
  paintActivity(view.root, item({
    line: `Example: ${xss} posted`,
    publicProfileUrl: "https://example.com/profile",
  }), { example: false });
  assert.equal(view.line.textContent, `Example: ${xss} posted`);
  assert.equal(view.when.textContent, "2026-10-02");
  const link = view.linkSlot.children[0];
  assert.equal(link.attrs.href, "https://example.com/profile");
  assert.equal(link.attrs.rel, "noopener noreferrer nofollow");
  assert.equal(link.attrs.target, "_blank");
  assert.equal(link.textContent, "Public profile");

  paintActivity(view.root, item({ publicProfileUrl: "https://example.com/profile" }), { example: true });
  assert.equal(view.when.textContent, "Example activity");
  assert.equal(view.badge.hidden, false);
  assert.equal(view.linkSlot.hidden, true);
  assert.equal(link.attrs.href, undefined);
});

test("empty and malformed payloads fall back", async () => {
  const fallback = payload([item()]);
  // Cloud's feed is empty today: a valid page with no data.
  const empty = await createFeedSource({
    transport: async () => response(200, { page: 0, pageSize: 20, totalCount: 0, data: [] }),
    fallback,
  }).load();
  assert.equal(empty.fromFallback, true);
  assert.equal(empty.reason, "empty");
  assert.equal(empty.example, true);
  assert.equal(empty.items[0].id, EID(1));

  const malformed = await createFeedSource({
    transport: async () => response(200, "{"),
    fallback,
  }).load();
  assert.equal(malformed.reason, "malformed");
  assert.equal(malformed.fromFallback, true);

  const arrayBody = await createFeedSource({
    transport: async () => response(200, []),
    fallback,
  }).load();
  assert.equal(arrayBody.fromFallback, true);
  assert.equal(arrayBody.reason, "invalid");

  const dropped = normalizePayload(live([item({ platform: "tiktok" }), item({ id: EID(2) })]));
  assert.equal(dropped.dropped, 1);
  assert.equal(dropped.items.length, 1);
  assert.equal(dropped.items[0].id, EID(2));
  assert.equal(dropped.items[0].example, false);

  const allBad = await createFeedSource({
    transport: async () => response(200, live([{ id: "nope" }])),
    fallback,
  }).load();
  assert.equal(allBad.reason, "invalid");
  assert.equal(allBad.fromFallback, true);
});

test("a page that is not an EventFeedPage yields no items", () => {
  const good = live([item()]);
  assert.equal(normalizePayload(good).valid, true);
  assert.equal(normalizePayload(good).items.length, 1);
  assert.equal(normalizePayload(live([])).valid, true);
  // The retired envelope has no `data`, so it is invalid.
  assert.equal(normalizePayload({ version: 1, sample: false, generatedAt: "2026-11-04T18:00:00Z", items: [item()] }).valid, false);
  // An unknown sibling key beside a valid EventFeedPage is ignored.
  assert.equal(normalizePayload({ ...good, items: [item()] }).valid, true);
  const { data, ...noData } = good;
  assert.equal(normalizePayload(noData).valid, false);
  assert.equal(normalizePayload({ ...good, page: -1 }).valid, false);
  assert.equal(normalizePayload({ ...good, page: 1.5 }).valid, false);
  assert.equal(normalizePayload({ ...good, pageSize: 0 }).valid, false);
  assert.equal(normalizePayload({ ...good, pageSize: 51 }).valid, false);
  assert.equal(normalizePayload({ ...good, totalCount: "1" }).valid, false);
  assert.equal(normalizePayload({ ...good, example: "yes" }).valid, false);
  assert.equal(normalizePayload(live(Array.from({ length: 51 }, (_, i) => item({ id: EID(i + 1) })), { pageSize: 50 })).valid, false);
  assert.equal(normalizePayload(null).valid, false);
});

test("timeout, network error and 500 use the fallback", async () => {
  const fallback = payload([item()]);
  let fire;
  const cleared = [];
  const timed = createFeedSource({
    timeoutMs: 5000,
    setTimer(fn) { fire = fn; return 7; },
    clearTimer(id) { cleared.push(id); },
    transport: () => new Promise(() => {}),
    fallback,
  });
  const pending = timed.load();
  fire();
  const timeout = await pending;
  assert.equal(timeout.reason, "timeout");
  assert.equal(timeout.fromFallback, true);
  assert.equal(timed.memory, null);
  assert.deepEqual(cleared, [7]);

  const network = await createFeedSource({
    transport: async () => { throw new TypeError("offline"); },
    fallback,
  }).load();
  assert.equal(network.reason, "network");
  assert.equal(network.items[0].line, item().line);

  let calls = 0;
  const server = createFeedSource({
    transport: async () => {
      calls += 1;
      return response(500, { error: true });
    },
    fallback,
  });
  assert.equal((await server.load()).reason, "http");
  assert.equal((await server.load()).fromFallback, true);
  assert.equal(calls, 2);
});

test("429 waits for Retry-After seconds or an HTTP date", async () => {
  const fallback = payload([item()]);
  let now = Date.parse("2026-11-05T12:00:00Z");
  let calls = 0;
  const seconds = createFeedSource({
    now: () => now,
    transport: async () => {
      calls += 1;
      return response(429, "slow", { "retry-after": "30" });
    },
    fallback,
  });
  assert.equal((await seconds.load()).reason, "rate-limit");
  now += 29000;
  assert.equal((await seconds.load()).reason, "rate-limit");
  assert.equal(calls, 1);
  now += 1000;
  calls = 0;
  seconds.destroy();

  const dated = createFeedSource({
    now: () => now,
    transport: async () => {
      calls += 1;
      return response(429, "slow", { "retry-after": "Wed, 05 Nov 2026 12:02:00 GMT" });
    },
    fallback,
  });
  calls = 0;
  assert.equal((await dated.load()).reason, "rate-limit");
  now = Date.parse("2026-11-05T12:01:00Z");
  assert.equal((await dated.load()).fromFallback, true);
  assert.equal(calls, 1);
  now = Date.parse("2026-11-05T12:02:00Z");
  assert.equal((await dated.load()).reason, "rate-limit");
  assert.equal(calls, 2);

  const until = parseRetryAfter("45", 1000);
  assert.equal(until, 46000);
  assert.equal(parseRetryAfter("not-a-date", 1000), null);
});

test("transport is disabled by default and the first visit has no stored feed", async () => {
  const fallback = payload([item()]);
  const disabled = await createFeedSource({
    fallback,
    transport: null,
  }).load();
  assert.equal(disabled.reason, "disabled");

  const implicit = await createFeedSource({ fallback }).load();
  assert.equal(implicit.reason, "disabled");
  assert.equal(implicit.example, true);
  assert.equal(implicit.items.length, 1);

  const offline = await createFeedSource({
    transport: async () => { throw new TypeError("Failed to fetch"); },
    fallback,
  }).load();
  assert.equal(offline.reason, "network");
  assert.equal(offline.fromFallback, true);
  assert.equal(createFeedSource({ fallback }).memory, null);
});

test("the bundled collection is labelled as examples and is not kept as live", async () => {
  const fallback = payload([item()]);
  const source = createFeedSource({
    transport: async () => response(200, payload([item({ id: EID(5), line: "A founder shared a launch post on LinkedIn" })]), { "cache-control": "max-age=30" }),
    fallback,
  });
  const result = await source.load();
  assert.equal(result.reason, "live");
  assert.equal(result.fromFallback, false);
  assert.equal(result.example, true);
  assert.equal(result.items[0].example, true);
  assert.equal(result.ttlMs, 0);
  assert.equal(source.memory, null);
});

test("a live page is shown as live for its max-age", async () => {
  const source = createFeedSource({
    now: () => 1_000_000,
    transport: async () => response(200, live([item({ id: EID(6), line: "A founder shared a launch post on LinkedIn" })]), { "cache-control": "public, max-age=30" }),
    fallback: payload([item()]),
  });
  const result = await source.load();
  assert.equal(result.reason, "live");
  assert.equal(result.example, false);
  assert.equal(result.items[0].example, false);
  assert.equal(result.ttlMs, 30000);
  assert.equal(source.memory.length, 1);
});

test("a live page with no max-age is not held and shows the examples", async () => {
  const result = await createFeedSource({
    transport: async () => response(200, live([item({ id: EID(7) })])),
    fallback: payload([item()]),
  }).load();
  assert.equal(result.reason, "ttl");
  assert.equal(result.fromFallback, true);
  assert.equal(result.example, true);
});

test("feedTransport takes only an https URL and sends no credentials", async () => {
  assert.equal(feedTransport(null), null);
  assert.equal(feedTransport(""), null);
  assert.equal(feedTransport("http://cloud.example.test/api/events/feed"), null);
  assert.equal(feedTransport("javascript:alert(1)"), null);
  const calls = [];
  const transport = feedTransport("https://cloud.example.test/api/events/feed?page=0&pagesize=20", async (url, init) => {
    calls.push({ url, init });
    return response(200, live([]));
  });
  assert.equal(typeof transport, "function");
  await transport();
  assert.equal(calls[0].url, "https://cloud.example.test/api/events/feed?page=0&pagesize=20");
  assert.equal(calls[0].init.credentials, "omit");
  assert.equal(calls[0].init.headers.accept, "application/json");
});

test("max-age is capped at 30 seconds", () => {
  assert.equal(MAX_LIVE_TTL_MS, 30000);
  assert.equal(parseMaxAge("max-age=10"), 10000);
  assert.equal(parseMaxAge("public, max-age=30"), 30000);
  assert.equal(parseMaxAge("max-age=90, public"), 30000);
  assert.equal(parseMaxAge("max-age=0"), 0);
  assert.equal(parseMaxAge("no-store"), 0);
  assert.equal(parseMaxAge(null), 0);
});

test("live items expire at the TTL and refresh failure restores labeled examples", async () => {
  const writes = [];
  const touch = () => writes.push("write");
  globalThis.localStorage = { setItem: touch, getItem: touch };
  globalThis.sessionStorage = { setItem: touch, getItem: touch };
  globalThis.indexedDB = { open: touch };
  globalThis.caches = { open: touch, put: touch, match: touch };
  const fallback = payload([item({ id: EID(21) })]);
  const liveItem = item({ id: EID(11), line: "A founder shared a launch post on LinkedIn" });
  let now = 1_000_000;
  let calls = 0;
  let fail = false;
  const source = createFeedSource({
    now: () => now,
    fallback,
    transport: async () => {
      calls += 1;
      if (fail) throw new TypeError("offline");
      return response(200, live([liveItem]), { "cache-control": "max-age=90" });
    },
  });
  const first = await source.load();
  assert.equal(first.reason, "live");
  assert.equal(first.fromFallback, false);
  assert.equal(first.ttlMs, 30000);
  assert.equal(first.items[0].id, EID(11));
  assert.equal(source.memory[0].id, EID(11));
  const cached = await source.load();
  assert.equal(cached.reason, "live");
  assert.equal(calls, 1);
  now += 30000;
  fail = true;
  const expired = await source.load();
  assert.equal(expired.fromFallback, true);
  assert.equal(expired.example, true);
  assert.equal(expired.items[0].id, EID(21));
  assert.equal(expired.items[0].example, true);
  assert.equal(source.memory.some((entry) => entry.id === EID(11)), false);
  assert.equal(source.memory[0].example, true);
  assert.equal(writes.length, 0);
  delete globalThis.localStorage;
  delete globalThis.sessionStorage;
  delete globalThis.indexedDB;
  delete globalThis.caches;
});

test("an expired hold is replaced by labeled examples when there is no transport", async () => {
  let now = 0;
  const options = {
    now: () => now,
    fallback: payload([item({ id: EID(29) })]),
    transport: async () => response(200, live([item({ id: EID(19), line: "A founder shared a launch post on LinkedIn" })]), { "cache-control": "max-age=5" }),
  };
  const source = createFeedSource(options);
  const first = await source.load();
  assert.equal(first.items[0].id, EID(19));
  assert.equal(first.ttlMs, 5000);
  now = 5000;
  options.transport = null;
  const next = await source.load();
  assert.equal(next.reason, "disabled");
  assert.equal(next.fromFallback, true);
  assert.equal(next.example, true);
  assert.equal(next.items[0].id, EID(29));
  assert.equal(source.memory[0].id, EID(29));
  assert.equal(source.memory.some((entry) => entry.id === EID(19)), false);
});

test("rotation pauses for reduced motion, a hidden document and hover, and clears timers", () => {
  assert.equal(INTERVAL_MS, 7000);
  const scheduled = [];
  const cleared = [];
  let id = 0;
  const setTimer = (fn, ms) => {
    const handle = ++id;
    scheduled.push({ handle, ms, fn });
    return handle;
  };
  const clearTimer = (handle) => cleared.push(handle);
  let reduced = false;
  let hidden = false;
  const seen = [];
  const rotation = createRotation({
    count: 3,
    intervalMs: INTERVAL_MS,
    isReduced: () => reduced,
    isHidden: () => hidden,
    setTimer,
    clearTimer,
    onIndex: (index) => seen.push(index),
  });

  reduced = true;
  rotation.start();
  assert.equal(rotation.armed, false);
  assert.equal(scheduled.length, 0);
  assert.equal(rotation.next(), 1);
  assert.deepEqual(seen, [1]);
  assert.equal(rotation.armed, false);

  reduced = false;
  hidden = true;
  rotation.start();
  assert.equal(rotation.armed, false);
  hidden = false;
  rotation.onVisibility();
  assert.equal(scheduled.length, 1);
  assert.equal(scheduled[0].ms, 7000);
  assert.equal(rotation.armed, true);

  rotation.pause();
  assert.equal(rotation.armed, false);
  assert.equal(cleared.includes(scheduled[0].handle), true);
  rotation.resume();
  assert.equal(rotation.armed, true);

  hidden = true;
  rotation.onVisibility();
  assert.equal(rotation.armed, false);
  hidden = false;
  rotation.onVisibility();
  const last = scheduled[scheduled.length - 1];
  rotation.destroy();
  assert.equal(rotation.armed, false);
  assert.equal(cleared.includes(last.handle), true);
  const before = scheduled.length;
  rotation.start();
  rotation.next();
  assert.equal(scheduled.length, before);
});

test("mount cleans timers and listeners and does not write storage", async () => {
  const writes = [];
  const storage = new Proxy({}, {
    get: () => () => writes.push("write"),
  });
  globalThis.localStorage = storage;
  globalThis.sessionStorage = storage;
  globalThis.indexedDB = storage;
  globalThis.caches = storage;

  const view = card();
  const timers = [];
  const cleared = [];
  let seq = 0;
  const mounted = mountActivityFeed(view.root, {
    matchMedia: () => ({ matches: true, addEventListener() {}, removeEventListener() {} }),
    setTimer(fn, ms) {
      const handle = ++seq;
      timers.push({ handle, ms, fn });
      return handle;
    },
    clearTimer(handle) { cleared.push(handle); },
    source: createFeedSource({
      transport: null,
      fallback: payload([item(), item({ id: EID(2), line: "Example: an agency published a release note on X" })]),
    }),
  });
  const result = await mounted.ready;
  assert.equal(result.reason, "disabled");
  assert.equal(view.root.classList.contains("is-ready"), true);
  assert.equal(view.line.textContent.includes("solo founder"), true);
  assert.equal(view.doc.listeners.some((entry) => entry.type === "visibilitychange"), true);
  view.next.listeners.find((entry) => entry.type === "click").fn();
  assert.equal(view.line.textContent.includes("agency"), true);
  mounted.destroy();
  assert.equal(view.doc.listeners.length, 0);
  mounted.destroy();
  assert.equal(writes.length, 0);
  delete globalThis.localStorage;
  delete globalThis.sessionStorage;
  delete globalThis.indexedDB;
  delete globalThis.caches;
});

test("runtime source has no endpoint and no web storage", () => {
  assert.equal(/localStorage|sessionStorage|indexedDB|serviceWorker|caches\.put|caches\.open/.test(sourceText), false);
  assert.equal(/\/api\/public|api\.blowhorn|layer5|events\/feed/.test(sourceText), false);
  assert.equal(/https?:\/\/[A-Za-z0-9.-]+\.[A-Za-z]{2,}/.test(sourceText), false);
  assert.equal(boot({ documentElement: { dataset: { activityFeedBoot: "off" } }, querySelector() { return {}; } }), null);
});
