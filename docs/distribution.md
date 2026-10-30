# Distributing Blowhorn

This repository is the public distribution point for Blowhorn builds. Product
source and build pipelines stay in the private product repository; only finished,
signed artifacts are published here.

## Where binaries live

**GitHub Releases on `blowhorn-ai/blowhorn-site`.** Disk images are never committed
to git (`*.dmg` is in `.gitignore`), and they are not served from GitHub Pages.
Pages hosts only the marketing site and small static files.

| What | Where |
|------|-------|
| Marketing site | GitHub Pages, built by Hugo from this repo, at <https://blowhorn.ai> (see [deploy.md](deploy.md)) |
| macOS DMG | Release asset on this repo |
| Checksums | `SHA256SUMS.txt` attached to each release |
| Update manifest (later) | Release asset next to the DMG (for example `latest-mac.yml` for electron-updater, or a Sparkle `appcast.xml`) |

## Release conventions

- **Tag:** `vMAJOR.MINOR.PATCH`, for example `v1.0.0`. A hyphenated suffix
  (`v1.1.0-beta.1`) makes it a GitHub prerelease, which is never marked "latest".
- **Assets per release:**
  - `Blowhorn-<version>-mac-<arch>.dmg`, where `<arch>` is `universal`, `arm64`, or `x64`
  - `Blowhorn-mac.dmg`, a copy of the same file under a fixed name (not linked from the site)
  - `SHA256SUMS.txt`
- **Download URL** (used by the site): the versioned disk image of the current
  desktop release,

  ```
  https://github.com/blowhorn-ai/blowhorn-site/releases/download/v<version>/Blowhorn-<version>-mac-universal.dmg
  ```

  A browser saves the file under the last segment of the URL, so linking the
  versioned asset puts the version in the name of the file a visitor downloads
  from blowhorn.ai. The site never links `Blowhorn-mac.dmg`
  (`check_download_links.py` fails the build if it does); the alias stays on
  every release for the app's update check and for scripts that want a fixed name.

  The version is pinned in `data/download.json`. `publish-dmg.yml` bumps it
  on master and redeploys the site after every public release (its `pin`
  job, `make dmg-pin-download`); a draft published by hand later needs the
  same `make dmg-pin-download` run, or a one-line PR. Never build a download link on
  `/releases/latest`: this repository also publishes blowhorn-axi and
  blowhorn-mcp releases (`axi-vX.Y.Z`, `mcp-vX.Y.Z`), GitHub resolves `latest`
  to whichever stable release was created most recently, and the always-latest
  URL 404s whenever one of those is the newest. The site's Download section
  (`assets/js/download.js`) reads the release list from GitHub's API in the
  visitor's browser and fills in the newest desktop release by the same rule
  the app's update check uses (the newest non-draft, non-prerelease release
  whose tag is exactly `vX.Y.Z` and which carries `Blowhorn-mac.dmg`), so an
  outage or rate limit only means the pinned version's details show, never a
  dead link.
- **Versioned URL:**
  `https://github.com/blowhorn-ai/blowhorn-site/releases/download/v1.0.0/Blowhorn-1.0.0-mac-universal.dmg`
- Releases are never overwritten. Ship a new patch version instead.

## Publishing a DMG

The DMG must already be built, signed with a Developer ID certificate, notarized,
and stapled before it reaches this repo. That happens in the product repo's
build pipeline. The workflow enforces it: **a public release (`draft=false`)
must have `require_notarized=true`**, which runs `codesign`, `spctl` and
`stapler validate` on a macOS runner and refuses to publish on failure. Only a
draft may skip verification, so an unverified image can be reviewed but never
published by the workflow.

### Option A: manual run here

1. Put the DMG at an HTTPS URL the runner can download (for example a release
   asset or a presigned object-storage URL).
2. Actions > **Publish DMG release** > **Run workflow**, then fill in `version`
   and `dmg_url`. Leave `draft` checked to review before publishing.
3. Leave `require_notarized` checked (the default). Untick it only for a draft
   of an unsigned test image; the workflow refuses `draft=false` without it.
4. Review the draft release and publish it.

