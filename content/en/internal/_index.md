---
title: Internal
layout: internal
description: Blowhorn's internal strategy, finance, engineering, design, specs, plans and research, for named team members only.
# Rendered only by `hugo --environment internal`.
# Keep internal pages out of the site-wide lists (menus, the search index,
# llms.txt, the sitemap and related-page lists), even in the internal build.
# Pages still render (segments decide whether they render at all).
# Descendants are `list: local`: out of every site-wide collection, but in
# their parents' .Pages, so the docs sidebar, breadcrumb and pager can walk
# the section. `type: docs` renders them in the docs shell
# (layouts/docs/baseof.html) with layouts/docs/internal.html. This section
# page itself stays `list: never`, so it is not one of the home page's
# sections.
cascade:
  - type: docs
    build:
      list: local
      render: always
    sitemap:
      disable: true
build:
  list: never
  render: always
sitemap:
  disable: true
# Render the generated table of contents (layouts/_partials/internal-contents.html).
contents: true
---

Every internal page is listed below, grouped by section. The list is
generated from the content tree on each build, so new pages appear here on
the next deploy.

<!-- Source: nothing under this section is committed to this repository.
`make site-internal` mounts it from a private clone as a Hugo module (see
docs/deploy.md). The public build never renders it. -->
