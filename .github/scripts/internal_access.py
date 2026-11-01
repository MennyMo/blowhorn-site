#!/usr/bin/env python3
"""Manage the Cloudflare Access application in front of the internal site.

Usage: internal_access.py check|ensure|verify-worker [--config PATH] [--env-out PATH]

  check          Read-only: confirm the API token can read the Zero Trust
                 organization, Access applications, policies and login
                 methods (identity providers), and the Worker's workers.dev
                 setting. Changes nothing.
  ensure         Idempotent: create or update the reusable allow policy and
                 the self-hosted Access application for the hostname in
                 internal-worker/access.json, then read them back and fail
                 unless the application is default-deny with exactly that
                 policy and exactly the configured login methods. The policy
                 admits the configured email domains and named emails plus
                 the extras in the environment variable that access.json's
                 extra_emails_env names (a GitHub secret in the workflow).
                 Writes TEAM_DOMAIN and POLICY_AUD to --env-out (GITHUB_ENV
                 in the workflow) for the Worker deploy.
  verify-worker  Fail unless the Worker's workers.dev and preview URLs are
                 off, so Access cannot be bypassed.

Login methods are named by identity provider type in allowed_idps (for
example onetimepin, google) and resolved to ids on the account at run time;
each type must match exactly one identity provider. docs/deploy.md, "Login
methods", says how to add one.

Needs CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID in the environment.
Prints only status lines, counts and Cloudflare API error codes: never a
token, never page content, and never an address or domain other than as a
count. Under GitHub Actions each extra address is masked before anything
else prints.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.cloudflare.com/client/v4"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_CONFIG = os.path.join(ROOT, "internal-worker", "access.json")
WORKER_CONFIG = os.path.join(ROOT, "internal-worker", "wrangler.json")

# What each call needs, so a 403 names the missing token permission.
PERM_ACCESS_APPS = "Account > Access: Apps and Policies > Edit"
PERM_ACCESS_ORG = "Account > Access: Organizations, Identity Providers, and Groups > Read"
PERM_WORKERS = "Account > Workers Scripts > Edit"

# Shapes the config and the extras must match. Matched after lower-casing, so
# a mixed-case address is accepted and normalized, never rejected.
DOMAIN_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+")
EMAIL_RE = re.compile(r"[a-z0-9._%+-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]*")
IDP_TYPE_RE = re.compile(r"[a-z0-9_-]+")
REQUIRED_KEYS = (
    "hostname", "app_name", "policy_name", "session_duration", "allowed_email_domains",
    "allowed_emails", "extra_emails_env", "allowed_idps",
)


class ApiError(Exception):
    def __init__(self, status, errors, permission):
        self.status = status
        self.errors = errors
        self.permission = permission
        codes = ", ".join(f"{e.get('code')}: {e.get('message')}" for e in errors) or "no error body"
        hint = f" The API token may lack '{permission}'." if status in (401, 403) and permission else ""
        super().__init__(f"Cloudflare API {status} ({codes}).{hint}")


def call(method, path, permission, body=None):
    token = os.environ["CLOUDFLARE_API_TOKEN"]
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"{API}{path}", data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            payload = json.loads(res.read() or b"{}")
            status = res.status
    except urllib.error.HTTPError as err:
        try:
            payload = json.loads(err.read() or b"{}")
        except ValueError:
            payload = {}
        raise ApiError(err.code, payload.get("errors") or [], permission) from None
    if not payload.get("success", False):
        raise ApiError(status, payload.get("errors") or [], permission)
    return payload


def list_all(path, permission):
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        payload = call("GET", f"{path}{sep}page={page}&per_page=50", permission)
        out.extend(payload.get("result") or [])
        info = payload.get("result_info") or {}
        if not info or page >= int(info.get("total_pages") or 1):
            return out
        page += 1


def _entries(cfg, key, pattern):
    """The list at cfg[key], lower-cased and stripped, in config order.

    Exits with the list positions of bad entries, never their values, so a
    malformed address cannot reach a log through this message.
    """
    value = cfg.get(key)
    if not isinstance(value, list):
        sys.exit(f"internal_access: {key} must be a list in internal-worker/access.json")
    bad = [str(i) for i, v in enumerate(value) if not isinstance(v, str) or not pattern.fullmatch(v.strip().lower())]
    if bad:
        noun = "entry" if len(bad) == 1 else "entries"
        sys.exit(f"internal_access: {key} has {len(bad)} malformed {noun} (list position {', '.join(bad)}) in internal-worker/access.json")
    return [v.strip().lower() for v in value]


def _extra_emails(cfg, required):
    """Addresses from the environment variable named by extra_emails_env.

    One per line or comma-separated. Under GitHub Actions every token is
    masked before anything else prints, so no log line can show it.
    """
    name = cfg["extra_emails_env"]
    raw = [t for t in re.split(r"[,\s]+", os.environ.get(name, "")) if t]
    if os.environ.get("GITHUB_ACTIONS") == "true":
        for t in sorted(set(raw) | {t.lower() for t in raw}):
            print(f"::add-mask::{t}")
    if not raw:
        if required:
            sys.exit(f"internal_access: {name} is not set or is empty, so the teammates in it would be dropped from the Access policy. Set it as a repository secret (gh secret set {name} -R blowhorn-ai/blowhorn-site < file, one address per line), then rerun.")
        print(f"internal_access: note: {name} is not set, so extra teammates are not part of this check")
        return []
    bad = [t for t in raw if not EMAIL_RE.fullmatch(t.lower())]
    if bad:
        noun = "entry" if len(bad) == 1 else "entries"
        sys.exit(f"internal_access: {len(bad)} malformed {noun} in {name}; each must be one email address, one per line or comma-separated")
    return sorted({t.lower() for t in raw})


def load_config(path, require_extras=True):
    """Read and normalize access.json and merge the extras into allowed_emails.

    require_extras=False (check, verify-worker) only notes an unset extras
    variable; ensure passes True, so an unconfigured secret never silently
    drops teammates from the policy.
    """
    with open(path) as fh:
        cfg = json.load(fh)
    missing = [k for k in REQUIRED_KEYS if k not in cfg]
    if missing:
        sys.exit("internal_access: internal-worker/access.json is missing " + ", ".join(missing))
    for key in ("hostname", "app_name", "policy_name", "session_duration", "extra_emails_env"):
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            sys.exit(f"internal_access: {key} must be a non-empty string in internal-worker/access.json")
    if not ENV_NAME_RE.fullmatch(cfg["extra_emails_env"]):
        sys.exit("internal_access: extra_emails_env must name an environment variable (upper-case letters, digits and underscores)")
    domains = sorted(set(_entries(cfg, "allowed_email_domains", DOMAIN_RE)))
    named = sorted(set(_entries(cfg, "allowed_emails", EMAIL_RE)))
    idps = _entries(cfg, "allowed_idps", IDP_TYPE_RE)
    if not idps:
        sys.exit("internal_access: allowed_idps needs at least one login method type in internal-worker/access.json")
    if len(set(idps)) != len(idps):
        sys.exit("internal_access: allowed_idps lists a login method type more than once")
    extras = _extra_emails(cfg, require_extras)
    cfg["allowed_email_domains"] = domains
    cfg["allowed_emails"] = sorted(set(named) | set(extras))
    cfg["allowed_idps"] = idps
    if not cfg["allowed_emails"] and not domains:
        sys.exit("internal_access: no email domains or email addresses are configured (access.json plus the extras); refusing to create an Access policy that admits nobody by mistake")
    return cfg


def account():
    return f"/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}"


def team_domain():
    org = call("GET", f"{account()}/access/organizations", PERM_ACCESS_ORG)["result"] or {}
    domain = org.get("auth_domain")
    if not domain:
        sys.exit("internal_access: no Zero Trust organization on this account. Open Zero Trust in the Cloudflare dashboard once to pick a team name (the free plan is enough), then rerun.")
    return domain


def app_hosts(app):
    hosts = [app.get("domain") or ""]
    hosts += app.get("self_hosted_domains") or []
    hosts += [d.get("uri", "") for d in app.get("destinations") or [] if d.get("type", "public") == "public"]
    return {h for h in hosts if h}


def matching_apps(apps, hostname):
    """Applications on the hostname itself or any path or subdomain of it."""
    hits = []
    for app in apps:
        for h in app_hosts(app):
            bare = h.split("/", 1)[0]
            if bare == hostname or bare.endswith("." + hostname) or bare == "*." + hostname:
                hits.append(app)
                break
    return hits


def policy_body(cfg):
    include = [{"email_domain": {"domain": d}} for d in cfg["allowed_email_domains"]]
    include += [{"email": {"email": e}} for e in cfg["allowed_emails"]]
    return {
        "name": cfg["policy_name"],
        "decision": "allow",
        "include": include,
        "exclude": [],
        "require": [],
        "session_duration": cfg["session_duration"],
    }


def resolve_idps(cfg):
    """Ids of the configured login methods, in config order.

    Each configured type must match exactly one identity provider on the
    account: zero means it was never added, more than one is ambiguous.
    """
    idps = list_all(f"{account()}/access/identity_providers", PERM_ACCESS_ORG)
    ids = []
    for idp_type in cfg["allowed_idps"]:
        match = [i for i in idps if i.get("type") == idp_type]
        if not match:
            sys.exit(f"internal_access: no login method of type '{idp_type}' on this account (found 0). Add it in Zero Trust > Settings > Authentication > Login methods; docs/deploy.md, 'Login methods', has the steps.")
        if len(match) > 1:
            sys.exit(f"internal_access: {len(match)} login methods of type '{idp_type}' on this account; keep one in Zero Trust > Settings > Authentication > Login methods")
        ids.append(match[0]["id"])
    return ids


def app_body(cfg, policy_id, idp_ids):
    host = cfg["hostname"]
    return {
        "name": cfg["app_name"],
        "type": "self_hosted",
        "domain": host,
        "destinations": [{"type": "public", "uri": host}],
        "session_duration": cfg["session_duration"],
        "app_launcher_visible": False,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "lax",
        "skip_interstitial": False,
        # Show every allowed login method on the page, not redirect straight to one.
        "auto_redirect_to_identity": False,
        "allowed_idps": idp_ids,
        "policies": [{"id": policy_id, "precedence": 1}],
    }


def ensure(cfg):
    acct = account()
    domain = team_domain()
    print(f"internal_access: Zero Trust team domain found")
    # Resolve login methods before writing anything, so a missing one fails cleanly.
    idp_ids = resolve_idps(cfg)

    policies = [p for p in list_all(f"{acct}/access/policies", PERM_ACCESS_APPS) if p.get("name") == cfg["policy_name"]]
    if len(policies) > 1:
        sys.exit(f"internal_access: {len(policies)} reusable policies are named '{cfg['policy_name']}'; delete the extras in Zero Trust > Access > Policies")
    if policies:
        policy = call("PUT", f"{acct}/access/policies/{policies[0]['id']}", PERM_ACCESS_APPS, policy_body(cfg))["result"]
        print("internal_access: allow policy updated")
    else:
        policy = call("POST", f"{acct}/access/policies", PERM_ACCESS_APPS, policy_body(cfg))["result"]
        print("internal_access: allow policy created")

    apps = matching_apps(list_all(f"{acct}/access/apps", PERM_ACCESS_APPS), cfg["hostname"])
    exact = [a for a in apps if a.get("domain") == cfg["hostname"] and a.get("type") == "self_hosted"]
    others = [a for a in apps if a not in exact]
    if others:
        # Another application on a path or subdomain could carry a bypass or
        # an Everyone rule and win for its paths. Refuse rather than guess.
        sys.exit(f"internal_access: {len(others)} other Access application(s) cover {cfg['hostname']} or a path under it; remove them so one default-deny application governs the whole hostname")
    if len(exact) > 1:
        sys.exit(f"internal_access: {len(exact)} Access applications exist for {cfg['hostname']}; keep one")
    if exact:
        app = call("PUT", f"{acct}/access/apps/{exact[0]['id']}", PERM_ACCESS_APPS, app_body(cfg, policy["id"], idp_ids))["result"]
        print("internal_access: Access application updated")
    else:
        app = call("POST", f"{acct}/access/apps", PERM_ACCESS_APPS, app_body(cfg, policy["id"], idp_ids))["result"]
        print("internal_access: Access application created")

    verify_app(cfg, app["id"], policy["id"], idp_ids)
    return domain, app["aud"]


def verify_app(cfg, app_id, policy_id, idp_ids):
    acct = account()
    app = call("GET", f"{acct}/access/apps/{app_id}", PERM_ACCESS_APPS)["result"]
    problems = []
    if app.get("domain") != cfg["hostname"]:
        problems.append("application domain differs from the configured hostname")
    if app.get("type") != "self_hosted":
        problems.append("application is not self_hosted")
    attached = app.get("policies") or []
    if [p.get("id") for p in attached] != [policy_id]:
        problems.append(f"application has {len(attached)} policies, expected exactly the managed allow policy")
    if sorted(app.get("allowed_idps") or []) != sorted(idp_ids):
        problems.append("application login methods differ from allowed_idps in internal-worker/access.json")
    policy = call("GET", f"{acct}/access/policies/{policy_id}", PERM_ACCESS_APPS)["result"]
    if policy.get("decision") != "allow":
        problems.append("policy decision is not allow")
    if policy.get("exclude") or policy.get("require"):
        problems.append("policy has unexpected exclude or require rules")
    include = policy.get("include") or []
    # Only named-email and email-domain rules: anything else (Everyone, a group,
    # an IP range, a country) would widen the policy beyond the config.
    if any(set(r) not in ({"email"}, {"email_domain"}) for r in include):
        problems.append("policy includes a rule other than a named email or an email domain (for example Everyone or a group)")
    emails = sorted({(r.get("email") or {}).get("email", "").lower() for r in include if "email" in r})
    domains = sorted({(r.get("email_domain") or {}).get("domain", "").lower() for r in include if "email_domain" in r})
    if emails != cfg["allowed_emails"]:
        problems.append("policy emails differ from internal-worker/access.json and the extras")
    if domains != cfg["allowed_email_domains"]:
        problems.append("policy email domains differ from allowed_email_domains in internal-worker/access.json")
    if not app.get("aud"):
        problems.append("application has no audience tag")
    if problems:
        sys.exit("internal_access: verification failed: " + "; ".join(problems))
    print(f"internal_access: verified: one self-hosted application, default deny, allow list of {len(domains)} email domain(s) and {len(emails)} named email(s), {len(idp_ids)} login method(s)")


def worker_name():
    with open(WORKER_CONFIG) as fh:
        return json.load(fh)["name"]


def verify_worker():
    name = worker_name()
    sub = call("GET", f"{account()}/workers/scripts/{name}/subdomain", PERM_WORKERS)["result"] or {}
    if sub.get("enabled") or sub.get("previews_enabled"):
        sys.exit(f"internal_access: Worker {name} has workers.dev or preview URLs enabled; Access could be bypassed")
    print(f"internal_access: Worker {name}: workers.dev off, preview URLs off")


def check(cfg):
    acct = account()
    results = []
    probes = [
        ("Zero Trust organization", lambda: team_domain()),
        ("Access applications", lambda: list_all(f"{acct}/access/apps", PERM_ACCESS_APPS)),
        ("Access reusable policies", lambda: list_all(f"{acct}/access/policies", PERM_ACCESS_APPS)),
        ("Access identity providers", lambda: resolve_idps(cfg)),
        ("Workers scripts", lambda: call("GET", f"{acct}/workers/scripts", PERM_WORKERS)),
    ]
    ok = True
    for label, fn in probes:
        try:
            fn()
            results.append(f"ok    {label}")
        except ApiError as err:
            ok = False
            results.append(f"FAIL  {label}: {err}")
        except SystemExit as err:
            ok = False
            results.append(f"FAIL  {label}: {err}")
    print("\n".join(results))
    if not ok:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "ensure", "verify-worker"])
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--env-out", default=os.environ.get("GITHUB_ENV", ""))
    args = ap.parse_args()
    for var in ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"):
        if not os.environ.get(var):
            sys.exit(f"internal_access: {var} is not set")
    cfg = load_config(args.config, require_extras=args.command == "ensure")
    try:
        if args.command == "check":
            check(cfg)
        elif args.command == "verify-worker":
            verify_worker()
        else:
            domain, aud = ensure(cfg)
            if os.environ.get("GITHUB_ACTIONS") == "true":
                print(f"::add-mask::{aud}")
            if not args.env_out:
                sys.exit("internal_access: pass --env-out (or set GITHUB_ENV) to hand TEAM_DOMAIN and POLICY_AUD to the deploy")
            with open(args.env_out, "a") as fh:
                fh.write(f"TEAM_DOMAIN={domain}\nPOLICY_AUD={aud}\n")
    except ApiError as err:
        sys.exit(f"internal_access: {err}")


if __name__ == "__main__":
    main()
