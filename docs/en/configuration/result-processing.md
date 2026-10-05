# Result processing

Choose what Prowlarr receives under **Result processing**. Start with
**Unfiltered** and change preset only when you know which results you want to
promote or hide.

- **Unfiltered** — starting choice; includes every result in its original order.
- **Italian preferred** — promotes likely Italian releases without hiding the
  alternatives.
- **Italian only** — shows only titles with explicit Italian markers.
- **Custom** — applies your [custom rules](../features/custom-filters).

Select **Save result processing** and wait for the confirmation message.

::: warning Downstream selection

Ranking ICVDB results does not guarantee that Radarr or Sonarr will select the
top ICVDB item. Their own profiles, scoring, and availability rules still apply.

:::

::: danger Hard filters hide results

**Italian only** and custom **Exclude** rules remove results before Prowlarr can
receive them.

:::

Read more about [Italian ranking](../features/italian-ranking) or the
[technical details](../how-it-works/result-processing).