If `dmg_url` needs a bearer token (for example a GitHub API asset URL on a
private repo, with `Accept: application/octet-stream`), store it as the
`DMG_SOURCE_TOKEN` repository secret. The token is attached only when
`dmg_url` begins with `https://api.github.com/`, `https://github.com/`,
`https://objects.githubusercontent.com/` or
`https://release-assets.githubusercontent.com/`: a literal prefix, so the host
must be followed directly by the path. Any other HTTPS URL is downloaded
without credentials, so a `dmg_url` pointing at an unexpected host cannot
exfiltrate the secret. The download and every redirect must stay on HTTPS;
`curl` is told to refuse anything else.

Runs are serialised (`concurrency: publish-dmg`): a second dispatch waits for
the running one to finish rather than cancelling it.

### Option B: triggered from product CI

After it signs and notarizes, the product pipeline sends a `repository_dispatch`
event to this repo. This needs a token that can write to `blowhorn-ai/blowhorn-site`
(a GitHub App installation token or a fine-grained token with Contents: write),
stored as a secret in the product repo:

```bash
gh api repos/blowhorn-ai/blowhorn-site/dispatches \
  -f event_type=publish-dmg \
  -F 'client_payload[version]=v1.0.0' \
  -F 'client_payload[dmg_url]=https://example.com/Blowhorn-1.0.0.dmg' \
  -F 'client_payload[arch]=universal' \
  -F 'client_payload[draft]=true' \
  -F 'client_payload[require_notarized]=true'
```

The same `publish-dmg.yml` workflow runs, so validation, naming, and checksums
are identical for both paths.

### Option C: direct upload from product CI

The product pipeline can also run `gh release create` against this repo with
the same token. It must follow the asset naming above (including the
`Blowhorn-mac.dmg` alias and `SHA256SUMS.txt`) so the pinned download URLs keep
working, pass `--latest`, and bump `data/download.json` in the same pass.
Prefer Option B so the naming rules live in one place.

## Chrome extension

The Blowhorn Chrome extension is published to the Chrome Web Store, not
distributed from this repo. CI publishes it with a
[Chrome Web Store service account](https://developer.chrome.com/docs/webstore/service-accounts).
That plan is tracked with the product repo's productization work.

## Local checks

```bash
make site-check                        # production build into public/ (the Pages artifact), then its checks
make site                              # http://localhost:1313 with live reload
make workflow-check                    # actionlint on this repo's workflows
make dmg-check DMG=path/to/file.dmg    # UDIF sanity check before publishing
```

Each step of `publish-dmg.yml` that runs repository logic is a make target backed
by a script in `.github/scripts/publish-dmg/`, and the workflow calls the target.
The targets read their inputs from the environment, exactly as the workflow sets
them, so a step can be rehearsed locally:

| Target | Inputs | Does |
|---|---|---|
| `dmg-resolve` | `IN_VERSION`, `IN_URL`, `IN_ARCH`, `IN_DRAFT`, `IN_NOTARIZED`, optional `IN_NOTES`, `GITHUB_OUTPUT` | validates the inputs, refuses a public release that skips verification, writes `notes.md` |
| `dmg-download` | `DMG_URL`, optional `DMG_SOURCE_TOKEN` | downloads to `dist/source.dmg` over HTTPS only; the token goes only to GitHub hosts |
| `dmg-package` | `VERSION`, `ARCH`, and the `notes.md` that `dmg-resolve` wrote | runs `check-dmg.sh`, names the versioned and `Blowhorn-mac.dmg` assets, writes `SHA256SUMS.txt`, moves `notes.md` into `dist/` |
| `dmg-verify` | (macOS only) | `hdiutil verify`, `codesign`, `spctl` and `stapler validate` on each DMG in `dist/` |
| `dmg-release` | `GH_TOKEN`, `GH_REPO`, `VERSION`, `PRERELEASE`, `DRAFT`, `GITHUB_SHA`, optional `GITHUB_STEP_SUMMARY` | creates the release; refuses an existing tag |

```bash
GITHUB_OUTPUT=/tmp/out IN_VERSION=v1.2.3 IN_URL=https://example.com/Blowhorn.dmg \
  IN_DRAFT=true IN_NOTARIZED=true make dmg-resolve   # rehearse input validation
```

`dmg-resolve` needs bash 4 or newer (macOS ships 3.2; `brew install bash`).

`publish-blowhorn-axi.yml`, which publishes blowhorn-axi and blowhorn-mcp to
npm, works the same way: its steps are `npm-fetch`, `npm-verify`,
`npm-publish` and `npm-confirm`, backed by `.github/scripts/publish-npm/`.
