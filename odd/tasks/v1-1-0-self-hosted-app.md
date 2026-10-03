# v1.1.0 self-hosted application

Deliver a backward-compatible v1.1.0 that adds persistent WebUI configuration, useful ICVDB result processing, one-click Prowlarr integration, and a public documentation site while preserving the v1.0 single-container runtime and Torznab contract.

## Objective

An existing or fresh user can run the GHCR image, open `http://localhost:8000`, configure result behavior and Prowlarr, and continue using `/api` without manually editing JSON or losing `/data` state.

## Problem and why

The v1.0 service is operationally safe but backend-only. Users cannot inspect status, persist interactive settings, prioritize Italian releases, or install the indexer in Prowlarr from the product itself. The release must add those capabilities without weakening the tested candidate-database snapshot switch.

## Authorized scope

- Add versioned, atomically written settings under `/data/state` with documented environment precedence and masked secrets.
- Add deterministic hard-filter and score/ranking processing before Torznab XML generation.
- Add same-origin JSON endpoints for status, settings, result processing, and Prowlarr operations.
- Add a Vue 3 + Vite WebUI served by FastAPI from the existing container.
- Add Prowlarr schema-derived Generic Torznab testing and creation via `X-Api-Key`.
- Keep PostgreSQL 16, `/data`, the snapshot updater, port 8000, and `/api` compatibility.
- Add behavior-focused backend/frontend tests and regression checks.
- Add a Markdown-first VitePress site, GitHub Pages workflow, and concise user-facing project docs.

## Constraints

- No second runtime container, settings database, Redis, Docker socket, plugin system, or complex authentication.
- Never expose the Prowlarr API key through logs or normal read responses.
- Do not add arbitrary scripting or uncontrolled regular expressions to custom rules.
- Preserve v1.0 query parameters, XML shape, categories, pagination, and safe snapshot rollback behavior.
- Generated assets are excluded from authored-line delivery budgeting.

## Delivery strategy

- Strategy: `ask-on-risk`, resolved by maintainer to `feature-branch-chain`.
- Tracker branch: `feature/v1.1.0`.
- Review budget: about 400 authored additions plus deletions per slice; use cohesive behavior rather than code-golf.
- Forecast: approximately 2,500–4,000 authored lines, excluding lockfiles and built assets.
- Planned slices:
  1. settings and result-processing foundation;
  2. internal API and Prowlarr integration;
  3. Vue WebUI and product design system;
  4. single-container frontend/runtime integration;
  5. VitePress documentation and release guidance.
- Pushes and pull requests remain maintainer decisions.

## Tasks

- [x] **V110-01 — Persist settings and process results**
  - Route: delegated; preparation and implementation span multiple non-trivial modules and tests.
  - Add versioned defaults, validation, atomic persistence, environment initialization/override semantics, and secret masking.
  - Add presets `unfiltered`, `italian_preferred`, `italian_only`, and `custom` with structured rules.
  - Support reliable title/language hints, seeders, provider, and size fields; reject unsafe rule shapes.
  - Preserve unfiltered v1.0 ordering and stable tie behavior.
  - Acceptance: defaults auto-create under `/data/state`; restart reloads settings; Italian preferred ranks without removing fallback; Italian only filters; custom score/exclude/minimum-seeders/disabled rules work.
  - Checks: focused pytest suite for settings and result processing; existing Torznab characterization tests.
  - Evidence: 41 focused/full tests passed; parent spot-check repeated 41 passes with 5 pre-existing deprecation warnings.
  - Commits: `a76643d` (result processor), `3034f24` (persistent settings), and `7c51831` (Torznab integration and regression coverage).
  - Delivery note: the cohesive settings unit is 452 authored lines; it exceeds the 400-line heuristic by 52 lines because validation, persistence, masking, and their behavior tests must remain reviewable together.
  - RDD outcome: `disabled/unmanaged` (global mode is off).

- [x] **V110-02 — Expose internal API and Prowlarr integration**
  - Route: delegated; multiple backend modules, HTTP contracts, and mocks are required.
  - Add non-colliding `/webapi` endpoints for health/status, settings, result processing, and Prowlarr.
  - Expose updater state without changing candidate restore/switch semantics.
  - Derive Generic Torznab resources from Prowlarr `/api/v1/indexer/schema`, test and create them with `X-Api-Key`, and detect existing installation by implementation plus normalized URL/path.
  - Acceptance: secrets remain masked; connection failures are actionable; already-installed detection is idempotent; `/api` remains unchanged.
  - Checks: mocked Prowlarr success/failure/schema/create tests; FastAPI endpoint and Torznab regression tests.
  - Evidence: 82 tests passed in the full suite; parent spot-check repeated 37 focused updater/Prowlarr/WebAPI tests with 5 deprecation warnings.
  - Commits: `b50bae1` (safe WebUI settings updates), `bd0fb68` (runtime updater controls), `acd10dc` (schema-derived Prowlarr client), and `dab8dc8` (WebAPI endpoints).
  - Delivery note: updater, Prowlarr, and WebAPI units are 452, 424, and 440 authored lines respectively; each keeps production behavior with its tests instead of splitting code from proof.
  - RDD outcome: `disabled/unmanaged` (global mode is off).

