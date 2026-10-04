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
- Preserve the old GHCR image name through an explicit compatibility policy rather than assuming registry redirects.

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
- Work-unit commit: pending.

### VIO-02 — Distribution metadata and compatibility

- [ ] Update package and image metadata to Violarr.
- [ ] Keep stable volume, paths, environment variables, routes, snapshot source, and operational aliases.
- [ ] Define explicit old/new GHCR publishing compatibility.
- [ ] Update architecture, changelog, and agent guidance where public names changed.
- [ ] Strengthen container contract tests for preserved identifiers.

Route: delegated. Trigger: coordinated multi-file metadata and compatibility edits.

Acceptance:

- Existing v1.0 data and configuration contracts are unchanged.
- Future publishing can expose `ghcr.io/xbit18/violarr` without silently breaking the former image path.
- Snapshot updater still uses `xbit18/icvdb-snapshots`.

Checks:

```text
python -m pytest tests/test_container_contract.py tests/test_webapi.py tests/test_prowlarr.py
docker compose config
```

Evidence: pending.

### VIO-03 — Italian README and bilingual Pages

- [ ] Rewrite `README.md` as the Italian primary entry point.
- [ ] Add `README.en.md` with an obvious language switch.
- [ ] Configure VitePress root locale as Italian and `/en/` as English.
- [ ] Set Pages base to `/violarr/` and update repository/edit links.
- [ ] Translate the complete root documentation and preserve the English content under `docs/en/`.
- [ ] Update all clone, image, container, and documentation links consistently.

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

Evidence: pending.

### VIO-04 — GitHub repository transition and final bounded verification

- [ ] Rename `xbit18/icvdb-torznab` to `xbit18/violarr` using the authorized active GitHub session.
- [ ] Update local `origin` to `https://github.com/xbit18/violarr.git`.
- [ ] Push the authorized feature branch only.
- [ ] Confirm repository identity and exact Pages-ready URLs once.
- [ ] Run one final bounded verification covering Python, frontend, docs, Compose, image build, capabilities, and a real database search.

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

Evidence: pending.

## Progress

- [x] User approved Violarr branding, subtitle, Italian-first localization, repository rename, Pages path, and use of the active GitHub session.
- [x] Read-only inventory completed with compatibility boundaries and delivery forecast.
- [x] VIO-01 complete.
- [ ] VIO-02 complete.
- [ ] VIO-03 complete.
- [ ] VIO-04 complete.

## Next step

Commit VIO-01 as one reviewable work unit, record its identity, then implement VIO-02.
