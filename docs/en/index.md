---
layout: home

hero:
  name: Violarr
  text: The Prowlarr integration for Il Corsaro Viola
  tagline:
    Run PostgreSQL, the Torznab API, database updates, and the WebUI in one
    container.
  actions:
    - theme: brand
      text: Install with Docker
      link: /en/getting-started/installation
    - theme: alt
      text: Configure Prowlarr
      link: /en/configuration/prowlarr

features:
  - title: Torznab compatible
    details:
      Search movies, TV, and anime from Prowlarr through the established /api
      endpoint.
  - title: Useful result processing
    details:
      Prefer or require explicit Italian markers, or build bounded custom score
      and exclusion rules.
  - title: Safe snapshot updates
    details:
      Validate a candidate database before a brief maintenance-only switch, with
      rollback on failure.
---

## Start here

Violarr is a thin adapter between an ICVDB PostgreSQL snapshot and
Torznab-compatible clients. It does not download torrents or manage a media
library.

1. [Start the container](/en/getting-started/installation).
2. Open the WebUI at `http://localhost:8000`.
3. [Connect Prowlarr](/en/configuration/prowlarr).

::: warning v1.1.0 release status

The WebUI and configuration features documented here are pending the v1.1.0
release. The implementation is present in the project, but publication of the
release image and Docker runtime verification are not yet complete.

:::

::: danger Network exposure

The application has no authentication. Keep port `8000` on a trusted network or
place an authenticated reverse proxy in front of it.

:::
