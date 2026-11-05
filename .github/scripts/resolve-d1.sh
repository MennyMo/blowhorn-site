#!/usr/bin/env bash
# Point a worker's wrangler.json at its D1 databases.
# Usage: resolve-d1.sh <worker-dir>
#
# Every database_id committed in wrangler.json is a placeholder: the real id
# only exists once the database is created in Cloudflare, which this script
# does (wrangler d1 create) for any d1_databases entry whose name
# `wrangler d1 list` does not already show. Every entry is resolved, so a
# worker can bind more than one database (the internal worker binds the
# signups database and the fleet stats database).
# The script is quiet by design: the caller's repository logs are public,
# so it prints one line and nothing that names account resources.
set -euo pipefail
dir="${1:?usage: resolve-d1.sh <worker-dir>}"
: "${CLOUDFLARE_API_TOKEN:?}" "${CLOUDFLARE_ACCOUNT_ID:?}"
WRANGLER_VERSION="${WRANGLER_VERSION:-4.151.3}"
log="$(mktemp)"
trap 'rm -f "$log"' EXIT
export WRANGLER_SEND_METRICS=false CI=true
fail_log() {
  # Print wrangler's own error lines, with long identifiers redacted: the
  # caller's repository logs are public.
  grep -iE 'error|failed|unknown argument|invalid' "$log" | sed -E 's/[0-9a-f]{32}/<id>/g; s/[A-Za-z0-9_-]{40}/<token>/g' | head -10 >&2 || true
}
list_dbs() {
  (cd "$dir" && npx --yes "wrangler@$WRANGLER_VERSION" d1 list --json >"$log" 2>&1) ||
    { echo "resolve-d1: d1 list failed" >&2; fail_log; exit 1; }
}
# Names in wrangler.json that the last list did not show, one per line.
missing() {
  python3 - "$dir/wrangler.json" "$log" <<'PY'
import json, sys
want = [d["database_name"] for d in json.load(open(sys.argv[1])).get("d1_databases", [])]
data = json.load(open(sys.argv[2]))
dbs = data if isinstance(data, list) else data.get("d1_databases", [data])
have = {db.get("name") for db in dbs if isinstance(db, dict) and db.get("uuid")}
for name in want:
    if name not in have:
        print(name)
PY
}
list_dbs
created=0
while IFS= read -r name; do
  [ -n "$name" ] || continue
  # d1 create takes no --json flag in this wrangler version, so ids are read
  # back from a second list call instead of from create's output.
  (cd "$dir" && npx --yes "wrangler@$WRANGLER_VERSION" d1 create "$name" >"$log.create" 2>&1) ||
    { mv -f "$log.create" "$log"; echo "resolve-d1: d1 create failed" >&2; fail_log; exit 1; }
  rm -f "$log.create"
  created=1
done < <(missing)
[ "$created" -eq 0 ] || list_dbs
python3 - "$dir/wrangler.json" "$log" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(sys.argv[2]))
dbs = data if isinstance(data, list) else data.get("d1_databases", [data])
ids = {db["name"]: db["uuid"] for db in dbs if isinstance(db, dict) and db.get("name") and db.get("uuid")}
doc = json.load(open(path))
for entry in doc.get("d1_databases", []):
    new_id = ids.get(entry["database_name"])
    if not new_id:
        print("resolve-d1: no database id found", file=sys.stderr)
        sys.exit(1)
    entry["database_id"] = new_id
with open(path, "w") as f:
    json.dump(doc, f, indent=2)
    f.write("\n")
PY
echo "resolve-d1: database ready"
