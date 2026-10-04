# Result processing

Choose a preset in the WebUI. Start with **Unfiltered** to preserve v1.0 order,
then add processing only when you need it.

| Preset              | Behavior                                                                                     |
| ------------------- | -------------------------------------------------------------------------------------------- |
| `unfiltered`        | Preserves the database query order                                                           |
| `italian_preferred` | Ranks explicit Italian markers first, then `MULTI`/`DUAL`, without removing fallback results |
| `italian_only`      | Keeps only titles with explicit Italian markers                                              |
| `custom`            | Applies enabled score and exclusion rules                                                    |

::: warning Downstream selection

Ranking ICVDB results does not guarantee that Radarr or Sonarr will select the
top ICVDB item. Their own profiles, scoring, and availability rules still apply.

:::

::: danger Hard filters hide results

`italian_only` and custom `exclude` rules remove matching results before XML is
returned. Prowlarr cannot see or recover hidden results.

:::

Processing is stable for equal scores and local to fixed 1000-row database
windows. Read [result-processing internals](../how-it-works/result-processing)
before relying on ranking across deep pagination.
