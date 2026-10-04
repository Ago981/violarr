# Snapshot system

Snapshots are PostgreSQL custom-format dumps published as GitHub Release assets
by [`xbit18/icvdb-snapshots`](https://github.com/xbit18/icvdb-snapshots).

## Discovery and validation

1. Request the configured latest-release API URL.
2. Select the first asset whose name ends in `.dump`.
3. Require the asset metadata to contain a `sha256:` digest.
4. Download the asset and verify SHA256.
5. Run `pg_restore --list` before attempting a restore.
6. Restore into `icv_db_candidate` with restore errors treated as fatal.
7. Connect to the candidate and require user tables.

The installed release tag is written atomically to
`/data/state/snapshot-version` only after a successful switch and final
validation.

`SNAPSHOT_LATEST_URL` can point discovery at another compatible GitHub-style
release response. The implementation expects `tag_name`, a `.dump` asset,
`browser_download_url`, and a GitHub asset digest.
