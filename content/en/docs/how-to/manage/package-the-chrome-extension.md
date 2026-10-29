---
title: "Package the Chrome extension"
description: "Build the store zip locally; submission happens at release time."
weight: 200
draft: true
aliases: [/docs/how-to/package-the-chrome-extension/]
---


Build the zip of the Google Chrome extension for the Chrome Web Store. `make extension-package` only
builds it. The desktop release submits it when this extension, or the
native-messaging contract it has to match, changed. Submitting does not skip
Google's review, and it does not open Chrome.

```bash
make extension-package
```

That runs `release/scripts/package_extension.py` and writes `dist/blowhorn-extension.zip`.
`manifest.json` is at the root of the zip. The copy inside the zip has no
`key`. The manifest in `extension/` keeps `key`, so an unpacked load stays on
the same id.

The zip is the extension directory only. It leaves out `.git`, `node_modules`,
`venv`, `.env`, source maps, `tests`, `docs`, `profiles`, `desktop`,
`README.md`, `CHROMEWEBSTORE.md`, `.DS_Store`, `store-assets`, and `chrome-web-store`. Listing
images live in `marketing/assets/store/chrome-web-store/` and are uploaded in the dashboard, not inside
the zip. The script adds the repo-root `LICENSE` (AGPL-3.0-only) at the zip root. A private key in the source tree stops the script before it writes
the archive.

`extension/icon16.png`, `icon32.png`, `icon48.png` and `icon128.png` are the
desktop app icon (`desktop/assets/app-icon.png`, sized copies in
`desktop/assets/blowhorn-icon-set/`) at those sizes. The manifest names them.
The listing images - five 1280 x 800 screenshots, the 440 x 280 promo tile
and the 1400 x 560 marquee - live in `marketing/assets/store/chrome-web-store/`; the Graphic assets table
in `marketing/assets/store/chrome-web-store/LISTING.md` in the product repository names each file and
its dashboard slot, beside the paste-ready summary and description. A
HyperFrames global promo (storyboard + script for HeyGen) lives at
`marketing/assets/store/chrome-web-store/hyperframes/global-promo/` in the product repository.

## Rebuild the listing graphics

Rebuild them after the brand kit, the console or its platform marks change:

```bash
make desktop-install          # once: the desktop dependencies the capture launches
make extension-assets-build   # rewrites every image in marketing/assets/store/chrome-web-store/
```

`make extension-assets-build` runs `tools/scripts/brand/build-store-assets.py`. It
rebuilds the desktop app, launches it against a showcase engine - a stand-in
checkout that answers the console's reads from the desktop's own contract
fixtures, so no account, profile, Chrome or real person is involved - and
captures four console screens at the default 1104 x 900 window, scaled to
1280 x 800. It then draws the platform gallery, the promo tile and the marquee
from `marketing/brand/` with Playwright's Chromium. The app window opens on your screen
for about a minute while it captures; leave it alone until the command
finishes. To recompose after a brand change without launching the app again,
pass the script `--skip-capture`:

```bash
./venv/bin/python tools/scripts/brand/build-store-assets.py --skip-capture
```

Open each image at full size before you upload it, then upload them on the
dashboard's **Store listing** tab and use **Save draft**; the listing goes to
Google only when someone submits it for review. `tests/test_store_assets.py`
checks that every file the table names exists at its exact size.

## Update an installed Chrome extension

A Blowhorn release does not reinstall the Chrome extension in each Chrome profile.

- Unpacked (Load unpacked on `extension/`): after you upgrade Blowhorn, open `chrome://extensions` and reload the Blowhorn extension. Chrome then runs the files in the checkout.
- Chrome Web Store: the installed copy updates after Google accepts a submitted package. `make desktop-release` packages `dist/blowhorn-extension.zip` and submits it to the existing store item when the content of `extension/` changed since the previous `desktop-v*` tag, or when the content of the native-messaging contract changed (`engine/blowhorn/browser/extension_host.py`, `engine/blowhorn/browser/drivers/extension.py`, `engine/blowhorn/browser/extension_install.py`); a comment-only or blank-line edit is not a content change. The desktop app does not implement that contract; it runs that Python. An unrelated desktop change does not submit a new item. The version is the desktop version with any prerelease suffix dropped. A dry run packages the zip and does not upload it. Credentials stay in the environment on the computer that cuts the release: `CHROME_EXTENSION_ID` (always `fcflpiagmpcfifgknledeknedfopnapf`; any other value is refused before upload), `CHROME_PUBLISHER_ID`, and a service-account credential, `CHROME_ACCESS_TOKEN` or `CHROME_SERVICE_ACCOUNT_KEY_FILE` (Publish the Chrome extension with a service account). The legacy `CHROME_CLIENT_ID`, `CHROME_CLIENT_SECRET`, and `CHROME_REFRESH_TOKEN` still work when no service-account credential is set. If those are missing, or the upload fails, the DMG stays published. Resume with `VERSION=<version> make extension-publish` (same version you just cut). That retries the upload without rebuilding the DMG. Automation submits the package; Google review still has to pass before Chrome updates the installed copy.

The desktop release sets `extension/manifest.json`'s version to that desktop version in the same cases, so the two copies can be told apart. A prerelease suffix is not part of the Chrome extension version. Until you reload, or the store update lands, a run stops before it acts. A hello that omits `trusted_input` stops as `extension_outdated` and names the installed and required versions ([The extension default](/docs/reference/chrome/#the-extension-default)). A hello that does not report this Blowhorn's version or the verbs it sends stops with:

```text
your Chrome extension is <reported>, this Blowhorn needs <version>: reload it in chrome://extensions or update it
```

`<reported>` is `unreported` when the installed extension does not say its version and verbs.
