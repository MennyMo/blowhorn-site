#!/usr/bin/env bash
# Download the Blowhorn DMG of a release of this repository (RELEASE_TAG, or the
# latest), check it against the release's SHA256SUMS.txt, and mount it read-only
# at $MOUNT. Prints the engine directory and, on Actions, exports ENGINE and
# BLOWHORN_VERSION for later steps. macOS only (hdiutil).
set -euo pipefail
repo="${GITHUB_REPOSITORY:-blowhorn-ai/blowhorn-site}"
work="${RUNNER_TEMP:-$(mktemp -d)}"
mount="${MOUNT:-$work/blowhorn-dmg}"
tag="${RELEASE_TAG:-}"
if [ -z "$tag" ]; then
  tag="$(gh release view -R "$repo" --json tagName --jq .tagName)"
fi
cd "$work"
rm -f Blowhorn-*-mac-*.dmg SHA256SUMS.txt
gh release download "$tag" -R "$repo" -p 'Blowhorn-*-mac-universal.dmg' -p SHA256SUMS.txt --clobber
dmg="$(ls Blowhorn-*-mac-universal.dmg | head -1)"
grep " ${dmg}\$" SHA256SUMS.txt | shasum -a 256 -c -
mkdir -p "$mount"
hdiutil attach "$dmg" -nobrowse -readonly -noautoopen -mountpoint "$mount" >/dev/null
engine="$mount/Blowhorn.app/Contents/Resources/engine"
test -x "$engine/bin/python" || { echo "no bundled engine in $dmg" >&2; exit 1; }
version="${tag#v}"
echo "release $tag: engine at $engine"
if [ -n "${GITHUB_ENV:-}" ]; then
  { echo "ENGINE=$engine"; echo "BLOWHORN_VERSION=$version"; } >> "$GITHUB_ENV"
fi
