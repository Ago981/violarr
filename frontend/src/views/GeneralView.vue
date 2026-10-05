<script setup lang="ts">
import { useLocale } from '../i18n'

const { t } = useLocale()
</script>
<template>
  <section class="page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">{{ t('common.settings') }}</p>
        <h1>{{ t('general.title') }}</h1>
        <p>{{ t('general.intro') }}</p>
      </div>
    </div>
    <article class="card prose">
      <h2>Violarr</h2>
      <p>{{ t('app.subtitle') }}</p>
      <p>{{ t('general.description') }}</p>
      <div class="notice">
        <strong>{{ t('general.trustedLan') }}</strong>
        <p>{{ t('general.security') }}</p>
      </div>
      <dl class="detail-list">
        <div>
          <dt>{{ t('general.mainEndpoint') }}</dt>
          <dd><code>/api</code></dd>
        </div>
        <div>
          <dt>Web API</dt>
          <dd><code>/webapi</code></dd>
        </div>
        <div>
          <dt>{{ t('general.configuration') }}</dt>
          <dd>{{ t('general.persisted') }}</dd>
        </div>
      </dl>
    </article>
  </section>
</template>
