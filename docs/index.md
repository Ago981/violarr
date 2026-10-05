---
layout: home

hero:
  name: Violarr
  text: Usa il database ICVDB direttamente con Prowlarr
  tagline: Avvia Violarr, apri la WebUI e collega Prowlarr in pochi passaggi.
  actions:
    - theme: brand
      text: Avvia Violarr
      link: /getting-started/installation
    - theme: alt
      text: Apri la guida WebUI
      link: /configuration/webui

features:
  - title: Tutto dal browser
    details:
      Controlla lo stato, collega Prowlarr e salva le impostazioni dalla WebUI.
  - title: Risultati adatti a te
    details:
      Preferisci l’italiano, filtra i risultati o crea regole personalizzate.
  - title: Database sempre pronto
    details:
      Controlla la versione installata e gestisci gli aggiornamenti automatici.
---

## Inizia da qui

1. [Avvia il container](/getting-started/installation).
2. Apri `http://localhost:8000/` nel browser.
3. [Collega Prowlarr](/configuration/prowlarr).

::: danger Esposizione di rete

L'applicazione non ha autenticazione. Mantieni la porta `8000` su una rete
affidabile o usa un reverse proxy autenticato.

:::
