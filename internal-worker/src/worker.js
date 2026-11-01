// Serves the internal site (public-internal/) only to requests that carry a
// valid Cloudflare Access token for this application. Access already sits in
// front of the hostname; this check means a missing or misconfigured Access
// application fails closed instead of exposing the site. Every request runs
// this code first (assets.run_worker_first), assets included. The root
// path serves the /internal/ table of contents.
//
// The signups admin (/internal/signups/, /internal/signups/export) shares
// this check: it reads the SIGNUPS_DB database the public signup worker
// writes, and is served only to a verified Access identity.
//
// Deploy-time vars (set by .github/scripts/internal-deploy.sh):
//   TEAM_DOMAIN     <team>.cloudflareaccess.com (the Access auth domain)
//   POLICY_AUD      the Access application's audience tag
//   ALLOWED_EMAILS          comma-separated named addresses: the repository's
//                           allowed_emails plus the INTERNAL_ACCESS_EXTRA_EMAILS
//                           secret (internal-worker/access.json, docs/deploy.md)
//   ALLOWED_EMAIL_DOMAINS   comma-separated email domains (allowed_email_domains)
//
// A verified email is admitted when it is one of ALLOWED_EMAILS, or when the
// part after its last "@" is exactly one of ALLOWED_EMAIL_DOMAINS (no subdomain
// or suffix match). With neither list set, every request is refused (503).

const CERTS_TTL_MS = 10 * 60 * 1000;
let certsCache = { url: '', keys: null, fetchedAt: 0 };

const DENY_HEADERS = {
  'content-type': 'text/plain; charset=utf-8',
  'cache-control': 'no-store',
  'x-robots-tag': 'noindex, nofollow',
};

function deny(status = 403) {
  return new Response(status === 403 ? 'Forbidden\n' : 'Unavailable\n', { status, headers: DENY_HEADERS });
}

function b64urlToBytes(s) {
  const pad = s.length % 4 === 0 ? '' : '='.repeat(4 - (s.length % 4));
  const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/') + pad);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function decodeJson(part) {
  return JSON.parse(new TextDecoder().decode(b64urlToBytes(part)));
}

async function accessKeys(teamDomain, fetchImpl) {
  const url = `https://${teamDomain}/cdn-cgi/access/certs`;
  const now = Date.now();
  if (certsCache.url === url && certsCache.keys && now - certsCache.fetchedAt < CERTS_TTL_MS) {
    return certsCache.keys;
  }
  const res = await fetchImpl(url);
  if (!res.ok) throw new Error('certs unavailable');
  const body = await res.json();
  certsCache = { url, keys: body.keys || [], fetchedAt: now };
  return certsCache.keys;
}

export function resetCertsCache() {
  certsCache = { url: '', keys: null, fetchedAt: 0 };
}

function tokenFrom(request) {
  const header = request.headers.get('cf-access-jwt-assertion');
  if (header) return header;
  const cookie = request.headers.get('cookie') || '';
  const m = cookie.match(/(?:^|;\s*)CF_Authorization=([^;]+)/);
  return m ? m[1] : '';
}

// Returns the verified claims, or null.
export async function verifyAccessToken(token, env, fetchImpl = fetch, nowSec = Math.floor(Date.now() / 1000)) {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  let header;
  let claims;
  try {
    header = decodeJson(parts[0]);
    claims = decodeJson(parts[1]);
  } catch {
    return null;
  }
  if (header.alg !== 'RS256' || !header.kid) return null;
  const keys = await accessKeys(env.TEAM_DOMAIN, fetchImpl);
  const jwk = keys.find((k) => k.kid === header.kid);
  if (!jwk) return null;
  const key = await crypto.subtle.importKey(
    'jwk',
    { kty: jwk.kty, n: jwk.n, e: jwk.e, alg: 'RS256', ext: true },
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['verify'],
  );
  const ok = await crypto.subtle.verify(
    'RSASSA-PKCS1-v1_5',
    key,
    b64urlToBytes(parts[2]),
    new TextEncoder().encode(`${parts[0]}.${parts[1]}`),
  );
  if (!ok) return null;
  const aud = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
  if (!aud.includes(env.POLICY_AUD)) return null;
  if (claims.iss !== `https://${env.TEAM_DOMAIN}`) return null;
  if (typeof claims.exp !== 'number' || claims.exp <= nowSec) return null;
  if (typeof claims.nbf === 'number' && claims.nbf > nowSec + 60) return null;
  const email = String(claims.email || '').toLowerCase();
  if (!emailAllowed(email, listFrom(env.ALLOWED_EMAILS), listFrom(env.ALLOWED_EMAIL_DOMAINS))) return null;
  return claims;
}

function listFrom(value) {
  return String(value || '')
    .split(',')
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
}

