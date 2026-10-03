<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import ToggleSwitch from '../components/ToggleSwitch.vue'
import { useAppStore } from '../composables/appStore'
import type { PublicSettings } from '../api/types'
const props = defineProps<{
  settings?: PublicSettings
  saveSettings?: (settings: PublicSettings) => Promise<unknown>
}>()
const store = useAppStore()
const enabled = ref(true)
const interval = ref(86400)
const localError = ref('')
const saving = ref(false)
onMounted(() => {
  if (!props.settings) store.loadAll()
})
const source = computed(() => props.settings ?? store.state.settings)
watch(
  source,
  (settings) => {
    if (settings) {
      enabled.value = settings.database_update.enabled
      interval.value = settings.database_update.interval_seconds
    }
  },
  { immediate: true },
)
const hours = computed({
  get: () => interval.value / 3600,
  set: (value: number) => {
    interval.value = Math.round(value * 3600)
  },
})
async function save() {
  localError.value = ''
  if (!Number.isFinite(interval.value) || interval.value < 60 || interval.value > 604800) {
    localError.value = 'Interval must be between 1 minute and 7 days.'
    return
  }
  if (!source.value || saving.value) return
  saving.value = true
  try {
    await (props.saveSettings ?? store.saveSettings)({
      ...source.value,
      database_update: { enabled: enabled.value, interval_seconds: interval.value },
    })
  } catch {
    /* Store or parent operation exposes the actionable error. */
  } finally {
    saving.value = false
  }
}
</script>
<template>
  <section class="page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">Settings</p>
        <h1>Database updates</h1>
        <p>Control automatic ICVDB snapshot checks.</p>
      </div>
    </div>
    <article class="card form-card">
      <ToggleSwitch
        v-model="enabled"
        label="Automatic snapshot updates"
        description="Periodically check for and safely apply a newer database snapshot."
      /><label
        >Check interval (hours)<input
          v-model.number="hours"
          type="number"
          min="0.0167"
          max="168"
          step="1"
          inputmode="decimal"
      /></label>
      <p class="field-help">Accepted range: 1 minute to 7 days.</p>
      <p v-if="localError || store.state.error" class="inline-error" role="alert">
        {{ localError || store.state.error }}
      </p>
      <p v-if="store.state.feedback" class="success-message" role="status">
        {{ store.state.feedback }}
      </p>
      <button class="button" type="button" :disabled="saving || store.state.saving" @click="save">
        {{ saving || store.state.saving ? 'Saving…' : 'Save update settings' }}
      </button>
    </article>
  </section>
</template>
