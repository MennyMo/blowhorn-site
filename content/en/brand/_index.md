---
title: Brand
description: The Blowhorn logo, wordmark, colors, type, Major Blowhorn and Old Thunderlung, with the rules for using them and two kits to download.
lead: The logo, the colors, the type and one opinionated rooster. Everything you need to show Blowhorn off without upsetting him.
layout: brand
lastmod: 2026-10-28
sitemap:
  changefreq: monthly
  priority: 0.3
# Both zips are built from the brand masters by the product repository's
# tools/scripts/brand/build-brand-kit.py and copied to static/brand/ unchanged.
# `size` is the file's size in MB (1024 x 1024 bytes): one decimal under 10 MB,
# whole MB above. make check-brand-kits fails when it drifts from the file.
kits:
  full:
    url: /brand/blowhorn-brand-kit.zip
    size: 28 MB
  logos:
    url: /brand/blowhorn-logo-kit.zip
    size: 2.0 MB
# Logo tiles. `stage` is the ground the file is drawn for: light, dark, teal or charcoal.
lockups:
  - name: Horizontal lockup
    note: The default
    file: blowhorn-lockup-horizontal.svg
    stage: light
    w: 584
    h: 145
  - name: Horizontal lockup, on dark
    note: For near black and charcoal
    file: blowhorn-lockup-horizontal-on-dark.svg
    stage: dark
    w: 584
    h: 145
  - name: Stacked lockup
    note: For square spaces
    file: blowhorn-lockup-stacked.svg
    stage: light
    w: 430
    h: 318
  - name: Stacked lockup, on dark
    note: For square spaces on dark
    file: blowhorn-lockup-stacked-on-dark.svg
    stage: dark
    w: 430
    h: 318
marks:
  - name: Icon
    note: When the name is already nearby
    file: blowhorn-icon.svg
    stage: light
  - name: Icon, on dark
    note: The mouthpiece turns teal
    file: blowhorn-icon-on-dark.svg
    stage: dark
  - name: One color, charcoal
    note: On teal, photos and busy grounds
    file: blowhorn-icon-mono-charcoal.svg
    stage: teal
  - name: One color, white
    note: On dark photos and busy grounds
    file: blowhorn-icon-mono-white.svg
    stage: charcoal
wordmarks:
  - name: Wordmark
    note: Outlined art, never a font
    file: blowhorn-wordmark.svg
    stage: light
  - name: Wordmark, on dark
    note: White, for dark grounds
    file: blowhorn-wordmark-white.svg
    stage: dark
  - name: Company lockup
    note: The formal lockup, with the company mark
    file: layer5-blowhorn-lockup.svg
    stage: light
  - name: Company lockup, on dark
    note: The same, after hours
    file: layer5-blowhorn-lockup-on-dark.svg
    stage: dark
  - name: One-color lockup, charcoal
    note: For teal and busy light grounds
    file: blowhorn-lockup-horizontal-mono-charcoal.svg
    stage: teal
  - name: One-color lockup, white
    note: For busy dark grounds
    file: blowhorn-lockup-horizontal-mono-white.svg
    stage: charcoal
apps:
  - name: App icon
    file: blowhorn-app-icon.svg
  - name: App icon, dark
    file: blowhorn-app-icon-dark.svg
  - name: App icon, light
    file: blowhorn-app-icon-light.svg
mascot:
  - name: Hat, facing left
    file: locked-6/major-6-hat-left
    alt: Major Blowhorn in his campaign hat, pointing and shouting into his bullhorn, facing left
    w: 657
    h: 560
  - name: Hat, facing right
    file: locked-6/major-6-hat-right
    alt: Major Blowhorn in his campaign hat, pointing and shouting into his bullhorn, facing right
    w: 657
    h: 560
  - name: Medals
    file: locked-6/major-6-medals-right
    alt: Major Blowhorn with his medals, shouting into his bullhorn
    w: 660
    h: 560
  - name: Plain
    file: locked-6/major-6-plain-left
    alt: Major Blowhorn without his hat, shouting into his bullhorn
    w: 659
    h: 560
# Old Thunderlung tiles: PNG and WebP copies of the product repository's
# marketing/brand/major-blowhorn/thunderlung/brand-style/ cutouts, unchanged.
thunderlung:
  - name: With cord, side
    file: thunderlung/thunderlung-tassel-side
    alt: Old Thunderlung, a dented brass army bugle with a red cord and two tassels, seen from the side
    w: 1173
    h: 660
  - name: With cord, three-quarter
    file: thunderlung/thunderlung-tassel-3q
    alt: Old Thunderlung, a dented brass army bugle with a red cord and two tassels, at a three-quarter angle
    w: 1110
    h: 641
  - name: Plain, side
    file: thunderlung/thunderlung-notassel-side
    alt: Old Thunderlung, a dented brass army bugle without its cord, seen from the side
    w: 1172
    h: 611
  - name: Plain, tilted
    file: thunderlung/thunderlung-notassel-tilt
    alt: Old Thunderlung, a dented brass army bugle without its cord, tilted bell up
    w: 963
    h: 725
fonts:
  - family: Bricolage Grotesque
    role: Display
    class: type-display
    weights: ExtraBold 800, Bold 700
    sample: One message out, many ears in
    url: https://fonts.google.com/specimen/Bricolage+Grotesque
  - family: Instrument Sans
    role: Text and interface
    class: type-sans
    weights: Regular 400, Medium 500, SemiBold 600
    sample: Write it once. Blowhorn takes it from there.
    url: https://fonts.google.com/specimen/Instrument+Sans
  - family: JetBrains Mono
    role: Code and labels
    class: type-mono
    weights: Regular 400, Medium 500
    sample: POSTED TO 12 PROFILES
    url: https://fonts.google.com/specimen/JetBrains+Mono
---
