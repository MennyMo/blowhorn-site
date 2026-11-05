---
# Authoring template - copy this file into a category folder
# (for example getting-started/my-video.md), fill in every field, and
# set draft to false. This file itself is a draft and never publishes.
# Full guide: /resources/contributing/ (tagging rules, feed implications).
#
# Required front matter:
#   title        - the video's name, shown on cards and the video page.
#   description  - one or two sentences; used on cards, search and feeds.
#   date         - publication date (YYYY-MM-DD). Our model requires one
#                  (the layer5io/docs model this is based on has none;
#                  our feeds and recency sorting need it).
#   layout       - always "video".
#   videoType    - "local" for a file the site hosts itself. "youtube"
#                  is reserved: the first embedded video ships with a
#                  privacy-page update, per the site's third-party rule.
#   duration     - "m:ss", shown on the card.
#   categories   - the display name of the category folder the file
#                  lives in. The folder is the category; keep them equal.
#   column       - exactly one of "desk-of-the-general", "boot-camp",
#                  "from-the-field" (blowhorn #1555); feeds carry it as
#                  a "column:<value>" category element.
#   tags         - lowercase slugs; they become /tags/<tag>/ pages and
#                  the tag filter chips. Reuse existing tags first.
#   video        - mp4 and webm paths under assets/video/, and a poster
#                  image (16:9) - the card and the player facade.
# Optional:
#   featured     - true puts the video at the top of the videos landing.
#                  One featured video at a time.
draft: true
title: Template video
description: "Template - replace with the video's summary."
date: 2026-01-01
layout: video
videoType: local
duration: "0:00"
categories: ["Getting started"]
tags: ["overview"]
column: "boot-camp"
video:
  mp4: "assets/video/battalion-thunder.mp4"
  webm: "assets/video/battalion-thunder.webm"
  poster: "assets/video/battalion-thunder-poster-megaphone.webp"
---

Replace this body with anything the video page should add under the player: notes, links, a transcript.
