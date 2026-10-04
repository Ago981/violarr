<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '../composables/appStore'
import { useLocale } from '../i18n'
const store = useAppStore()
const { t } = useLocale()
onMounted(() => store.loadAll())
</script>
<template>
  <section class="page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">{{ t('common.diagnostics') }}</p>
        <h1>{{ t('advanced.title') }}</h1>
        <p>{{ t('advanced.intro') }}</p>
      </div>
    </div>
    <article class="card">
      <h2>{{ t('advanced.endpoints') }}</h2>
      <dl class="detail-list">
        <div>
          <dt>Torznab</dt>
          <dd><code>/api</code></dd>
        </div>
        <div>
          <dt>{{ t('advanced.status') }}</dt>
          <dd><code>/webapi/status</code></dd>
        </div>
        <div>
          <dt>{{ t('common.settings') }}</dt>
          <dd><code>/webapi/settings</code></dd>
        </div>
        <div>
          <dt>{{ t('advanced.resultProcessing') }}</dt>
          <dd><code>/webapi/result-processing</code></dd>
        </div>
      </dl>
    </article>
    <article class="card prose">
      <h2>{{ t('advanced.precedence') }}</h2>
      <p>{{ t('advanced.precedenceText') }}</p>
      <p>{{ t('advanced.secrets') }}</p>
    </article>
  </section>
</template>
