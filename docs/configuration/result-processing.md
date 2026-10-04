# Elaborazione dei risultati

Scegli un preset nella WebUI. Parti da **Unfiltered** per conservare l'ordine di
v1.0 e abilita l'elaborazione solo quando serve.

| Preset              | Comportamento                                                                                 |
| ------------------- | --------------------------------------------------------------------------------------------- |
| `unfiltered`        | Conserva l'ordine della query al database                                                     |
| `italian_preferred` | Porta prima i marcatori italiani, poi `MULTI`/`DUAL`, senza rimuovere i risultati di fallback |
| `italian_only`      | Mantiene solo titoli con marcatori italiani espliciti                                         |
| `custom`            | Applica le regole abilitate di punteggio ed esclusione                                        |

::: warning Selezione downstream

L'ordine dei risultati ICVDB non garantisce che Radarr o Sonarr scelgano il
primo elemento: applicano profili, punteggi e regole di disponibilità propri.

:::

::: danger I filtri rigidi nascondono risultati

`italian_only` e le regole `exclude` rimuovono gli elementi prima dell'XML.
Prowlarr non può recuperarli.

:::

L'elaborazione è stabile a parità di punteggio ed è locale a finestre fisse di
1000 righe. Leggi i [dettagli interni](../how-it-works/result-processing) prima
di fare affidamento sull'ordinamento nella paginazione profonda.
