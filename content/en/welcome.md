---
title: Welcome
heading: Welcome to Blowhorn
description: You installed the Blowhorn browser extension. Three steps finish the setup on your computer.
lead: The Blowhorn extension does nothing on its own. It acts only when the Blowhorn app on your computer asks, so finish these three steps and the extension's toolbar icon turns from "not connected" to connected.
url: /welcome/
layout: onboarding
outputs: [html]
sitemap:
  disable: true
---

## 1. Download the Blowhorn app {#download-the-app}

[Download Blowhorn](/download/), open the disk image and drag Blowhorn to Applications.

## 2. Sign in to your account {#sign-in}

Open Blowhorn and choose **Sign in**. Your browser opens [your account]({{< cloud-url >}}), where you can create one or log in, and then returns you to the app. From a terminal, `blowhorn auth login` does the same.

## 3. Connect your browser profiles {#connect-chrome}

On first muster the app lists the browser profiles it found and asks before it connects any of them. It writes one small file your browser reads for each profile you choose. It does not open your browser or change its settings. You can run `blowhorn setup` at any time to check or repeat this step.

When the extension's icon shows connected, you are ready. If your account does not have Blowhorn yet, the app sends you straight to [your account]({{< cloud-url >}}) to start the beta.
