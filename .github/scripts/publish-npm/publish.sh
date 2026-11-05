#!/usr/bin/env bash
# Publish the verified tarball with npm trusted publishing (OIDC) and a
# provenance attestation; a missing OIDC token fails instead of publishing without one.
# Env: TARBALL (from npm-fetch via GITHUB_ENV); optional DIST_TAG (default latest).
# Run through make (see the npm-* targets); publish-blowhorn-axi.yml calls the same targets.
set -e
npm publish "./$TARBALL" --access public --provenance --tag "${DIST_TAG:-latest}"
