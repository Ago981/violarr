<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { AppStatus } from '../api/types'
import { useAppStore } from '../composables/appStore'
import StatusBadge from '../components/StatusBadge.vue'

const props = defineProps<{
  status?: AppStatus | null
  loading?: boolean
  error?: string | null
  onRefresh?: () => Promise<void>
}>()
const store = useAppStore()
const refreshing = ref(false)
onMounted(() => {
  if (props.status === undefined) store.loadAll()
})
const data = computed(() => (props.status === undefined ? store.state.status : props.status))
const busy = computed(() => (props.loading ?? store.state.loading) || refreshing.value)
const failure = computed(() => (props.error === undefined ? store.state.error : props.error))
const presets: Record<string, string> = {
  unfiltered: 'Unfiltered',
  italian_preferred: 'Italian preferred',
  italian_only: 'Italian only',
  custom: 'Custom',
}
function relative(value: string | null) {
  if (!value) return 'Not available'
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
  return new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' }).format(
    seconds < 0 ? -amount : amount,
    unit as Intl.RelativeTimeFormatUnit,
  )
}
const prowlarrText = computed(() => {
  const value = data.value?.prowlarr
  if (!value?.configured) return 'Not configured'
  if (value.error) return `Error: ${value.error}`
  if (value.connected === null) return 'Configured; connection unknown'
  if (!value.connected) return 'Configured; disconnected'
  return value.indexer_installed
    ? 'Connected; indexer installed'
    : 'Connected; indexer not installed'
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
        <p class="eyebrow">Overview</p>
        <h1>Dashboard</h1>
        <p>Current health and configuration at a glance.</p>
      </div>
      <button
        class="button button--secondary"
        type="button"
        aria-label="Refresh status"
        :disabled="busy"
        @click="refresh"
      >
        {{ refreshing ? 'Refreshing…' : 'Refresh' }}
      </button>
    </div>
    <p v-if="busy" class="state-panel" role="status">Loading system status…</p>
    <p v-else-if="failure" class="state-panel state-panel--danger" role="alert">{{ failure }}</p>
    <div v-else-if="data" class="dashboard-grid">
      <article class="card">
        <div class="card-heading">
          <h2>Service</h2>
          <StatusBadge
            :tone="data.database.connected ? 'success' : 'danger'"
            :label="data.database.connected ? 'Healthy' : 'Unavailable'"
          />
        </div>
        <dl class="detail-list">
          <div>
            <dt>Application</dt>
            <dd>v{{ data.application_version }}</dd>
          </div>
          <div>
            <dt>Web API</dt>
            <dd>v{{ data.api_version }}</dd>
          </div>
          <div>
            <dt>Database</dt>
            <dd>
              {{ data.database.connected ? 'PostgreSQL connected' : 'PostgreSQL unavailable' }}
            </dd>
          </div>
        </dl>
      </article>
      <article class="card">
        <div class="card-heading">
          <h2>Database snapshot</h2>
          <StatusBadge
            :tone="
              data.updater.last_error ? 'danger' : data.updater.updating ? 'warning' : 'success'
            "
            :label="
              data.updater.last_error
                ? 'Error'
                : data.updater.updating
                  ? 'Updating'
                  : data.updater.enabled
                    ? 'Enabled'
                    : 'Disabled'
            "
          />
        </div>
        <dl class="detail-list">
          <div>
            <dt>Installed</dt>
            <dd>{{ data.updater.installed_version ?? 'Unknown' }}</dd>
          </div>
          <div>
            <dt>Latest</dt>
            <dd>{{ data.updater.latest_version ?? 'Not checked' }}</dd>
          </div>
          <div>
            <dt>Last / next check</dt>
            <dd>
              {{ relative(data.updater.last_check) }} · {{ relative(data.updater.next_check) }}
            </dd>
          </div>
          <div>
            <dt>Maintenance</dt>
            <dd>{{ data.updater.maintenance ? 'Active' : 'Inactive' }}</dd>
          </div>
        </dl>
        <p v-if="data.updater.last_error" class="inline-error">{{ data.updater.last_error }}</p>
        <RouterLink to="/database">Manage updates →</RouterLink>
      </article>
      <article class="card">
        <div class="card-heading">
          <h2>Result processing</h2>
          <StatusBadge label="Active" tone="success" />
        </div>
        <p class="metric">{{ presets[data.result_processing.preset] }}</p>
        <p>{{ data.result_processing.custom_rule_count }} custom rules configured.</p>
        <RouterLink to="/result-processing">Configure results →</RouterLink>
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
                ? 'Connected'
                : data.prowlarr.configured
                  ? 'Unknown'
                  : 'Not configured'
            "
          />
        </div>
        <p class="metric metric--small">{{ prowlarrText }}</p>
        <RouterLink class="prowlarr-link" to="/prowlarr">Manage Prowlarr →</RouterLink>
      </article>
    </div>
  </section>
</template>
