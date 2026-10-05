# Panoramica WebUI

Apri `http://HOST:8000/` per controllare Violarr e modificarne le impostazioni.

## Cosa trovi

- **Panoramica** mostra stato ed errori. Tutte le schede devono essere sane.
- **Generali** mostra identità, sicurezza e indirizzi. Non richiede azioni.
- **Aggiornamenti database** gestisce i controlli. Di norma: ogni 24 ore.
- **Elaborazione risultati** gestisce preset e regole. Inizia senza filtri.
- **Prowlarr** salva la connessione. Lo stato atteso è **Connesso**.
- **Avanzate** è una vista in sola lettura e non richiede azioni.

## Salvare e verificare

- Ogni pagina salva solo quando premi il relativo pulsante **Salva**.
- Attendi il messaggio di conferma prima di cambiare pagina.
- La chiave API salvata non viene mostrata: usa **Sostituisci chiave** solo per
  cambiarla.

## Se lo stato non è operativo

1. Premi **Aggiorna** in **Panoramica**.
2. Leggi l'errore nella scheda rossa e apri l'area indicata dal problema.
3. Se l'errore resta, consulta la [risoluzione dei problemi](../troubleshooting)
   e i log del container.

La WebUI non ha autenticazione: esponila solo su una rete affidabile o dietro un
reverse proxy autenticato.
