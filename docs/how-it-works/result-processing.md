# Pipeline di elaborazione dei risultati

L'elaborazione si colloca tra i risultati SQL e la generazione dell'XML Torznab.

## Percorso senza filtri

`unfiltered` passa `limit` e `offset` direttamente a SQL e conserva l'ordine di
v1.0.

## Percorso elaborato

Con gli altri preset, la pagina richiesta viene associata a finestre fisse e non
sovrapposte di 1000 righe. Ogni finestra necessaria viene interrogata ed
elaborata indipendentemente, quindi viene restituita la porzione locale
richiesta.

Questo limita la memoria e supporta offset arbitrari, comprese pagine a cavallo
tra finestre. Ordinamento e filtri sono quindi **locali alla finestra**, non
globali sull'intero insieme dei risultati.

## Garanzie sull'ordine

- La priorità italiana usa punteggi basati sui token del titolo.
- L'ordinamento personalizzato somma tutte le regole di punteggio
  corrispondenti.
- Lo stable sort di Python conserva l'ordine originale a parità di punteggio.
- Le esclusioni sono applicate prima dei punteggi personalizzati.

I filtri rigidi possono produrre pagine con meno elementi: la paginazione taglia
la finestra elaborata e le righe nascoste non sono sostituite da finestre
successive.
