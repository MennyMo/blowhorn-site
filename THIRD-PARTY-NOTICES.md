# Third-party notices

## llms-txt Hugo module (GetHugoThemes)

`layouts/index.llms`, `layouts/index.llmsfull`, `layouts/index.md`,
`layouts/_default/single.md`, `layouts/_default/list.md` and the `llms`,
`llmsfull` and `md` output formats in `hugo.toml` are copied, as
[layer5io/docs](https://github.com/layer5io/docs) uses them, from
[gethugothemes/hugo-modules/llms-txt](https://github.com/gethugothemes/hugo-modules/tree/master/llms-txt)
at `v0.0.0-20260701054856-10b1d2cdc11a`. The three `.md` templates carry
layer5io/docs' change from `.RawContent` to `.RenderShortcodes`.

```
MIT License

Copyright (c) 2018 - Present, Gethugothemes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## jQuery (OpenJS Foundation)

`assets/js/vendor/jquery.min.js` is jQuery v3.7.1, the same bytes Docsy loads
from its CDN, vendored so the docs ship no third-party request. Unmodified.

```
Copyright OpenJS Foundation and other contributors, https://openjsf.org/
```

(MIT license; the full text ships in the file's banner.)

## lunr.js (Oliver Nightingale)

`assets/js/vendor/lunr.min.js` is lunr v2.3.9, the same bytes Docsy loads
from its CDN, vendored so the docs ship no third-party request. One
comment-only change: the banner no longer names the project's homepage URL,
because shipped scripts may not reference another host. Copyright and license
are unchanged.

```
Copyright (C) 2020 Oliver Nightingale
```

(MIT license; the full text ships in the file's banner.)

## Mermaid (Knut Sveidqvist and contributors)

`assets/js/vendor/mermaid.min.js` is `dist/mermaid.min.js` from the npm package
`mermaid` v12.2.0 (sha256 `a8a6a6f805b074a8261a2825c86f99c8054acb3b35f50bb7e24a4f9f2c3c3b9f`),
vendored so diagrams ship no third-party request. Unmodified. It loads only on
pages with a `mermaid` code fence (`layouts/_markup/render-codeblock-mermaid.html`),
which today means the internal site only. To update, unpack the new npm tarball,
copy that file over and change the version and hash here.

```
Copyright (c) 2014 - 2022 Knut Sveidqvist
```

(MIT license; the full text ships in the package.)

## Docsy offline search (Google LLC, Apache-2.0)

`assets/js/offline-search.js` is forked from Docsy v0.14.3
`assets/js/offline-search.js`. The index, the query, and the result entries
are unchanged; the attribution comment no longer names a blog URL (same
reason as above) and results render in an inline box instead of a Bootstrap
popover, because Bootstrap's JavaScript is not shipped.
