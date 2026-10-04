# Priorità ai risultati italiani

Il preset `italian_preferred` porta in alto i titoli con marcatori riconosciuti
senza rimuovere i risultati di fallback.

## Ordine

1. I token esatti `ITA`, `ITALIAN` o `ITALIANO` ricevono 100 punti.
2. I token esatti `MULTI` o `DUAL` ricevono 25 punti.
3. Gli altri titoli ricevono 0 punti.

I token sono sequenze senza distinzione tra maiuscole e minuscole di lettere e
cifre ASCII. Così `ITA` non corrisponde all'interno di parole non correlate. A
parità di punteggio resta l'ordine del database.

`italian_only` mantiene solo corrispondenze `ITA`, `ITALIAN` o `ITALIANO`.
`MULTI` e `DUAL` sono indizi, non prove della presenza dell'audio italiano.

::: warning Ambito

La funzione ordina solo la risposta ICVDB. Non modifica il punteggio di Radarr,
Sonarr o Prowlarr e non garantisce la selezione downstream.

:::
