#!/usr/bin/env bash
# Fetch <package>-<version>.tgz into the working directory and hand its name to
# later steps as TARBALL in GITHUB_ENV.
# Env: PACKAGE (blowhorn-axi or blowhorn-mcp), VERSION, GITHUB_ENV; optional
# TARBALL_URL (HTTPS), else RELEASE_TAG (default v<version> for blowhorn-axi,
# mcp-v<version> for blowhorn-mcp) with GH_TOKEN and GITHUB_REPOSITORY.
# Run through make (see the npm-* targets); publish-blowhorn-axi.yml calls the same targets.
set -euo pipefail
case "$PACKAGE" in
  blowhorn-axi) default_tag="v$VERSION" ;;
  blowhorn-mcp) default_tag="mcp-v$VERSION" ;;
  *) echo "::error::package must be blowhorn-axi or blowhorn-mcp, got $PACKAGE"; exit 1 ;;
esac
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]] || { echo "::error::version must be X.Y.Z[-pre], got $VERSION"; exit 1; }
file="${PACKAGE}-${VERSION}.tgz"
if [ -n "$TARBALL_URL" ]; then
  [[ "$TARBALL_URL" == https://* ]] || { echo "::error::tarball_url must be HTTPS"; exit 1; }
  curl --fail --location --proto '=https' --proto-redir '=https' --max-time 120 -sS -o "$file" "$TARBALL_URL"
else
  tag="${RELEASE_TAG:-$default_tag}"
  gh release download "$tag" -R "$GITHUB_REPOSITORY" -p "$file" -O "$file"
fi
echo "TARBALL=$file" >> "$GITHUB_ENV"
