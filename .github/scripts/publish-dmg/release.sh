#!/usr/bin/env bash
# Create the GitHub Release from dist/; refuses to overwrite an existing tag.
# Env: GH_TOKEN, GH_REPO, VERSION, PRERELEASE, DRAFT, GITHUB_SHA, optional GITHUB_STEP_SUMMARY.
# Run through make (see the dmg-* targets); publish-dmg.yml calls the same targets.
set -euo pipefail
if gh release view "$VERSION" >/dev/null 2>&1; then
  echo "::error::release $VERSION already exists; refusing to overwrite"
  exit 1
fi
versioned=(dist/Blowhorn-*-mac-*.dmg)
{
  if [[ -s dist/notes.md ]]; then cat dist/notes.md; echo; echo; fi
  echo "## Download"
  echo
  echo "- macOS: \`$(basename "${versioned[0]}")\`"
  echo "- Download: https://github.com/${GH_REPO}/releases/download/${VERSION}/$(basename "${versioned[0]}")"
  echo
  echo "## SHA-256"
  echo
  echo '```'
  cat dist/SHA256SUMS.txt
  echo '```'
} >release-notes.md
flags=(--title "Blowhorn ${VERSION}" --notes-file release-notes.md --target "${GITHUB_SHA}")
[[ "$DRAFT" == "true" ]] && flags+=(--draft)
if [[ "$PRERELEASE" == "true" ]]; then
  flags+=(--prerelease --latest=false)
else
  flags+=(--latest)
fi
gh release create "$VERSION" "${flags[@]}" dist/*.dmg dist/SHA256SUMS.txt
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  echo "### Release ${VERSION} created (draft=${DRAFT}, prerelease=${PRERELEASE})" >>"$GITHUB_STEP_SUMMARY"
  if [[ "$DRAFT" != "true" && "$PRERELEASE" != "true" ]]; then
    echo "The pin job sets data/download.json to ${VERSION#v} and redeploys blowhorn.ai." >>"$GITHUB_STEP_SUMMARY"
  fi
fi
