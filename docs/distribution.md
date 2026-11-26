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
  `/releases/latest`: this repository also publishes blowhorn-axi releases
  (`axi-vX.Y.Z`), GitHub resolves `latest`
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

## Building the desktop DMG

The signed disk image is built on this repository's free `macos-26` runner
by `.github/workflows/build-dmg.yml`, not on a maintainer's Mac. The image is
pinned, not `macos-latest`, so a label migration cannot change the OS or its
Xcodes under a release. `.github/actions/build-dmg-mac` sets `DEVELOPER_DIR`
to `/Applications/Xcode_26.3.app`: actool compiles the app's Icon Composer icon
during packaging, and the image's default Xcode 26.6 (like 26.4.1 and 26.5)
fails on it with "Could not open Icon.icon", while 26.0.1 through 26.3 and
27.0 through 27.2 compile it (27 so far runs only on the preview `xcode-27`
image). If an image update drops Xcode 26.3, the step fails naming the setting
to change; move it to another Xcode from that list.

**Preferred entry:** publish a public GitHub release on this repository whose
tag is `vX.Y.Z` (optional prerelease suffix, schema:
`.github/schemas/desktop-release-published.schema.json`). That fires
`release-desktop.yml`, which only validates the tag and the publisher, then
dispatches `cut-desktop-release.yml` with `--ref master`. The master run
bumps and tags `desktop-vX.Y.Z` in the private product repository, calls
`build-dmg.yml` for Linux gates and the signed DMG, and attaches the image
to both the private `desktop-vX.Y.Z` release and this public `vX.Y.Z`
release. `axi-v*` publishes are skipped; any other tag is rejected.

The published-release run's `github.ref` is the tag, not `master`, so
`release-desktop.yml` does not run the signed job and does not see
`BLOWHORN_RELEASE_TOKEN` or the signing secrets. Those stay on the
master-pinned `cut-desktop-release.yml` run, which is what
`macos-dmg-signing`'s master-only policy applies to.
`BLOWHORN_RELEASE_TOKEN` is a blowhorn-ai organization secret, selected
for the `blowhorn` and `blowhorn-site` repositories, and is passed only
to the steps that push to the private product repository (the product
checkout and the private release attach).

`make release` in the product repository can still bump, tag and dispatch
`build-dmg.yml` from a laptop (the previous default). `make release LOCAL_SIGN=1`
remains the local sign and notarize fallback. `make release-request VERSION=X.Y.Z`
creates and publishes the public `vX.Y.Z` release, which is enough to start
the preferred path.

**Triggers for `build-dmg.yml`:** `workflow_dispatch`, `repository_dispatch`
with event type `build-dmg`, and `workflow_call` from
`cut-desktop-release.yml`. The workflow does not run on `pull_request` or
`push`. Linux gates (`product-ci.yml`) run first on `ubuntu-latest`, then
the Mac job builds the image.

**Modes:** `adhoc` is an unsigned timing build. `developer-id` signs, notarizes
and staples. A signed run is allowed only when the product commit is the one
named by `desktop-vVERSION` or `refs/releases/desktop-vVERSION`.

**Environment:** signed jobs use the `macos-dmg-signing` environment, which is
restricted to this repository's `master` branch (a custom policy, because
`master` is not a protected branch). Pull requests, forks and other branches
cannot reach it. There are no required reviewers: a signed run on `master`
proceeds without an approval. That is Yi Nuo's call: any team member listed
in the Firstmate roster can initiate a release on their own recognizance.
Signing secret values are blowhorn-ai organization secrets, selected for
the `blowhorn` and `blowhorn-site` repositories: `DEVELOPER_ID_P12`,
`DEVELOPER_ID_P12_PASSPHRASE`, `APPLE_API_KEY`, `APPLE_TEAM_ID`,
`APPLE_API_KEY_ID`, and `APPLE_API_ISSUER`. They resolve in the
`macos-dmg-signing` environment job even though that environment has no
environment-scoped secrets. The workflow does not load keys from the
private product repository. The #2759 rotation was canceled; the existing
keys were moved unrotated to those org secrets.
`BLOWHORN_DIAGNOSTICS_KEY` is a `blowhorn-site` repository secret. The
signed job passes it only to the staging step (not as job-level env, not
as an input to `build-dmg-mac`, and never on the adhoc job or on pull
requests). That step writes the key under `RUNNER_TEMP`; the packaging
step loads the file so rustup, setup-node and pnpm do not inherit it.
A signed release fails if the key is missing, because the app could not
send support cases or failure reports.

**Artifacts:** the only uploads are the DMG and its sha256 manifest, retained for
1 day, and, when a Linux gate or a Mac job fails, that job's log as `age`
ciphertext (below), retained for 3 days. The Mac build's full log stays under
`RUNNER_TEMP` and is never printed, cached or uploaded as plaintext. The public log shows only
fixed phase labels with UTC start and end times (keychain import is limited
to 5 minutes, the build to 100 minutes, inside the 120-minute job), release
phase names, and the notarization submission id and status. Private source
is checked out sparsely, with internal paths excluded. The Mac job caches
the Cargo registry and git sources, keyed on `Cargo.lock` and the exact
`rustc` version, and does not cache `engine/rust/target`.

### Reading a failed Product CI log

