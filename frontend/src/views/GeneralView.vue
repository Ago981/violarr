<template>
  <section class="page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">Settings</p>
        <h1>General</h1>
        <p>Application identity and network posture.</p>
      </div>
    </div>
    <article class="card prose">
      <h2>ICVDB Torznab</h2>
      <p>
        This service is a thin, read-only bridge between your local ICVDB PostgreSQL snapshot and
        Torznab clients.
      </p>
      <div class="notice">
        <strong>Designed for a trusted LAN</strong>
        <p>
          The WebUI has no built-in authentication. Do not expose it directly to the public
          internet.
        </p>
      </div>
      <dl class="detail-list">
        <div>
          <dt>Main Torznab endpoint</dt>
          <dd><code>/api</code></dd>
        </div>
        <div>
          <dt>Web API</dt>
          <dd><code>/webapi</code></dd>
        </div>
        <div>
          <dt>Configuration</dt>
          <dd>Persisted under the service data volume</dd>
        </div>
      </dl>
    </article>
  </section>
</template>
