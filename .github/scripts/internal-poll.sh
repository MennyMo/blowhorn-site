#!/usr/bin/env bash
# Decide whether internal-site-auto.yml deploys the internal site, and at
# which blowhorn-ai/blowhorn ref.
#   push, workflow_dispatch: always deploy, at BLOWHORN_REF (default master).
#   schedule: deploy blowhorn master's current SHA when any path the internal
#     build mounts has a commit on master in the last WINDOW_HOURS (default 0.5).
#     Needs DMG_SOURCE_TOKEN (read access to blowhorn-ai/blowhorn).
# Env: EVENT (github.event_name), BLOWHORN_REF, DMG_SOURCE_TOKEN, WINDOW_HOURS.
# Writes should_deploy and blowhorn_ref to $GITHUB_OUTPUT (stdout when unset).
# This repository is public: prints one summary line of counts, path prefixes
# and the SHA, never a commit message, author or file name.
set -euo pipefail
repo="${BLOWHORN_REPO:-blowhorn-ai/blowhorn}"
out="${GITHUB_OUTPUT:-/dev/stdout}"
# The sparse-checkout list in internal-site.yml.
paths=(
  marketing/strategy
  marketing/capability-comparison
  marketing/brand
  marketing/assets.manifest.json
  internal/engineering
  internal/design
  internal/specs
  internal/plans
  internal/research
)

emit() { printf 'should_deploy=%s\nblowhorn_ref=%s\n' "$1" "$2" >> "$out"; }

event="${EVENT:-}"
if [ "$event" != schedule ]; then
  ref="${BLOWHORN_REF:-master}"
  emit true "$ref"
  echo "Deploy: ${event:-manual} run, blowhorn ref $ref."
  exit 0
fi

if [ -z "${DMG_SOURCE_TOKEN:-}" ]; then
  echo "::error::DMG_SOURCE_TOKEN is not set on blowhorn-ai/blowhorn-site, so the scheduled poll cannot read $repo and product changes will never redeploy internal.blowhorn.ai. Add the secret (read access to $repo) or remove the schedule."
  exit 1
fi
command -v gh > /dev/null || { echo "::error::gh not found."; exit 1; }
export GH_TOKEN="$DMG_SOURCE_TOKEN"

window="${WINDOW_HOURS:-0.5}"
since="$(python3 -c 'import datetime,sys; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=float(sys.argv[1]))).strftime("%Y-%m-%dT%H:%M:%SZ"))' "$window")"

# Pin the SHA first, then ask about history up to it, so the ref deployed is
# the one the answer was about.
sha="$(gh api "repos/$repo/commits/master" --jq .sha 2>/dev/null)" || sha=""
if ! [[ "$sha" =~ ^[0-9a-f]{40}$ ]]; then
  echo "::error::Could not read $repo master with DMG_SOURCE_TOKEN (expired, or no read access?)."
  exit 1
fi

changed=()
for p in "${paths[@]}"; do
  n="$(gh api "repos/$repo/commits?sha=$sha&path=$p&since=$since&per_page=1" --jq length 2>/dev/null)" || n=""
  if ! [[ "$n" =~ ^[0-9]+$ ]]; then
    echo "::error::Could not list $repo commits on $p with DMG_SOURCE_TOKEN."
    exit 1
  fi
  [ "$n" -eq 0 ] || changed+=("$p")
done

if [ "${#changed[@]}" -gt 0 ]; then
  emit true "$sha"
  echo "Deploy: ${#changed[@]} of ${#paths[@]} mounted paths changed on $repo master since $since (${changed[*]}); blowhorn ref $sha."
else
  emit false ""
  echo "Skip: no mounted path changed on $repo master since $since (master is $sha)."
fi