The Linux gates (`product-ci.yml`, run on its own or by `build-dmg.yml`) print
only step results, counts and failing test ids, because this repository's logs
are public. When a suite fails, `.github/scripts/product-ci/run.py` encrypts
its full log with [age](https://age-encryption.org) to the public recipient
`LOG_RECIPIENT` in `.github/scripts/encrypted-log/encrypted_log.py`, and the job uploads only the ciphertext as the
artifact `product-ci-<suite>-log-attempt<n>`, kept 3 days. The public log says
so in one line (`Encrypted log: available as artifact ...`). A passing suite
uploads nothing, and a runner without `age` says so and uploads nothing.

The private key is never in a repository, a secret or a runner; a maintainer
who holds it reads a log with:

```bash
make product-ci-log RUN=<run id> SUITE=python   # KEY=<identity file>, default ~/.config/blowhorn/ci-log.agekey
```

The target downloads the artifact (the latest attempt, or `ATTEMPT=<n>`) with
`gh run download` into a new temporary directory outside the repository,
decrypts it there, deletes the ciphertext and prints the plaintext file's path,
never its contents. The log holds private product code: read it locally, never
paste it into an issue, pull request or chat, and delete the directory when done.

### Reading a failed Build DMG log

The Mac jobs (`Mac signed build`, `Mac adhoc build`) print only fixed phase
labels and the failed sub-step's public name, such as `build: failed step:
electron-builder (exit 1)`. Each phase that runs product code writes its whole
output to a private log under `RUNNER_TEMP/build-dmg/`: `install.log` (the
desktop package install), `import.log` (the signing keychain import, signed
job only) and `build.log` (preflight, the build, packaging, signing,
notarization and the DMG verify). When any step of the job fails,
`make build-dmg-encrypt-log` (`.github/scripts/build-dmg/encrypt_logs.py`)
joins the logs that exist, each under a `===== <name> =====` header, and
encrypts them to the same `LOG_RECIPIENT`. The job uploads only that ciphertext
as `build-dmg-<signed|adhoc>-log-attempt<n>`, kept 3 days. A passing job
uploads nothing, and without `age` (installed with Homebrew at the start of
each Mac job, optional) or when encryption fails, the job prints
`Encrypted log: none (<reason>).` and uploads nothing.

What the log can contain: the product's build output (source paths, test
names and failures, compiler, pnpm, electron-builder, codesign, notarytool and
`hdiutil` output), the commands the build runs with their arguments, file
paths under `RUNNER_TEMP`, and Apple's public identifiers (team id, App Store
Connect key id and issuer), which signed binaries and notarization logs carry
anyway. It never holds key material. The build does not print any: the
keychain import passes the p12 passphrase only as an argument to `security`,
`release-mac.mjs` logs the notarytool command with the `.p8` key's path, never
its contents, and the diagnostics key hook says only that it wrote the key. As
a second guard, before encrypting, every line holding the value of a secret the
signed job staged (the p12 passphrase, the `.p8` key, the temporary keychain's
password, the diagnostics key, and the p12 in its base64 forms) is replaced
with a fixed marker, and the public log says how many lines were removed. A
staged secret shorter than 8 characters cannot be matched safely, so the job
uploads nothing rather than guess.

A key holder reads it the same way:

```bash
make build-dmg-log RUN=<run id> JOB=adhoc   # or JOB=signed; KEY=<identity file>, ATTEMPT=<n>
```

## Building the Windows preview installer

`build-windows.yml` builds an early-tester Windows installer (per-user, x64, Rust engine only) on the free `windows-latest` runner. It is manual only:

```sh
gh workflow run build-windows.yml -f ref=<product commit sha> -f version=<X.Y.Z>
```

- It runs the same Linux gates as the DMG build first, then checks the private product out sparsely with the read-only `DMG_SOURCE_TOKEN`, as the DMG build does.
- The installer is signed with one self-signed development certificate. Its private key and password are the `WINDOWS_PREVIEW_CERT_PFX_BASE64` and `WINDOWS_PREVIEW_CERT_PASSWORD` secrets of the `windows-preview-signing` environment, passed to the build step alone. Only the public `.cer` is ever published. Testers see SmartScreen once and choose "More info", then "Run anyway".
- Build output goes to a log under `RUNNER_TEMP` that is never printed, uploaded or cached. The only artifact is the installer and its `.sha256`, kept 1 day.
- A second job, `smoke-windows`, downloads that artifact on a fresh Windows runner and runs `.github/scripts/build-windows/smoke.py`: a silent install into a throwaway folder, the packaged engine answering `--version`, `config show` and `platforms capabilities --json` with every user folder pointed at throwaway ones, and the uninstaller. It prints a label and ok or failed per check and never the product's output. It holds no secret. The native host registration and Chrome connecting to the extension over a throwaway profile are not in it yet.
- A published preview is a GitHub pre-release named "Blowhorn for Windows (preview)" with short install notes. It never moves the site's download pin.

## Publishing a DMG

The DMG must already be built, signed with a Developer ID certificate, notarized,
and stapled before it is published (see [Building the desktop DMG](#building-the-desktop-dmg)).
The publish workflow enforces it: **a public release (`draft=false`)
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

`publish-blowhorn-axi.yml`, which publishes blowhorn-axi to npm, works the same
way (blowhorn-mcp publishes from its own repository,
https://github.com/blowhorn-ai/blowhorn-mcp, with that repository's
`publish.yml`): its steps are `npm-fetch`, `npm-verify`,
`npm-publish` and `npm-confirm`, backed by `.github/scripts/publish-npm/`.