// Exact matches only. A domain match needs exactly one "@" and a non-empty
// local part, so "a@evil.com@layer5.io", "layer5.io" and "@layer5.io" are
// refused.
export function emailAllowed(email, emails, domains) {
  if (!email) return false;
  if (emails.includes(email)) return true;
  const at = email.lastIndexOf('@');
  // Exactly one "@": a real mailbox never has two, so refuse rather than judge.
  if (at <= 0 || email.indexOf('@') !== at) return false;
  return domains.includes(email.slice(at + 1));
}

export async function handle(request, env, fetchImpl = fetch) {
  if (!env.TEAM_DOMAIN || !env.POLICY_AUD) return deny(503);
  if (listFrom(env.ALLOWED_EMAILS).length + listFrom(env.ALLOWED_EMAIL_DOMAINS).length === 0) return deny(503);
  const token = tokenFrom(request);
  if (!token) return deny();
  let claims = null;
  try {
    claims = await verifyAccessToken(token, env, fetchImpl);
  } catch {
    return deny(503);
  }
  if (!claims) return deny();
  const url = new URL(request.url);
  // The signups admin lives behind the same Access check: the list holds
  // email addresses, so it is never served to an unauthenticated request.
  if (url.pathname === '/internal/signups/' || url.pathname === '/internal/signups/export') {
    return handleSignupsAdmin(url, env);
  }
  // The root serves the generated table of contents (/internal/), not the
  // build's local-preview redirect page.
  const assetRequest = url.pathname === '/' || url.pathname === '/index.html'
    ? new Request(new URL('/internal/', url), request)
    : request;
  const res = await env.ASSETS.fetch(assetRequest);
  const out = new Response(res.body, res);
  out.headers.set('cache-control', 'private, no-store');
  out.headers.set('x-robots-tag', 'noindex, nofollow');
  return out;
}

// Signups admin: the coming-soon waitlists and the newsletter list, from
// the same D1 database the public signup worker writes (SIGNUPS_DB
// binding). Served only after the Access check above, at
// /internal/signups/ (table) and /internal/signups/export (CSV).
function escHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function csvCell(v) {
  const s = String(v ?? '');
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

const ADMIN_HEADERS = {
  'cache-control': 'no-store',
  'x-robots-tag': 'noindex, nofollow',
};

async function handleSignupsAdmin(url, env) {
  const db = env.SIGNUPS_DB;
  if (!db) return deny(503);
  let rows = [];
  try {
    const res = await db
      .prepare(
        'SELECT email, kind, topic, remark, created_at, unsubscribed_at, source_page FROM signups ORDER BY created_at DESC',
      )
      .all();
    rows = res.results || [];
  } catch {
    return deny(503);
  }
  if (url.pathname === '/internal/signups/export') {
    const head = 'email,kind,topic,remark,created_at,unsubscribed_at,source_page';
    const lines = rows.map((r) =>
      [r.email, r.kind, r.topic, r.remark, r.created_at, r.unsubscribed_at, r.source_page].map(csvCell).join(','),
    );
    return new Response(`${[head, ...lines].join('\n')}\n`, {
      headers: { 'content-type': 'text/csv; charset=utf-8', 'content-disposition': 'attachment; filename="blowhorn-signups.csv"', ...ADMIN_HEADERS },
    });
  }
  const counts = {};
  for (const r of rows) {
    const k = r.topic ? `${r.kind}/${r.topic}` : r.kind;
    counts[k] = (counts[k] || 0) + 1;
  }
  const countList = Object.entries(counts)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([k, n]) => `<li>${escHtml(k)}: ${n}</li>`)
    .join('');
  const tableRows = rows
    .map(
      (r) =>
        `<tr><td>${escHtml(r.email)}</td><td>${escHtml(r.kind)}</td><td>${escHtml(r.topic || '')}</td>` +
        `<td>${escHtml(r.remark)}</td><td>${escHtml(r.created_at)}</td>` +
        `<td>${r.unsubscribed_at ? 'Unsubscribed' : 'Subscribed'}</td><td>${escHtml(r.source_page)}</td></tr>`,
    )
    .join('');
  return new Response(
    `<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="utf-8"><title>Signups</title></head>\n<body>\n<main>\n<h1>Signups</h1>\n<ul>${countList}</ul>\n<p><a href="/internal/signups/export">Download CSV</a></p>\n<table>\n<thead><tr><th>Email</th><th>Kind</th><th>Topic</th><th>Remark</th><th>Signed up</th><th>Status</th><th>Page</th></tr></thead>\n<tbody>${tableRows}</tbody>\n</table>\n</main>\n</body>\n</html>\n`,
    { headers: { 'content-type': 'text/html; charset=utf-8', ...ADMIN_HEADERS } },
  );
}

export default {
  fetch(request, env) {
    return handle(request, env);
  },
};
