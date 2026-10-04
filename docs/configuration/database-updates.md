# Aggiornamenti del database

Nella WebUI usa **Aggiornamenti database** per abilitare o disabilitare i
controlli periodici e impostare un intervallo tra 60 e 604800 secondi.

| Impostazione                | Valore predefinito |
| --------------------------- | ------------------ |
| Abilitati                   | `true`             |
| Intervallo                  | `86400` secondi    |
| Ritardo del primo controllo | `60` secondi       |

Il ritardo iniziale è configurabile solo tramite ambiente. Stato e intervallo
sono salvati nello schema v1, salvo override con `DB_AUTO_UPDATE` o
`DB_UPDATE_INTERVAL`.

Gli aggiornamenti usano un database candidato e restituiscono brevemente HTTP
`503` solo durante la sostituzione finale. Consulta gli
[aggiornamenti sicuri](../how-it-works/safe-updates).
