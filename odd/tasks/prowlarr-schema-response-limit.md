# Prowlarr schema response limit

## Objective

Allow real-world Prowlarr indexer-schema responses larger than 1 MiB without weakening the existing response-size protection for normal API calls.

## Problem and why

`GET /api/v1/indexer/schema` can return about 5.8 MiB. The generic 1 MiB response limit currently rejects that valid response, so Violarr reports a generic Prowlarr connection failure despite valid connectivity and credentials.

## Authorized scope

- Add one schema-specific response limit, preferably 16 MiB.
- Let `ProwlarrClient._request()` accept an optional per-request response-size override.
- Use the override only from `_schemas()`.
- Add focused automated coverage for schema and normal-response boundaries.
- Do not change WebUI, settings, Docker, timeout, JSON handling, or unrelated Prowlarr behavior.

## Task

- [x] Inspect the current client and tests before editing.
- [x] Add failing tests for the three required size-boundary cases.
- [x] Implement the localized per-request override while preserving all existing guards.
- [x] Run focused and full relevant Prowlarr tests.
- [x] Record verification and commit evidence.

Route: delegated direct writer. Trigger: coordinated behavior and test changes span two non-trivial files.

Forecast: fewer than 100 authored changed lines. Delivery strategy: `ask-on-risk`; no split expected.

## Acceptance

- Schema responses between 1 MiB and 16 MiB succeed.
- Normal responses above 1 MiB still raise `ProwlarrError("Prowlarr response is too large")`.
- Schema responses above 16 MiB raise the same error.
- Content-Length and streamed `limit + 1` protections remain active.
- Timeout and JSON validation/error behavior remain unchanged.
- Existing Prowlarr tests pass.

## Evidence

- Observed RED: the schema response above 1 MiB was rejected by the generic limit; 20 tests passed and 1 failed.
- Observed GREEN: all 21 focused Prowlarr tests passed.
- Added coverage for accepted schema responses between 1 MiB and 16 MiB, rejected normal responses above 1 MiB, and rejected schema responses above 16 MiB.
- Preserved Content-Length, streamed `limit + 1`, timeout, JSON validation, and exact oversized-response error behavior.
- Native assessment classified the 94-line candidate as medium risk and under budget.
- Work-unit commit: `881c63c` (`fix(prowlarr): allow larger schema responses`).

## Next step

Push the focused fix branch when authorized.
