# Prima configurazione

Completa la configurazione iniziale dalla WebUI.

1. Apri `http://localhost:8000/`.
2. In **Panoramica**, verifica che il servizio sia **Operativo**.
3. Lascia **Senza filtri** per iniziare, oppure scegli un
   [preset di elaborazione](../configuration/result-processing).
4. [Collega Prowlarr](../configuration/prowlarr).

Se il servizio non è operativo, premi **Aggiorna**. Se lo stato resta rosso,
apri la [risoluzione dei problemi](../troubleshooting).

## Sicurezza prima della condivisione

La WebUI non ha autenticazione. Non pubblicare la porta `8000` direttamente su
Internet: usa una LAN affidabile o un reverse proxy autenticato.
