# What fingerprint and bot-detection checkers measure

Free fingerprint pages and commercial bot detectors publish different signals, and their popularity counts do not share one measure. This article lists the signal groups, two dated rankings, a coverage matrix that includes Blowhorn Tells, and the Tells gaps on the public backlog.


Free pages and commercial bot products do not publish one shared checklist. They publish different readings of the same browser. The notes below use one set of signal groups so those readings can sit in one matrix. Every figure is the figure on the page that stated it. The pages were fetched on November 24, 2026.

You can run Blowhorn's own reading at [Blowhorn Tells](https://tells.blowhorn.ai/). Tells scores what that page can read in the browser you opened. It does not reproduce a vendor's block decision.

## Signal groups

The groups are the ones used to compare Tells with the other tools. A later cell says whether a tool's fetched pages showed that group.

- **Automation and headless markers.** Scripted-browser flags, such as a webdriver bit, a headless build, or a vendor's bot score.
- **Lies.** Tampered prototypes and getters, where a browser API no longer behaves like the engine that claims to be running.
- **Navigator and client hints.** The browser's own identity fields, including user-agent client hints.
- **Wire.** Request headers, the order of those headers, TLS fingerprints (JA3 and JA4), and HTTP/2 fingerprints.
- **IP reputation.** Datacenter, proxy, VPN, and Tor labels on the address.
- **DNS and WebRTC leaks.** A DNS resolver or a WebRTC address that tells a different story than the request IP.
- **Timezone and locale against IP.** The clock, the language, or the locale compared with the address.
- **Canvas, WebGL, and WebGPU.** Drawing and GPU surfaces.
- **Audio.** The audio stack as a signal.
- **Fonts.** The font list.
- **Screen and window.** Screen size, window size, and combinations that cannot occur on a real display.
- **Media and DRM.** Cameras, microphones, codecs, and DRM or payment surfaces.
- **Permissions.** Notification permission and the wider permissions list.
- **Storage.** localStorage, sessionStorage, IndexedDB, and quotas.
- **Cross-context consistency.** The same fact read from the page, a worker, a service worker, an iframe, and the request headers.
- **Behavior.** Pointer, keys, scroll, and timing.
- **Challenges.** Proof of work, a CAPTCHA, or a similar task the detector asks the browser to finish.
- **Uniqueness against a crowd.** How rare each attribute is in that tool's own dataset, often stated in bits.
- **Stability across visits.** Whether the same browser still looks like the same browser on a later day.

## What Tells records today

The Tells check catalog read on November 24, 2026 is version 1.0.3, with 17 check rows. The README on that read still said catalog 1.0.2. The score is 0-100, computed on the server. The verdict is one of `likely_human`, `suspicious`, or `likely_bot`.

JA3 and JA4 are shown and are not scored. The randomized-fingerprint flag is worth 0 points. Interaction checks warn only. A same-visit stability read is three samples in one visit. Tells does not store a visitor id. The compare page diffs two files the reader pastes.

On that catalog, Tells covers automation flags, navigator and client hints, IP reputation, screen and window geometry, cross-context agreement, and behavior. The other groups are partial or absent. The matrix uses the letters below for that split. The open gaps are listed with the backlog issue that tracks each theme.

## Free test sites

Do not sort these sites into one visit league. Semrush total visits, Similarweb visits, Ahrefs search traffic, and GitHub stars count different things. Semrush overview pages for pixelscan.net, browserscan.net, fingerprint.com, coveryourtracks.eff.org, and sannysoft.com returned HTTP 404 on November 24, 2026.

## One provider: Semrush total visits, October 2026

These Semrush pages were fetched on November 24, 2026 and say "Last updated: November 11, 2026."

