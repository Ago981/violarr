<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import type { IndexerResult, ProwlarrStatus, PublicSettings } from '../api/types'
import { ApiError } from '../api/client'
import { useAppStore } from '../composables/appStore'
import StatusBadge from '../components/StatusBadge.vue'

const props = defineProps<{
  settings?: PublicSettings
  status?: ProwlarrStatus | null
  saveSettings?: (settings: PublicSettings) => Promise<unknown>
  testConnection?: () => Promise<void>
  installIndexer?: () => Promise<IndexerResult>
}>()
const store = useAppStore()
const form = reactive({ url: '', indexerUrl: '', apiKey: '' })
const replaceKey = ref(false)
const clearKey = ref(false)
const keyConfigured = ref(false)
const operation = ref<'save' | 'test' | 'install' | null>(null)
const success = ref('')
const failure = ref('')
const source = computed(() => props.settings ?? store.state.settings)
const liveStatus = computed(() =>
  props.status === undefined ? store.state.prowlarrStatus : props.status,
)
const busy = computed(() => operation.value !== null || store.state.saving)
const showKeyInput = computed(() => !keyConfigured.value || replaceKey.value)

watch(
  source,
  (settings) => {
    if (!settings) return
    form.url = settings.prowlarr.url
    form.indexerUrl = settings.prowlarr.indexer_url
    keyConfigured.value = settings.prowlarr.api_key_configured
  },
  { immediate: true },
)
onMounted(() => {
  if (!props.settings) store.loadAll()
})

function validHttpUrl(value: string) {
  try {
    return ['http:', 'https:'].includes(new URL(value).protocol)
  } catch {
    return false
  }
}

function toggleKeyReplacement() {
  replaceKey.value = !replaceKey.value
  clearKey.value = false
}

function validate(kind: 'save' | 'test' | 'install') {
  if (form.url && !validHttpUrl(form.url)) return 'Enter a valid absolute HTTP Prowlarr URL.'
  if (form.indexerUrl && !validHttpUrl(form.indexerUrl))
    return 'Enter a valid absolute HTTP Indexer URL.'
  if (kind !== 'save' && !form.url) return 'Enter the Prowlarr URL before continuing.'
  if (kind !== 'save' && (clearKey.value || (!keyConfigured.value && !form.apiKey)))
    return 'Enter an API key before continuing.'
  if (kind === 'install' && !form.indexerUrl) return 'Enter the Indexer URL before adding ICVDB.'
  return null
}

function payload(): PublicSettings | null {
  if (!source.value) return null
  const prowlarr: PublicSettings['prowlarr'] = {
    url: form.url,
    indexer_url: form.indexerUrl,
    api_key_configured: keyConfigured.value,
  }
  if (clearKey.value) prowlarr.api_key = ''
  else if (showKeyInput.value && form.apiKey) prowlarr.api_key = form.apiKey
  return { ...source.value, prowlarr }
}

function errorMessage(error: unknown, fallback: string) {
  return error instanceof ApiError ? error.message : fallback
}

async function persist(kind: 'save' | 'test' | 'install') {
  const validation = validate(kind)
  if (validation) throw new Error(validation)
  const value = payload()
  if (!value) throw new Error('Settings are still loading. Please try again.')
  await (props.saveSettings ?? store.saveSettings)(value)
  if (clearKey.value) keyConfigured.value = false
  else if (form.apiKey) keyConfigured.value = true
  form.apiKey = ''
  replaceKey.value = false
  clearKey.value = false
}

async function save() {
  if (busy.value) return
  operation.value = 'save'
  success.value = ''
  failure.value = ''
  try {
    await persist('save')
    success.value = 'Prowlarr settings saved.'
  } catch (error) {
    failure.value = errorMessage(
      error,
      'Settings could not be saved. Correct the form and try again.',
    )
  } finally {
    operation.value = null
  }
}

