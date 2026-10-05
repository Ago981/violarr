# Italian ranking

Choose **Italian preferred** to promote titles with recognized markers without
hiding alternatives.

## Ranking order

1. Exact title tokens `ITA`, `ITALIAN`, or `ITALIANO` receive score 100.
2. Exact title tokens `MULTI` or `DUAL` receive score 25.
3. Other titles receive score 0.

Tokens are case-insensitive sequences of ASCII letters and digits. This avoids
matching `ITA` inside unrelated words. Equal scores retain database order.

**Italian only** is stricter: it keeps only `ITA`, `ITALIAN`, or `ITALIANO`
token matches. `MULTI` and `DUAL` alone are ranking hints, not proof of Italian
audio.

::: warning Scope

This feature ranks ICVDB's response only. It does not change Radarr, Sonarr, or
Prowlarr scoring and cannot guarantee downstream selection.

:::
