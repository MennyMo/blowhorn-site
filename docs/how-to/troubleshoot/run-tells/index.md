# Run Blowhorn Tells


> Check what sites can see about your browser, in Chrome or from a terminal.



[Blowhorn Tells](https://tells.blowhorn.ai/) is a free check of what sites can
see about the browser you open it in: the bot-detection and fingerprinting
signals a page can read, explained in plain words. No sign-up, and it keeps no
copy of the report.

Open that page in the Google Chrome profile you want to check.

You can also run the same check from a terminal with the `tells` command.

## Install

With npm:

```bash
npm i -g blowhorn-tells
```

Or with Homebrew, which also installs Node:

```bash
brew install blowhorn-ai/tap/tells
```

The npm package is
[`blowhorn-tells`](https://www.npmjs.com/package/blowhorn-tells). The command
it puts on your PATH is `tells`.

## Run

```bash
tells
tells --server-only
```

`tells` opens the check in a headless browser, then prints the JSON report and
a one-line verdict. It does not save the report. `--server-only` checks the
server-side signals and needs no browser.

To run it once without a global install:

```bash
npx github:blowhorn-ai/tells
npx github:blowhorn-ai/tells --server-only
```

The default run needs Playwright and its Chromium, which neither install adds.
Without them, `tells` exits with code 2 and prints the install step. After the
npm install, add them:

```bash
npm i -g playwright
npx playwright install chromium
```

A Homebrew install keeps `tells` in its own prefix, where Node cannot find
Playwright, so use the npm install for browser runs.

## Related

- [Blowhorn Tells](https://tells.blowhorn.ai/) - the check in Google Chrome.
- [Fix a sign-in that stopped working](/docs/how-to/troubleshoot/sign-in-problems/) - when a platform
  keeps challenging you.
- [Get help](/docs/reference/support/) - where to look first.

