#!/usr/bin/env bash
# Confirm the registry lists PACKAGE@VERSION. The registry can take a few
# minutes to list a new version. Poll for about 5 minutes (10s growing to 30s
# between attempts), then warn; never fails the job over propagation delay.
# Env: PACKAGE, VERSION.
# Run through make (see the npm-* targets); publish-blowhorn-axi.yml calls the same targets.
# -e only, as GitHub Actions runs an inline step (bash -e); no -u or pipefail.
set -e
waited=0
delay=10
attempt=1
while :; do
  echo "Attempt $attempt (${waited}s elapsed): npm view $PACKAGE@$VERSION version"
  if npm view "$PACKAGE@$VERSION" version; then exit 0; fi
  [ "$waited" -ge 300 ] && break
  sleep "$delay"
  waited=$((waited + delay))
  attempt=$((attempt + 1))
  delay=$((delay + 5 > 30 ? 30 : delay + 5))
done
echo "::warning::The publish step succeeded, but the registry did not list $PACKAGE@$VERSION within ${waited}s. It is usually propagation delay; check later with: npm view $PACKAGE@$VERSION version"
