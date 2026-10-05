# PostgreSQL

PostgreSQL 16 runs inside the application container. It listens on
`127.0.0.1:5432`, is consumed by FastAPI and the snapshot updater, and is not
published to the host.

Persistent cluster data lives at `/data/postgres`. The service treats the ICVDB
schema as external and uses read-only search queries during normal requests.
HTTP values are passed through psycopg parameter binding.

## Database roles during updates

| Name               | Purpose                                   |
| ------------------ | ----------------------------------------- |
| `icv_db`           | Active application database               |
| `icv_db_candidate` | Restore and validation target             |
| `icv_db_previous`  | Temporary rollback source during a switch |

Do not expose port `5432` or mount a second database volume. The supported
persistence boundary is the single `/data` volume.
