<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '../composables/appStore'
const store = useAppStore()
onMounted(() => store.loadAll())
</script>
<template>
  <section class="page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">Diagnostics</p>
        <h1>Advanced</h1>
        <p>Read-only endpoints and effective configuration details.</p>
      </div>
    </div>
    <article class="card">
      <h2>Service endpoints</h2>
      <dl class="detail-list">
        <div>
          <dt>Torznab</dt>
          <dd><code>/api</code></dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd><code>/webapi/status</code></dd>
        </div>
        <div>
          <dt>Settings</dt>
          <dd><code>/webapi/settings</code></dd>
        </div>
        <div>
          <dt>Result processing</dt>
          <dd><code>/webapi/result-processing</code></dd>
        </div>
      </dl>
    </article>
    <article class="card prose">
      <h2>Configuration precedence</h2>
      <p>
        Environment variables can override persisted values at runtime. If a setting appears to
        revert after saving, inspect the container environment.
      </p>
      <p>Secrets are intentionally excluded from this page and all normal read responses.</p>
    </article>
  </section>
</template>
