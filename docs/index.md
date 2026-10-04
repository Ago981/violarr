---
layout: home

hero:
  name: Violarr
  text: L’integrazione Prowlarr per Il Corsaro Viola
  tagline:
    PostgreSQL, API Torznab, aggiornamenti del database e WebUI in un solo
    container.
  actions:
    - theme: brand
      text: Installa con Docker
      link: /getting-started/installation
    - theme: alt
      text: Configura Prowlarr
      link: /configuration/prowlarr

features:
  - title: Compatibile con Torznab
    details: Cerca film, serie TV e anime da Prowlarr tramite l'endpoint /api.
  - title: Elaborazione utile dei risultati
    details:
      Preferisci o richiedi marcatori italiani espliciti oppure crea regole
      limitate di punteggio ed esclusione.
  - title: Aggiornamenti snapshot sicuri
    details:
      Convalida un database candidato prima di una breve sostituzione in
      manutenzione, con rollback in caso di errore.
---

## Inizia da qui

Violarr è un adattatore leggero tra uno snapshot PostgreSQL di ICVDB e client
compatibili con Torznab. Non scarica torrent e non gestisce librerie
multimediali.

1. [Avvia il container](/getting-started/installation).
2. Apri la WebUI su `http://localhost:8000`.
3. [Collega Prowlarr](/configuration/prowlarr).

::: danger Esposizione di rete

L'applicazione non ha autenticazione. Mantieni la porta `8000` su una rete
affidabile o usa un reverse proxy autenticato.

:::