async function test() {
  if (busy.value) return
  operation.value = 'test'
  success.value = ''
  failure.value = ''
  try {
    await persist('test')
    await (props.testConnection ?? store.testProwlarr)()
    success.value = 'Connection successful.'
  } catch (error) {
    failure.value = errorMessage(
      error,
      error instanceof Error ? error.message : 'Connection failed. Check the URL and API key.',
    )
  } finally {
    operation.value = null
  }
}

async function install() {
  if (busy.value) return
  operation.value = 'install'
  success.value = ''
  failure.value = ''
  try {
    await persist('install')
    const result = await (props.installIndexer ?? store.installIndexer)()
    success.value = result.already_installed
      ? 'ICVDB is already installed.'
      : 'ICVDB was added to Prowlarr.'
  } catch (error) {
    failure.value = errorMessage(
      error,
      error instanceof Error
        ? error.message
        : 'Indexer installation failed. Check the connection and Indexer URL.',
    )
  } finally {
    operation.value = null
  }
}
</script>

<template>
  <section class="page page--prowlarr">
    <div class="page-heading">
      <div>
        <p class="eyebrow eyebrow--prowlarr">Integration</p>
        <h1>Prowlarr</h1>
        <p>Connect Prowlarr and install ICVDB as a Generic Torznab indexer.</p>
      </div>
      <StatusBadge
        v-if="liveStatus"
        :tone="liveStatus.connected ? 'success' : liveStatus.error ? 'danger' : 'neutral'"
        :label="
          liveStatus.connected
            ? 'Connected'
            : liveStatus.configured
              ? 'Not connected'
              : 'Not configured'
        "
      />
    </div>
    <article v-if="source" class="card form-card card--prowlarr">
      <label
        >Prowlarr URL<input
          v-model.trim="form.url"
          type="url"
          placeholder="http://prowlarr:9696"
          :disabled="busy"
      /></label>
      <p class="field-help">
        Use an address reachable from this container. <code>localhost</code> usually points back to
        the ICVDB container, not Prowlarr.
      </p>
      <div class="key-panel">
        <div>
          <strong>API key</strong>
          <p>{{ keyConfigured && !clearKey ? 'A key is saved' : 'No key is saved' }}</p>
        </div>
        <button
          v-if="keyConfigured"
          class="text-button"
          type="button"
          :disabled="busy"
          @click="toggleKeyReplacement"
        >
          {{ replaceKey ? 'Cancel replacement' : 'Replace key' }}
        </button>
      </div>
      <label v-if="showKeyInput"
        >{{ keyConfigured ? 'New API key' : 'API key'
        }}<input v-model="form.apiKey" type="password" autocomplete="new-password" :disabled="busy"
      /></label>
      <label v-if="keyConfigured" class="check-row"
        ><input
          v-model="clearKey"
          type="checkbox"
          aria-label="Clear saved API key"
          :disabled="busy"
        />
        Clear the saved API key on Save</label
      >
      <label
        >Indexer URL as seen by Prowlarr<input
          v-model.trim="form.indexerUrl"
          type="url"
          placeholder="http://icvdb-torznab:8000/api"
          :disabled="busy"
      /></label>
      <p class="field-help">
        This must be reachable from the Prowlarr container and end at the Torznab
        <code>/api</code> endpoint.
      </p>
      <div class="button-row">
        <button class="button button--prowlarr" type="button" :disabled="busy" @click="save">
          {{ operation === 'save' ? 'Saving…' : 'Save Prowlarr settings' }}
        </button>
        <button class="button button--secondary" type="button" :disabled="busy" @click="test">
          {{ operation === 'test' ? 'Testing…' : 'Test connection' }}
        </button>
        <button class="button button--prowlarr" type="button" :disabled="busy" @click="install">
          {{ operation === 'install' ? 'Adding…' : 'Add ICVDB to Prowlarr' }}
        </button>
      </div>
      <p v-if="success" role="status" class="success-message">{{ success }}</p>
      <p v-if="failure || liveStatus?.error || store.state.error" role="alert" class="inline-error">
        {{ failure || liveStatus?.error || store.state.error }}
      </p>
    </article>
  </section>
</template>
