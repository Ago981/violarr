# Elaborazione dei risultati

Scegli in **Elaborazione risultati** cosa mostrare a Prowlarr. Parti da **Senza
filtri** e cambia preset solo quando sai quali risultati vuoi favorire o
nascondere.

- **Senza filtri** — scelta iniziale; include tutti i risultati nell'ordine
  originale.
- **Italiano preferito** — porta in alto le versioni probabilmente italiane
  senza nascondere le altre.
- **Solo italiano** — mostra solo titoli con indicatori italiani espliciti.
- **Personalizzato** — applica le
  [regole personalizzate](../features/custom-filters).

Premi **Salva elaborazione risultati** e attendi il messaggio di conferma.

::: warning Selezione downstream

L'ordine dei risultati ICVDB non garantisce che Radarr o Sonarr scelgano il
primo elemento: applicano profili, punteggi e regole di disponibilità propri.

:::

::: danger I filtri rigidi nascondono risultati

**Solo italiano** e le regole **Escludi** rimuovono i risultati prima che
Prowlarr possa riceverli.

:::

Approfondisci la [priorità italiana](../features/italian-ranking) o i
[dettagli tecnici](../how-it-works/result-processing).
