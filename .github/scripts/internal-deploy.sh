#!/usr/bin/env bash
# Deploy public-internal/ to the blowhorn-internal Worker (internal-worker/).
# Usage: internal-deploy.sh   (needs CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID,
# TEAM_DOMAIN and POLICY_AUD; the last two come from internal_access.py ensure)
#
# This runs in a public repository's Actions log. wrangler's own output lists
# bindings and can name asset files, so it goes to a private temp file and
# only an allow-listed summary is printed. Never add set -x here.
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
: "${TEAM_DOMAIN:?run internal_access.py ensure first}"
: "${POLICY_AUD:?run internal_access.py ensure first}"
: "${CLOUDFLARE_API_TOKEN:?}" "${CLOUDFLARE_ACCOUNT_ID:?}"
WRANGLER_VERSION="${WRANGLER_VERSION:-4.151.3}"
test -f "$root/public-internal/internal/index.html" || { echo "internal-deploy: public-internal/ has no internal build; run make site-internal-build first" >&2; exit 1; }
# The same loader as internal_access.py ensure, so the Worker's allow list
# includes the extras from the secret. Its stdout is captured, so anything it
# prints (the ::add-mask:: lines under Actions) goes to stderr instead. Only
# the two lists come back, and they are never echoed.
access_lists="$(python3 -c '
import contextlib, os, sys
sys.path.insert(0, os.path.join(sys.argv[1], ".github", "scripts"))
import internal_access as ia
with contextlib.redirect_stdout(sys.stderr):
    cfg = ia.load_config(sys.argv[2], require_extras=True)
print(",".join(cfg["allowed_emails"]))
print(",".join(cfg["allowed_email_domains"]))
' "$root" "$root/internal-worker/access.json")"
{ IFS= read -r emails; IFS= read -r domains; } <<<"$access_lists"
log="$(mktemp)"
trap 'rm -f "$log"' EXIT
export WRANGLER_SEND_METRICS=false CI=true
set +e
(cd "$root/internal-worker" && npx --yes "wrangler@$WRANGLER_VERSION" deploy \
  --var "TEAM_DOMAIN:$TEAM_DOMAIN" --var "POLICY_AUD:$POLICY_AUD" \
  --var "ALLOWED_EMAILS:$emails" --var "ALLOWED_EMAIL_DOMAINS:$domains") >"$log" 2>&1
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  echo "internal-deploy: wrangler deploy failed (exit $rc). Cloudflare error codes, if any:" >&2
  grep -oE '\[code: [0-9]+\]|Authentication error|not authorized|permission' "$log" | sort -u >&2 || true
  echo "internal-deploy: reproduce locally (make site-internal-build, then this script) to see the full output." >&2
  exit "$rc"
fi
grep -E '^(Total Upload|Worker Startup Time|Uploaded blowhorn-internal|Deployed blowhorn-internal|Current Version ID)|Success! Uploaded [0-9]+ files|\(custom domain\)' "$log" || true
echo "internal-deploy: deployed"