| Order | Site | October 2026 total visits | Also on that page |
| --- | --- | ---: | --- |
| 1 | [whoer.net](https://www.semrush.com/website/whoer.net/overview/) | 14.72M | September 15.43M, August 12.31M |
| 2 | [browserleaks.com](https://www.semrush.com/website/browserleaks.com/overview/) | 4.13M | September 3.7M |
| 3 | [ipleak.net](https://www.semrush.com/website/ipleak.net/overview/) | 2.32M | September 1.77M. An IP-leak suite, not a full fingerprint bench, so it is not a matrix column. |
| 4 | [iphey.com](https://www.semrush.com/website/iphey.com/overview/) | 83.58K | September 64.18K, August 94.14K |
| 5 | [amiunique.org](https://www.semrush.com/website/amiunique.org/overview/) | 62.54K | September 58.54K, August 108.76K |

whoer.com is a second domain. Semrush lists 2.91M total visits for it in October 2026. It is not treated as a separate tool.

## Other public counts

Each row names its own measure. None of these is a Semrush total-visit rank.

| Site | Figure | What the figure is | Source |
| --- | --- | --- | --- |
| fingerprint.com | 242,504 visits in October 2026, down 2% from the prior month | Similarweb, reprinted by AdLibrarySpy, read November 24, 2026 | [AdLibrarySpy](https://adlibraryspy.com/answers/store/fingerprint.com) |
| coveryourtracks.eff.org | 233.2K "last month", down 8.7% | websites-traffic.com. The month name is not on the page. Fetched November 24, 2026. | [websites-traffic.com](https://websites-traffic.com/site/coveryourtracks.eff.org) |
| browserscan.net | 89.6K search traffic in November 2026, down 46.7K from the prior month | Ahrefs search traffic via ahrefstop.com. Total visits were not on that page. | [ahrefstop.com](https://ahrefstop.com/websites/browserscan.net) |
| pixelscan.net | No current-month visit count | The Semrush overview returned HTTP 404 on November 24, 2026. A third-party copy of an older Semrush page, last updated February 19, 2026, says 448.12K visits in January 2026. That figure is not used as a current rank. | [sem2.heaventechit.com](https://sem2.heaventechit.com/website/pixelscan.net/overview/) |
| CreepJS | 2,558 GitHub stars. Last push June 11, 2026. | No visit figure was retrieved. GitHub API, November 24, 2026. | [abrahamjuliot/creepjs](https://github.com/abrahamjuliot/creepjs) |
| bot.sannysoft.com | No visit figure and no star count | The live page was fetched on November 24, 2026. | [bot.sannysoft.com](https://bot.sannysoft.com/) |

The matrix uses ten free tools, largest sourced audience first, with the measure named: whoer.net, BrowserLeaks, fingerprint.com (Similarweb), Cover Your Tracks (websites-traffic.com, month unnamed), iphey, BrowserScan (search traffic only), AmIUnique, Pixelscan (current visits unverified), CreepJS (stars), and sannysoft (no popularity figure).

What each one reported on that fetch:

- **whoer.net** showed IP, ISP, DNS, hostname, OS, browser, proxy, anonymizer, blacklist, and an anonymity percent. In that render, Flash, Java, DNT off, and ActiveX were each a -10% deduction. The full formula was not published.
- **BrowserLeaks** is a suite of pages, with no single score on the homepage. The homepage lists IP (headers, a TCP/IP OS fingerprint, WebRTC, DNS, IPv6), JavaScript, canvas, WebGL, fonts, the Geolocation API, features, a TLS client test, and content filters. HTTP/2 was not in that homepage text.
- **fingerprint.com** is the demo. FingerprintJS is MIT, npm `@fingerprintjs/fingerprintjs` 5.3.0 on November 24, 2026, 28,796 GitHub stars, and it returns a `visitorId`. BotD is MIT, npm `@fingerprintjs/botd` 2.0.0, 1,501 stars, and it returns a bot detection, not entropy. Pro bot detection is commercial. Its sample fields are `bot` of good, bad, or not_detected, plus IP and user agent. No public deployment-share figure was retrieved.
- **Cover Your Tracks** describes an overview of the browser's most unique characteristics and says only anonymous data is collected. The page loads tracker-test iframes. A bit-level formula was not on the homepage.
- **iphey** shows one MX Score and the categories Browser, Location, IP, Hardware, and Software, including VPN or proxy, bot, DNS leak, and an IP blacklist.
- **BrowserScan** lists DNS leak, WebRTC leak, IP lookup, HTTP/2, SSL, TLS, client hints, plugins, bot detection, canvas, kernel versus user agent, WebGPU, media devices, timezone, and a port scan. A [blog post on November 15, 2026](https://blog.browserscan.net/docs/browserscan-vs-browsercheck) also names an authenticity score and WebDriver and CDP checks.
- **AmIUnique** compares the browser with contributors. The page says viewing a fingerprint stores it and sets a cookie for four months. Named attributes include browser and OS, screen, architecture, fonts, plugins, microphone, and camera. The result is uniqueness, not a bot verdict.
- **Pixelscan.** The homepage fetch returned almost no text. A first-party signal list was not retrieved. A [secondary guide](https://multime.app/blog/fingerprint-test-sites), checked by its author on October 24, 2026, says the verdicts are consistent, unsure, or inconsistent, and that the site stores fingerprints and IPs. Layer agreement, such as WebRTC against IP, is that secondary claim. It is not a captured Pixelscan run, so the matrix leaves those cells unverified.
- **CreepJS** is MIT. The README's only stated official deploy is the GitHub Pages site. The README lists tests that include canvas, text metrics, WebGL, GPU, fonts, voices, audio, screen, timezone, Math, CSS, and workers. The score on the page is a set of section percents. The README does not define one number.
- **bot.sannysoft.com** is a pass or fail table: WebDriver, the Chrome object, permissions, plugins, languages, WebGL vendor and renderer, broken image dimensions, canvas reads, and screen fields. The page calls the set "Antibot Intoli.com tests + additions." No license file for the site was retrieved.

## Commercial detectors

Two censuses count different denominators. Both put Cloudflare first, near three quarters of the things they count. They do not agree on the order under that.

**Zyte, State of Web Access 2026, antibot page, fetched November 24, 2026.** The page covers 11,100 landing pages and says antibot is on 18.5% of them. Of 2,054 sites with an identifiable antibot vendor: Cloudflare Bot Management 75.9%, Imperva (Incapsula) 9.1%, Akamai Bot Manager 7.7%, PerimeterX (HUMAN) 5%, DataDome 2%, Other 0.3%. Source: [Zyte](https://www.zyte.com/sowa/2026/barriers/antibot/).

**WMTips bot-mitigation category, last calculated November 23, 2026, covering 4,048,507 websites.** The shares below are the share of detected bot-mitigation tools, from the category page text retrieved through a search index on November 24, 2026. A direct fetch of the page returned HTTP 403 that day. Cloudflare's own WMTips product page, dated November 11, 2026, lists 245,083 sites. That site count is not 74.6% of the 4,048,507 websites. Sources: [the category](https://www.wmtips.com/technologies/bot-mitigation/) and [the Cloudflare product page](https://www.wmtips.com/technologies/bot-mitigation/cloudflare-bot-management/).

| WMTips rank | Product | WMTips share of detected tools | Zyte share of identifiable antibot |
| ---: | --- | --- | --- |
| 1 | Cloudflare Bot Management | 74.6% | 75.9% |
| 2 | Akamai Bot Manager | 7.1% | 7.7% |
| 3 | F5 BIG-IP | 6.3% | Not broken out |
| 4 | Imperva, labeled Imperva WAF on WMTips | 3% | 9.1%, labeled Imperva (Incapsula) |
| 5 | DDoS Guard | 2.9% | Not named |
| 6 | FortiWeb | 1.5% | Not named |
| 7 | ClickCease | 1.2% | Not named |
| 8 | Fastly Bot Management | 0.6% | Not named |
| 9 | Qrator | 0.5% | Not named |
| 10 | HUMAN (PerimeterX), labeled Human on WMTips | 0.5% | 5% |

DataDome ties HUMAN on WMTips at 0.5%, where WMTips spells it Datadome, and it ties Radware Bot Manager at that share. On Zyte, DataDome is 2%, fifth among named vendors. The matrix keeps DataDome because Zyte names it, and it leaves out F5, DDoS Guard, FortiWeb, ClickCease, Fastly Bot Management, and Qrator because no public signal list was retrieved for them.

A third cut is not a web-wide share. The [proxies.sx census](https://www.proxies.sx/anti-bot/dataset), reviewed July 2026, page dated August 1, 2026, covers 93 sites: Akamai 45/93 (48%), Cloudflare 32/93 (34%), HUMAN 11/93 (12%), DataDome 8/93 (9%), Kasada 5/93 (5%), reCAPTCHA 3/93, hCaptcha 3/93, Queue-it 2/93, Imperva 1/93, AWS WAF 1/93.

[W3Techs reverse proxies](https://www.w3techs.com/technologies/overview/proxy), page dated November 24, 2026, is not bot management. It says Cloudflare is on 30.3% of websites, 86.7% of identified reverse proxies, with Akamai at 0.6% and Imperva at 0.1%. Those numbers are not ranks in the table above.

The Panoramic URL `https://panoramic.al/technologies/bot-protection` returned HTTP 404 on November 24, 2026. Shares that depended on that page are not used here.

Vendor docs fetched the same day, in short:

- **Cloudflare** documents a bot score from 1 to 99, with 1 automated and 99 human. Enterprise plans see the number. Others see groupings. The doc, last updated August 26, 2026, names heuristics, machine learning, anomaly detection, JavaScript detections, and verified bots. Separate docs cover JA3 and JA4, and a signal for the HTTP/2 plus HTTP/3 share per JA4. A blog post on September 23, 2025 names HTTP/2 fingerprints and behavioral path analysis. Turnstile is a separate challenge product and is not enumerated on the bot-score page. IP reputation, canvas, and DNS were not stated on the pages fetched. Sources: [bot score](https://developers.cloudflare.com/bots/concepts/bot-score/), [JA3/JA4](https://developers.cloudflare.com/bots/additional-configurations/ja3-ja4-fingerprint/), [Signals Intelligence](https://developers.cloudflare.com/bots/additional-configurations/ja3-ja4-fingerprint/signals-intelligence/), [per-customer defenses](https://blog.cloudflare.com/per-customer-bot-defenses/).
- **Akamai.** Akamai's own techdocs HTML was not retrieved. Secondary pages quote a behavior script and quote a TLS ClientHello patent and an HTTP/2 fingerprint talk. Canvas, audio, fonts, and sensor field lists stay unverified. The sourced groups are wire (TLS, HTTP/2, header order) and behavior. Sources: [antibrow.com, November 1, 2026](https://antibrow.com/blog/akamai-bot-manager-explained) and [coronium.io, October 30, 2026](https://www.coronium.io/blog/akamai-bot-manager).
- **DataDome** docs say signature models use a TLS fingerprint, a browser fingerprint, and HTTP headers. Behavioral models and reputation models cover IPs flagged as datacenter or residential proxy. Responses are Allow, Captcha, Block, and Device Check. Device Check collects screen size and resolution, codecs, plugins, browser type, CPU and GPU counts, and JavaScript consistency challenges. The product page adds a proof-of-work step and a slider. One model name is "Headless Browser Forged Fingerprint," aimed at Puppeteer, Selenium, and Playwright. HTTP/2 was not in the fetched docs. Sources: [AI detection](https://docs.datadome.co/docs/ai-detection), [Device Check](https://docs.datadome.co/docs/device-check), [product page](https://datadome.co/products/datadome-device-check/).
- **HUMAN (PerimeterX)** documents a sensor for DOM, BOM, and WASM signals, visual and audio rendering, plugins, and extensions, then a machine learning detector and a risk score from 0 to 100. Behavior docs name mouse, touch, cadence, and timing. Calibration mentions user agents and IP addresses. JA3 was not in the pages fetched. Sources: [sensor FAQ](https://docs.humansecurity.com/applications/bd-faq-sensor), [detection overview](https://docs.humansecurity.com/applications/bd-detection-overview), [product overview](https://docs.humansecurity.com/applications/overview).
- **Imperva.** The [product page](https://www.imperva.com/products/bot-management/) fetched on November 24, 2026 is a feature list. It does not enumerate signals.
- **Kasada.** The [bot-management page](https://www.kasada.io/bot-management/) names account-takeover and scraping use cases and does not list signals. Kasada is 5 of 93 sites in the proxies.sx set. It is not in the WMTips snippet above.

## Coverage matrix

Rows are the signal groups. Columns after Tells are the ten free tools, then the five vendors Zyte names. Cells:

- **Y** - the fetched source shows that group.
- **P** - part of the group, or collected and not fully scored.
- **N** - the fetched pages or source files did not show that group.
- **U** - unverified. This pass did not retrieve a first-party list for that cell. U stays U.

Short headers: Leaks is BrowserLeaks. FP is fingerprint.com plus FingerprintJS and BotD. CYT is Cover Your Tracks. Scan is BrowserScan. AmIU is AmIUnique. Pixel is Pixelscan. Creep is CreepJS. sanny is bot.sannysoft.com. CF is Cloudflare Bot Management. Akam is Akamai Bot Manager. DD is DataDome. Imp is Imperva.

| Group | Tells | whoer | Leaks | FP | CYT | iphey | Scan | AmIU | Pixel | Creep | sanny | CF | Akam | DD | HUMAN | Imp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Automation / headless | Y | U | N | Y | N | Y | Y | N | U | Y | Y | Y | U | Y | P | U |
| Lies (prototypes, getters) | P | N | N | P | N | U | U | N | U | Y | P | U | U | P | U | U |
| Navigator and client hints | Y | P | Y | Y | U | P | Y | Y | U | Y | Y | U | U | Y | P | U |
| Wire: headers, order, TLS, HTTP/2 | P | P | P | N | N | U | Y | U | U | N | N | Y | Y | P | U | U |
| IP reputation | Y | Y | P | P | N | Y | Y | N | U | N | N | U | U | Y | P | U |
| DNS and WebRTC | P | Y | Y | N | N | Y | Y | N | U | P | N | U | U | U | U | U |
| Timezone / locale vs IP | P | P | P | P | N | Y | Y | U | U | P | N | U | U | U | U | U |
| Canvas, WebGL, WebGPU | P | U | P | P | U | P | Y | U | U | Y | P | U | U | P | P | U |
| Audio | P | N | N | Y | N | U | U | N | U | Y | N | U | U | N | Y | U |
| Fonts | P | N | Y | Y | U | U | U | Y | U | Y | N | U | U | N | U | U |
| Screen / window | Y | U | Y | Y | U | P | U | Y | U | Y | Y | U | U | Y | P | U |
| Media / DRM | P | N | N | P | N | U | Y | P | U | P | N | U | U | P | U | U |
| Permissions | P | N | P | Y | N | U | U | N | U | U | Y | U | U | N | U | U |
| Storage | P | N | N | Y | N | U | N | N | U | N | N | U | U | N | U | U |
| Cross-context | Y | N | N | N | N | U | P | N | U | Y | P | U | U | U | U | U |
| Behavior | Y | N | N | N | N | U | U | N | U | N | N | P | Y | Y | Y | U |
| Challenges (proof of work, CAPTCHA) | P | N | N | N | N | N | N | N | U | N | N | U | U | Y | U | U |
| Uniqueness vs crowd | N | N | N | P | Y | P | N | Y | U | N | N | U | U | N | P | U |
| Stability across visits | P | N | N | Y | N | U | N | P | U | N | N | U | U | U | P | U |

Three cells need a narrower reading than the letter alone. The FP uniqueness cell is a persistent `visitorId`, not entropy bits. The AmIUnique stability cell is the four-month cookie and a history page, not a published revisit score. CreepJS has a WebRTC module in the repo. DNS was not in the CreepJS README test list.

Akamai's Y cells for wire and behavior come from the secondary pages dated November 1, 2026 and October 30, 2026. Akamai's own manual was not fetched, so the other Akamai cells stay U. Pixelscan stays U for the same reason as the homepage fetch.

## Where Tells is behind

The gaps below are the places Tells is N or partial and another tool's fetched evidence shows the missing piece. Each theme is an open issue on the Tells backlog. Nothing in this list is a ship date.

**Automation tells.** [Issue 96](https://github.com/blowhorn-ai/tells/issues/96). sannysoft still has rows Tells does not score as their own checks: a missing `chrome` object, the PluginArray type, broken image dimensions, and canvas inside a sandboxed iframe. BotD detectors with no Tells reason on this read include eval length, error trace, `Function.prototype.bind`, `productSub`, `window.external`, a `process` global, and mime-type consistency. BrowserScan publishes a kernel-versus-user-agent check. Tells already compares the user agent with client hints. It does not have an engine-versus-user-agent row.

**Challenges and forged-fingerprint models.** [Issue 97](https://github.com/blowhorn-ai/tells/issues/97). Tells can ask the reader to type a phrase. It has no proof of work and no CAPTCHA result. DataDome's Device Check adds codec and plugin consistency, CPU and GPU counts, JavaScript challenges, a proof-of-work step, and a slider CAPTCHA. DataDome also names a "Headless Browser Forged Fingerprint" model for Playwright, Puppeteer, and Selenium after the obvious flags are patched. HUMAN's docs describe a risk score that compares mouse and touch cadence, plus audio and visual rendering, with a library of bad actors. Tells scores behavior and audio stability separately and has no such library.

**Crowd uniqueness, a visitor id, opt-in.** [Issue 98](https://github.com/blowhorn-ai/tells/issues/98). AmIUnique and Cover Your Tracks report uniqueness against a crowd. FingerprintJS returns a `visitorId` that is meant to last across days. Tells has no crowd dataset and no stored visitor id. The backlog item is an opt-in dataset, with the reader choosing to contribute.

**A deeper lie scan, including Math.** [Issue 99](https://github.com/blowhorn-ai/tells/issues/99). Tells checks native getters, `Function.prototype.toString`, a webdriver patch, and a prototype mismatch across the page, the iframe, the worker, and the service worker. CreepJS goes further: Math, audio, canvas, CSS computed style, DomRect, emoji, error stacks, and contentWindow. FingerprintJS and CreepJS both treat Math as its own fingerprint. That wider scan is the gap.

**Score more surfaces.** [Issue 100](https://github.com/blowhorn-ai/tells/issues/100). Tells collects several surfaces and does not score them as identity. The gap is WebGPU as a scored surface (BrowserScan), audio as an identity hash rather than a same-session stability class (FingerprintJS, CreepJS, and the HUMAN sensor), the font list (BrowserLeaks, FingerprintJS, AmIUnique, CreepJS), speech voices (CreepJS; Tells collects them), media-device counts (BrowserScan, and microphone and camera on the AmIUnique homepage), storage beyond an unscored `localStorage` probe (FingerprintJS also reads sessionStorage and IndexedDB), and DRM or Apple Pay presence (FingerprintJS). Tells already files DRM under surfaces it reports and does not score.

**Tracker blocking.** [Issue 101](https://github.com/blowhorn-ai/tells/issues/101). Cover Your Tracks loads tracker-test iframes. whoer deducts points when DNT is off. Tells does not report whether third-party trackers were blocked.

**Network leaks.** [Issue 102](https://github.com/blowhorn-ai/tells/issues/102). whoer, BrowserLeaks, BrowserScan, and iphey test DNS leaks. Tells compares the WebRTC public IP with the request IP and has no DNS leak test. BrowserLeaks also shows an IPv6 reading and a TCP/IP OS fingerprint as their own results. BrowserLeaks links a Geolocation API test. Tells compares the browser timezone with the IP timezone. It does not read the Geolocation API position.

**Locale, IP country, and blacklists.** [Issue 103](https://github.com/blowhorn-ai/tells/issues/103). iphey has a Location category, and BrowserScan has a timezone tool. Tells flags a timezone mismatch and an Accept-Language mismatch against the browser. It does not check that the language matches the IP country. whoer has a blacklist line, and iphey has an IP blacklist test, separate from the VPN, proxy, Tor, and datacenter flags Tells already scores.

**Wire fingerprints.** [Issue 104](https://github.com/blowhorn-ai/tells/issues/104). Tells checks the header set, a missing Accept or Accept-Language, and the user agent against `navigator`. It displays JA3 and JA4 and does not score them. It does not check header order. It does not fingerprint HTTP/2. BrowserScan publishes an HTTP/2, SSL, and TLS test. Cloudflare publishes JA3 and JA4 and an HTTP/2 plus HTTP/3 share. The Akamai header-order claim is the secondary write-up, because Akamai's own page was not fetched.

Imperva, Kasada, F5, Fastly Bot Management, FortiWeb, ClickCease, Qrator, and DDoS Guard had no public signal list on this pass, so no extra gap line was taken from them.

## A published stealth benchmark

One public stealth benchmark of hosted browser providers was retrieved on November 24, 2026. The numbers below are what that publisher reports. They are not a Blowhorn measurement. No Tells report was captured for any of these products on that pass, and this article does not add a Blowhorn score beside them.

**Browser Use, "We Stealth Benchmarked Every Major Cloud Browser Provider," published March 21, 2026.** [The post](https://browser-use.com/posts/stealth-benchmark) says the set is 71 sites drawn from 300,000 production security-check events. The vendor mix is Cloudflare 23, PerimeterX 18, DataDome 13, Akamai 8, reCAPTCHA 6, and other (including Kasada and Shape) 3. That mix is a block list, not a market share.

The task is 3 steps, with no login. The judge is gemini-2.5-flash, blocked or not. A page-load failure counts as a block. The same agent and model, bu-2-0, runs on every provider. Controls on a GitHub Actions datacenter IP: headless Chromium 2%, headful Chromium 50%. Provider pass rates in the post: Browser Use Cloud 81%, Anchor 77%, Kernel 67% (the post spells it kernel), Steel 47%, Browserbase 42%, Hyperbrowser 40%. Browser Use Cloud by vendor, only the three rates the post publishes: Cloudflare 93%, Akamai 85%, PerimeterX 81%.

The same post reports Halluminate BrowserBench, 296 tasks, which it describes as less focused on hard sites: Browser Use Cloud 84.8%, Hyperbrowser 76.4%, Anchor 76.0%, Steel 73.3%, Browserbase 70.3%. The post says proxy quality and site configuration move the numbers. The post links [browser-use/benchmark](https://github.com/browser-use/benchmark). That repository was not re-read on November 24, 2026.

No other public stealth benchmark of this product list was retrieved on that pass. Anti-detect roundups were not re-fetched as benchmark results.

## How to read a checker

Open [Blowhorn Tells](https://tells.blowhorn.ai/) in the browser you want to understand. Read the verdict beside the separate checks. A single anonymity percent on another site is that site's formula.

When you quote a ranking, keep the provider, the month, and the link. Semrush total visits, Similarweb visits, and Ahrefs search traffic answer different questions. When you quote a pass rate, keep the date, the site set, and who ran it. The March 21, 2026 Browser Use figures are Browser Use's own runs.

A commercial detector's score is that vendor's score. The matrix records which signal groups their public docs name. It is not a claim that any one checker blocks a given browser.

For one platform block where the vendor never published the detector, see [Amazon blocked Meta's Muse](/resources/articles/how-amazon-detects-muse/).

## Sources

Fetched November 24, 2026 unless the line names another date.

- Semrush overviews, last updated November 11, 2026: [whoer.net](https://www.semrush.com/website/whoer.net/overview/), [browserleaks.com](https://www.semrush.com/website/browserleaks.com/overview/), [ipleak.net](https://www.semrush.com/website/ipleak.net/overview/), [iphey.com](https://www.semrush.com/website/iphey.com/overview/), [amiunique.org](https://www.semrush.com/website/amiunique.org/overview/)
- [AdLibrarySpy on fingerprint.com](https://adlibraryspy.com/answers/store/fingerprint.com), read November 24, 2026
- [websites-traffic.com on Cover Your Tracks](https://websites-traffic.com/site/coveryourtracks.eff.org)
- [ahrefstop.com on browserscan.net](https://ahrefstop.com/websites/browserscan.net)
- [Zyte, State of Web Access 2026, antibot](https://www.zyte.com/sowa/2026/barriers/antibot/)
- [WMTips bot mitigation](https://www.wmtips.com/technologies/bot-mitigation/), last calculated November 23, 2026
- [proxies.sx anti-bot dataset](https://www.proxies.sx/anti-bot/dataset), page dated August 1, 2026
- [Browser Use stealth benchmark](https://browser-use.com/posts/stealth-benchmark), March 21, 2026
- [Cloudflare bot score](https://developers.cloudflare.com/bots/concepts/bot-score/), doc updated August 26, 2026
- [DataDome device check](https://docs.datadome.co/docs/device-check) and [AI detection](https://docs.datadome.co/docs/ai-detection)
- [HUMAN Bot Defender overview](https://docs.humansecurity.com/applications/overview)
- Live checkers: [whoer.net](https://whoer.net/), [BrowserLeaks](https://browserleaks.com/), [Cover Your Tracks](https://coveryourtracks.eff.org/), [iphey](https://iphey.com/), [BrowserScan](https://www.browserscan.net/), [AmIUnique](https://amiunique.org/), [CreepJS](https://abrahamjuliot.github.io/creepjs), [bot.sannysoft.com](https://bot.sannysoft.com/)
- [Blowhorn Tells](https://tells.blowhorn.ai/), catalog 1.0.3 read November 24, 2026

