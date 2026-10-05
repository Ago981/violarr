---
layout: home

hero:
  name: Violarr
  text: Use the ICVDB database directly with Prowlarr
  tagline: Start Violarr, open the WebUI, and connect Prowlarr in a few steps.
  actions:
    - theme: brand
      text: Start Violarr
      link: /en/getting-started/installation
    - theme: alt
      text: Open the WebUI guide
      link: /en/configuration/webui

features:
  - title: Everything in your browser
    details: Check status, connect Prowlarr, and save settings from the WebUI.
  - title: Results that suit you
    details: Prefer Italian releases, filter results, or create custom rules.
  - title: A database ready to use
    details: Check the installed version and manage automatic updates.
---

## Start here

1. [Start the container](/en/getting-started/installation).
2. Open `http://localhost:8000/` in your browser.
3. [Connect Prowlarr](/en/configuration/prowlarr).

::: danger Network exposure

The application has no authentication. Keep port `8000` on a trusted network or
place an authenticated reverse proxy in front of it.

:::
