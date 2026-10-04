# Filtri personalizzati

Il preset `custom` valuta regole strutturate e limitate. Non supporta
espressioni regolari né script arbitrari.

## Campi delle regole

| Campo      | Operatori                            |
| ---------- | ------------------------------------ |
| `title`    | `contains`, `not_contains`, `equals` |
| `provider` | `contains`, `not_contains`, `equals` |
| `size`     | `equals`, `gte`, `lte`               |
| `seeders`  | `equals`, `gte`, `lte`               |

Ogni regola contiene `enabled`, `field`, `operator`, `value` e `action`.
`action` vale `score` o `exclude`; le regole di punteggio richiedono anche
`score`.

## Semantica degli operatori

| Tipo              | Comportamento                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------- |
| Testo             | Confronto Unicode case-folded; `contains` cerca una sottostringa, `equals` l'intero valore    |
| Testo mancante    | Corrisponde a `not_contains`, non a `contains` o `equals`                                     |
| Numero            | `equals`, `gte` e `lte` confrontano valori finiti; i booleani non sono numeri                 |
| Numero non valido | Un valore nullo, mancante, booleano, NaN o infinito non corrisponde mai a una regola numerica |

Limiti: massimo 100 regole; testo non vuoto fino a 512 caratteri; valori e
punteggi numerici finiti e non booleani; valore assoluto del punteggio fino
a 1000.

Le regole disabilitate non hanno effetto. Una regola `exclude` corrispondente
rimuove il risultato; gli altri sono ordinati per somma dei punteggi, mantenendo
stabile l'ordine a parità.

::: danger Visibilità

L'esclusione è un filtro rigido. Le righe nascoste non raggiungono Prowlarr.

:::
