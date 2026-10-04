# Violarr rebrand and Italian-first localization

## Objective

Rebrand the application as **Violarr**, make Italian the default user-facing language while retaining English, rename the public GitHub repository to `xbit18/violarr`, and publish project documentation below `/violarr/` without breaking existing runtime installations.

## Problem and why

The current public identity (`icvdb-torznab`) describes the implementation rather than the product. User-facing content is English-only and the Pages base is tied to the old repository name. Violarr needs a coherent identity and Italian-first experience while preserving the stable technical contracts already used by v1.0 installations.

## Brand

- Product name: **Violarr**
- Subtitle: **L’integrazione Prowlarr per Il Corsaro Viola**
- Technical description: self-hosted Torznab indexer connecting ICVDB to Prowlarr

## Authorized scope

- Rebrand user-visible application, documentation, metadata, and Prowlarr display name.
- Add Italian-default and English-selectable WebUI localization.
- Make VitePress Italian-first with an English mirror under `/en/`.
- Make `README.md` Italian-first and provide `README.en.md`.
- Rename `xbit18/icvdb-torznab` to `xbit18/violarr`, update links, Pages base, local origin, and the authorized feature branch.
- Publish only `ghcr.io/xbit18/violarr`; do not retain a legacy GHCR publishing alias.

## Compatibility constraints

The following contracts remain unchanged:

- `/data` and `/data/state/settings.json`
- settings schema version 1
- `ICVDB_*` and `DB_*` environment variables
- `/api` and `/webapi`
- PostgreSQL schema and snapshot semantics
- named volume `icvdb_torznab_data`
- snapshot repository `xbit18/icvdb-snapshots`
- legacy theme key `icvdb-theme`
- operational Compose aliases required by existing Prowlarr URLs

Internal code identifiers, API contracts, comments, and commit messages remain English unless localization requires a user-visible message.

## Delivery strategy

- Strategy: `ask-on-risk`, previously resolved to `feature-branch-chain` for oversized work.
- Forecast: 2,200–3,400 authored changed lines.
- Boundaries: three coherent implementation commits plus one remote repository transition.
- No pull request, release, tag, or merge is authorized.
- Documentation translation may use a size exception inside its coherent slice rather than artificial splitting.
- Conservative cadence: one inventory, one implementation pass per work unit, and one focused verification boundary per work unit. No frequent polling.

## Tasks

### VIO-01 — Runtime branding and bilingual WebUI

- [x] Replace public product branding with Violarr and the approved subtitle.
- [x] Add stable localization keys with Italian default and English selection.
- [x] Persist language client-side without changing server settings schema.
- [x] Preserve and continue reading `icvdb-theme`.
- [x] Rename the Torznab/Prowlarr display name without changing endpoint-based idempotency.
- [x] Update behavior-focused frontend and backend tests.

Route: delegated. Trigger: multi-file implementation and read-before-write preparation.

Acceptance:

- First load is Italian.
- English can be selected and persists across reloads.
- Navigation, views, validation, feedback, theme labels, and document metadata are localized.
- Existing theme preference remains effective.
- Existing Prowlarr indexers remain detectable by endpoint.

Checks:

