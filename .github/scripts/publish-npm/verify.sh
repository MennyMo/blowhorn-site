#!/usr/bin/env bash
# Check the fetched tarball before publishing: optional sha256, package name,
# version, repository.url (provenance needs blowhorn-ai/blowhorn-site), and
# that the version is not already on npm. Writes pkg.json in the working directory.
# Env: PACKAGE, VERSION, TARBALL (from npm-fetch via GITHUB_ENV); optional SHA256.
# Run through make (see the npm-* targets); publish-blowhorn-axi.yml calls the same targets.
set -euo pipefail
if [ -n "$SHA256" ]; then echo "$SHA256  $TARBALL" | sha256sum -c -; fi
tar -xzf "$TARBALL" package/package.json -O > pkg.json
name=$(node -p "require('./pkg.json').name")
ver=$(node -p "require('./pkg.json').version")
repo=$(node -p "(require('./pkg.json').repository||{}).url||''")
[ "$name" = "$PACKAGE" ] || { echo "::error::tarball is $name, not $PACKAGE"; exit 1; }
[ "$ver" = "$VERSION" ] || { echo "::error::tarball is version $ver, input is $VERSION"; exit 1; }
case "$repo" in *github.com/blowhorn-ai/blowhorn-site*) ;; *) echo "::error::repository.url ($repo) must be blowhorn-ai/blowhorn-site for provenance"; exit 1;; esac
if npm view "$PACKAGE@$VERSION" version >/dev/null 2>&1; then echo "::error::$PACKAGE@$VERSION is already published"; exit 1; fi
tar -tzf "$TARBALL"
sha256sum "$TARBALL"
