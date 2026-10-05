<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { AppStatus } from '../api/types'
import { useAppStore } from '../composables/appStore'
import StatusBadge from '../components/StatusBadge.vue'
import { useLocale } from '../i18n'

const props = defineProps<{
  status?: AppStatus | null
  loading?: boolean
  error?: string | null
  onRefresh?: () => Promise<void>
}>()
const store = useAppStore()
const locale = useLocale()
const { t } = locale
const refreshing = ref(false)
onMounted(() => {
  if (props.status === undefined) store.loadAll()
})
const data = computed(() => (props.status === undefined ? store.state.status : props.status))
const busy = computed(() => (props.loading ?? store.state.loading) || refreshing.value)
const failure = computed(() => (props.error === undefined ? store.state.error : props.error))
const presetLabel = (preset: string) =>
  ({
    unfiltered: t('preset.unfiltered'),
    italian_preferred: t('preset.italianPreferred'),
    italian_only: t('preset.italianOnly'),
    custom: t('preset.custom'),
  })[preset]
function relative(value: string | null) {
  if (!value) return t('common.notAvailable')
  const seconds = Math.round((new Date(value).getTime() - Date.now()) / 1000)
  const abs = Math.abs(seconds)
  const [amount, unit] =
    abs < 60
      ? [abs, 'second']
      : abs < 3600
        ? [Math.round(abs / 60), 'minute']
        : abs < 86400
          ? [Math.round(abs / 3600), 'hour']
          : [Math.round(abs / 86400), 'day']
  return new Intl.RelativeTimeFormat(locale.current.value, { numeric: 'auto' }).format(
    seconds < 0 ? -amount : amount,
    unit as Intl.RelativeTimeFormatUnit,
  )
}
const prowlarrText = computed(() => {
  const value = data.value?.prowlarr
  if (!value?.configured) return t('common.notConfigured')
  if (value.error) return `${t('common.error')}: ${value.error}`
  if (value.connected === null) return t('dashboard.configuredUnknown')
  if (!value.connected) return t('dashboard.configuredDisconnected')
  return value.indexer_installed
    ? t('dashboard.indexerInstalled')
    : t('dashboard.indexerNotInstalled')
})
async function refresh() {
  if (busy.value) return
  refreshing.value = true
  try {
    await (props.onRefresh ? props.onRefresh() : store.loadAll(true))
  } finally {
    refreshing.value = false
  }
}
</script>
<template>
  <section class="page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">{{ t('navigation.dashboard') }}</p>
        <h1>{{ t('dashboard.title') }}</h1>
        <p>{{ t('dashboard.intro') }}</p>
      </div>
      <button
        class="button button--secondary"
        type="button"
        :aria-label="t('dashboard.refreshLabel')"
        :disabled="busy"
        @click="refresh"
      >
        {{ refreshing ? t('dashboard.refreshing') : t('dashboard.refresh') }}
      </button>
    </div>
    <p v-if="busy" class="state-panel" role="status">{{ t('dashboard.loading') }}</p>
    <p v-else-if="failure" class="state-panel state-panel--danger" role="alert">{{ failure }}</p>
    <div v-else-if="data" class="dashboard-grid">
      <article class="card">
        <div class="card-heading">
          <h2>{{ t('dashboard.service') }}</h2>
          <StatusBadge
            :tone="data.database.connected ? 'success' : 'danger'"
            :label="data.database.connected ? t('dashboard.healthy') : t('dashboard.unavailable')"
          />
        </div>
        <dl class="detail-list">
          <div>
            <dt>{{ t('dashboard.application') }}</dt>
            <dd>v{{ data.application_version }}</dd>
          </div>
          <div>
            <dt>Web API</dt>
            <dd>v{{ data.api_version }}</dd>
          </div>
          <div>
            <dt>{{ t('dashboard.database') }}</dt>
            <dd>
              {{
                data.database.connected
                  ? t('dashboard.databaseConnected')
                  : t('dashboard.databaseUnavailable')
              }}
            </dd>
          </div>
        </dl>
      </article>
      <article class="card">
        <div class="card-heading">
          <h2>{{ t('dashboard.snapshot') }}</h2>
          <StatusBadge
            :tone="
              data.updater.last_error ? 'danger' : data.updater.updating ? 'warning' : 'success'
            "
            :label="
              data.updater.last_error
                ? t('common.error')
                : data.updater.updating
                  ? t('common.updating')
                  : data.updater.enabled
                    ? t('common.enabled')
                    : t('common.disabled')
            "
          />
        </div>
        <dl class="detail-list">
          <div>
            <dt>{{ t('dashboard.installed') }}</dt>
            <dd>{{ data.updater.installed_version ?? t('common.unknown') }}</dd>
          </div>
          <div>
            <dt>{{ t('dashboard.latest') }}</dt>
            <dd>{{ data.updater.latest_version ?? t('dashboard.notChecked') }}</dd>
          </div>
          <div>
            <dt>{{ t('dashboard.lastNextCheck') }}</dt>
            <dd>
              {{ relative(data.updater.last_check) }} · {{ relative(data.updater.next_check) }}
            </dd>
          </div>
          <div>
            <dt>{{ t('dashboard.maintenance') }}</dt>
            <dd>{{ data.updater.maintenance ? t('common.active') : t('common.inactive') }}</dd>
          </div>
        </dl>
        <p v-if="data.updater.last_error" class="inline-error">{{ data.updater.last_error }}</p>
        <RouterLink to="/database">{{ t('dashboard.manageUpdates') }}</RouterLink>
      </article>
      <article class="card">
        <div class="card-heading">
          <h2>{{ t('dashboard.resultProcessing') }}</h2>
          <StatusBadge :label="t('common.active')" tone="success" />
        </div>
        <p class="metric">{{ presetLabel(data.result_processing.preset) }}</p>
        <p>
          {{ t('dashboard.rulesConfigured', { count: data.result_processing.custom_rule_count }) }}
        </p>
        <RouterLink to="/result-processing">{{ t('dashboard.configureResults') }}</RouterLink>
      </article>
      <article class="card card--prowlarr">
        <div class="card-heading">
          <h2>Prowlarr</h2>
          <StatusBadge
            :tone="
              data.prowlarr.error || data.prowlarr.connected === false
                ? 'danger'
                : data.prowlarr.connected
                  ? 'success'
                  : 'neutral'
            "
            :label="
              data.prowlarr.connected
                ? t('common.connected')
                : data.prowlarr.configured
                  ? t('common.unknown')
                  : t('common.notConfigured')
            "
          />
        </div>
        <p class="metric metric--small">{{ prowlarrText }}</p>
        <RouterLink class="prowlarr-link" to="/prowlarr">{{
          t('dashboard.manageProwlarr')
        }}</RouterLink>
      </article>
    </div>
  </section>
</template>