```text
python -m pytest tests/test_prowlarr.py tests/test_torznab_regression.py
npm --prefix frontend run format:check
npm --prefix frontend run typecheck
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

Evidence:

- Observed RED: focused i18n test failed before `frontend/src/i18n/` existed.
- Observed GREEN: 23 frontend tests passed; formatting, typecheck, and production build passed.
- Backend branding regressions: 28 tests passed in one isolated `uv` environment.
- Independent verification found and closed one localization-boundary issue for server-origin errors.
- RDD: globally disabled. Native risk assessment was unassessable because authorized untracked files required declaration; independent verification was used conservatively.
- Work-unit commit: `e979460` (`feat(webui): add Violarr localization`).

### VIO-02 — Distribution metadata and compatibility

- [x] Update package and image metadata to Violarr.
- [x] Keep stable volume, paths, environment variables, routes, snapshot source, and operational aliases.
- [x] Publish only the new Violarr GHCR image.
- [x] Update architecture, changelog, and agent guidance where public names changed.
- [x] Strengthen container contract tests for preserved identifiers.

Route: delegated. Trigger: coordinated multi-file metadata and compatibility edits.

Acceptance:

- Existing v1.0 data and configuration contracts are unchanged.
- Future publishing exposes only `ghcr.io/xbit18/violarr`.
- Snapshot updater still uses `xbit18/icvdb-snapshots`.

Checks:

```text
python -m pytest tests/test_container_contract.py tests/test_webapi.py tests/test_prowlarr.py
docker compose config
```

Evidence:

- Observed RED: OCI metadata contract failed before the Violarr title was added.
- Observed GREEN: 37 focused Python tests passed; independent container-contract verification passed 11 tests.
- `docker compose config` resolved `ghcr.io/xbit18/violarr:latest` while retaining service/container `icvdb-torznab`, `/data`, and volume `icvdb_torznab_data`.
- Release workflow uses one metadata/build path for only `ghcr.io/xbit18/violarr`, with least-privilege permissions and no shell steps.
- The former GHCR package is intentionally not maintained; live publishing remains unexecuted until a release is explicitly authorized.
- Work-unit commit: `55bc917` (`build: target Violarr image`).

### VIO-03 — Italian README and bilingual Pages

- [x] Rewrite `README.md` as the Italian primary entry point.
- [x] Add `README.en.md` with an obvious language switch.
- [x] Configure VitePress root locale as Italian and `/en/` as English.
- [x] Set Pages base to `/violarr/` and update repository/edit links.
- [x] Translate the complete root documentation and preserve the English content under `docs/en/`.
- [x] Update all clone, image, container, and documentation links consistently.

Route: delegated. Trigger: broad documentation rewrite across more than four files.

Acceptance:

- Italian and English navigation cover equivalent documentation.
- Internal links build correctly under `/violarr/` and `/violarr/en/`.
- No published link points to the obsolete Pages base.
- Examples preserve stable technical identifiers where compatibility requires them.

Checks:

```text
npm --prefix docs run format:check
npm --prefix docs run docs:build
```

Evidence:

- Italian `README.md` and all root documentation pages have equivalent English versions in `README.en.md` and `docs/en/`.
- VitePress uses `/violarr/`, Italian root, English `/en/`, and locale-specific header, sidebar, outline, and previous/next labels.
- Fixed 23 malformed custom containers whose inline markers captured later page content and disrupted pagination flow.
- Final `format:check` and VitePress production build passed; rendered Italian and English pages show correct navigation, sidebar, callout boundaries, and previous/next controls.
- Work-unit commit: `41fffa7` (`docs: add bilingual Violarr guide`).

### VIO-04 — GitHub repository transition and final bounded verification

- [x] Rename `xbit18/icvdb-torznab` to `xbit18/violarr` using the authorized active GitHub session.
- [x] Update local `origin` to `https://github.com/xbit18/violarr.git`.
- [ ] Push the authorized feature branch only.
- [x] Confirm repository identity and exact Pages-ready URLs once.
- [x] Run one final bounded verification covering Python, frontend, docs, Compose, image build, capabilities, and a real database search.

Route: delegated verification plus parent-owned remote state operations. Trigger: full suites/builds belong to fresh workers; GitHub state remains parent-owned.

Acceptance:

- Repository is available at `https://github.com/xbit18/violarr`.
- Documentation is configured for `https://xbit18.github.io/violarr/`.
- No release, tag, pull request, or merge is created.
- All required checks report observed results, including any skipped or environmental failures.

Checks:

```text
python -m pytest
npm --prefix frontend run format:check
npm --prefix frontend run typecheck
npm --prefix frontend test -- --run
npm --prefix frontend run build
npm --prefix docs run format:check
npm --prefix docs run docs:build
docker compose config
docker build -t violarr:verify .
curl -fsS 'http://localhost:8000/api?t=caps'
curl -fsS 'http://localhost:8000/api?t=search&q=avatar'
```

Evidence:

- GitHub reports `xbit18/violarr` at `https://github.com/xbit18/violarr`; local fetch and push remotes use `https://github.com/xbit18/violarr.git`.
- VitePress remains configured for `https://xbit18.github.io/violarr/`; deployment still requires the documentation commit to reach `main`.
- Python suite passed 99 tests in an isolated `uv` environment; the direct interpreter lacked pytest and the first isolated run lacked the `httpx` test dependency.
- Frontend formatting, type checking, 23 tests, and production build passed; documentation formatting and production build passed.
- Compose configuration resolved `ghcr.io/xbit18/violarr:latest`; the image built locally, the container started, caps returned `<caps>`, and an `avatar` search returned populated Torznab RSS from PostgreSQL.
- Verification left the tracked worktree clean. No release, tag, pull request, or merge was created.

## Progress

- [x] User approved Violarr branding, subtitle, Italian-first localization, repository rename, Pages path, and use of the active GitHub session.
- [x] Read-only inventory completed with compatibility boundaries and delivery forecast.
- [x] VIO-01 complete.
- [x] VIO-02 complete.
- [x] VIO-03 complete.
- [ ] VIO-04 complete.

## Next step

Push the authorized feature branch, then record the final remote evidence and close VIO-04.
