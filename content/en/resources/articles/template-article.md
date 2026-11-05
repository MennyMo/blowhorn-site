---
# Copy this file, rename it, and fill it in. Files starting with
# "template" stay drafts and never publish. Delete these comments.
# Full guide: /resources/contributing/ (tagging rules, feed implications).
draft: true
layout: article
# Required: the headline.
title: "Template article: replace this headline"
# Required: one or two sentences. This is the card text, the search
# text and the RSS item description - write it for a reader deciding
# whether to click.
summary: "A one or two sentence summary of what the reader learns."
# Required: publication date, YYYY-MM-DD. Feeds and sorting use it.
date: 2026-01-01
# Required: the byline.
author: "Blowhorn team"
# Required: at least one tag. Series membership is a tag:
# "in-product-intelligence" is the Product intelligence series (its
# feed is a published contract with the desktop app - never rename
# the slug), "tips" marks a short tip. Add ONE topic tag from the
# existing set before inventing a new one; a new tag also needs a
# feed page under content/en/resources/tags/.
tags: ["in-product-intelligence"]
# Required: exactly one column - the taxonomy every tip and dated
# resource carries (blowhorn #1555). One of:
# "desk-of-the-general" (From the Desk of the General),
# "boot-camp" (From Boot Camp), "from-the-field" (From the Field).
# Feeds carry it as a "column:<value>" category element.
column: "boot-camp"
# Tips only (tag "tips"): required. The tip's place in the desktop
# app's bundled curriculum order - the next free integer.
# tipOrder: 7
# Tips only: required, enforced by check_tips.py - a tip never
# publishes without a video (#1554). Self-hosted files under
# static/assets/video/tips/, with a 16:9 poster; duration "m:ss".
# video:
#   mp4: "assets/video/tips/<slug>.mp4"
#   webm: "assets/video/tips/<slug>.webm"
#   poster: "assets/video/tips/<slug>-poster.webp"
#   duration: "0:20"
---

Write the article here, in Markdown. Short paragraphs, headings at
## level, and advice a reader can act on today. The summary above is
the teaser; the first paragraph here should open the argument, not
repeat the summary.
