# Database updates

Use **Database updates** in the WebUI to enable or disable periodic checks and
set an interval from 60 seconds to 604800 seconds (seven days).

Defaults:

| Setting                    | Default         |
| -------------------------- | --------------- |
| Enabled                    | `true`          |
| Interval                   | `86400` seconds |
| First periodic check delay | `60` seconds    |

The start delay is environment-only. The enabled state and interval are stored
in settings schema v1 unless overridden by `DB_AUTO_UPDATE` or
`DB_UPDATE_INTERVAL`.

Updates use a candidate database and briefly return HTTP `503` only during the
final switch. See [safe updates](../how-it-works/safe-updates).