- [x] **V110-03 — Build the Vue WebUI**
  - Route: delegated; new multi-file Vue application and responsive design system.
  - Add dashboard, general/update/result-processing/Prowlarr settings, preset UX, bounded custom rule builder, loading/error states, and accessible responsive light/dark navigation.
  - Use violet as the product primary and orange only for Prowlarr context; derive patterns from Downtify without copying code or branding.
  - Acceptance: dashboard shows service/database/result/Prowlarr state; settings persist; secrets never reappear; core workflows work on mobile and desktop.
  - Checks: frontend type/build checks plus focused component/store tests for critical configuration flows.
  - Evidence: formatting, 20 behavior tests, TypeScript checking, production build, and production/development audits passed; bundled CSS stayed byte-identical after modularization.
  - Commits: `c4960c2`, `2384806`, `5e56c91`, `a300748`, `7806d56`, `65d3f2d`, `7f4a018`, `4334c76`, `eaedb9e`, and `48c54db`.
  - Delivery note: 2,567 authored lines excluding the generated lockfile, split by API foundation, state hardening, design system, dashboard, settings, result processing, Prowlarr, and application shell. The 493-line responsive-style unit preserves one cohesive visual contract.
  - RDD outcome: `disabled/unmanaged` (global mode is off).

- [ ] **V110-04 — Integrate the single-container runtime**
  - Route: delegated; Docker build, FastAPI static fallback, startup behavior, and upgrade verification cross several files.
  - Add a Node build stage and copy only production frontend assets into the PostgreSQL/Python runtime.
  - Serve the SPA at `/` without shadowing `/api` or `/webapi`; keep `/data`, PostgreSQL binding, bootstrap, updater, and shutdown behavior unchanged.
  - Acceptance: fresh install exposes WebUI and Torznab; a v1.0 volume upgrades without losing PostgreSQL or snapshot state.
  - Checks: frontend/backend builds, Docker image build, caps XML, real search, affected movie/TV searches, persistence restart, and v1.0-volume upgrade scenario where feasible.
  - Status: implementation complete; Docker-dependent acceptance remains blocked because Docker CLI is unavailable in this environment.
  - Evidence: 22 focused and 87 full Python tests passed; static verification confirmed PostgreSQL 16, `/data`, copied modules, route ordering, and entrypoint invariants. Image build, container smoke, real search, restart, and v1.0-volume upgrade remain pending.
  - Commits: `183fd3c` (safe FastAPI SPA hosting) and `7168a29` (multi-stage single-container image).
  - RDD outcome: `disabled/unmanaged` (global mode is off).

- [x] **V110-05 — Publish cohesive product documentation**
  - Route: delegated; VitePress structure, shared visual tokens, workflows, README, and architecture docs span many files.
  - Add the requested Markdown-first navigation, shared violet/orange design language, responsive light/dark theme, Pages workflow, troubleshooting, API/configuration reference, and v1.0 upgrade path.
  - Document LAN/no-auth posture, Prowlarr reachability, environment/settings precedence, hard-filter versus ranking semantics, and downstream Radarr/Sonarr behavior.
  - Keep README focused on preview, features, quick start, WebUI, Prowlarr, and documentation links.
  - Acceptance: docs build locally; Pages workflow uses the correct base; user-visible behavior and architecture agree with implementation.
  - Checks: VitePress build, link/config review, README command validation.
  - Evidence: formatting and VitePress build passed with no broken internal links; production audit reports zero vulnerabilities; implementation contracts received independent source verification.
  - Commits: `a92643b`, `5d1e895`, `9bb828b`, `af57004`, `140f01a`, `495834c`, and `932af69`.
  - Risk: VitePress 1.6.4 currently resolves development-only Vite/esbuild advisories with no compatible automatic fix; static output and production dependencies are unaffected, and docs development remains localhost-only.
  - RDD outcome: `disabled/unmanaged` (global mode is off).

- [ ] **V110-06 — Final regression and release-readiness verification**
  - Route: delegated verification; full builds and runtime checks exceed the parent execution budget.
  - Run all backend/frontend/docs tests and builds, container smoke tests, real PostgreSQL search, secret/dump checks, and review every acceptance criterion.
  - Record all failed, unavailable, skipped, or environment-dependent checks honestly.
  - Acceptance: no known regression in Torznab or snapshot updates; remaining release risks are explicit.
  - Commit: pending if verification requires tracked fixes; otherwise N/A.
  - RDD outcome: pending.

## Progress and evidence

- Exploration completed against the repository, Prowlarr OpenAPI/controller sources, Downtify, Vue/Vite, FastAPI static serving, and VitePress deployment documentation.
- Current branch: `feature/v1.1.0`.
- Current task: `V110-06`; Docker CLI is now available, so V110-04 runtime verification resumes as part of final checks.
- Running authored-line count: 7,381 committed, excluding generated lockfiles.
- Reviewed boundary: branch point `d022024`.

## Next step

Run V110-06 release-readiness verification, including image build, fresh-container smoke, persistence restart, real PostgreSQL searches, and a disposable v1.0-volume upgrade where the published image is available.
