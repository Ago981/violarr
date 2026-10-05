<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import type { IndexerResult, ProwlarrStatus, PublicSettings } from '../api/types'
import { apiErrorMessage } from '../api/client'
import { useAppStore } from '../composables/appStore'
import StatusBadge from '../components/StatusBadge.vue'
import { useLocale } from '../i18n'

const props = defineProps<{
  settings?: PublicSettings
  status?: ProwlarrStatus | null
  saveSettings?: (settings: PublicSettings) => Promise<unknown>
  testConnection?: () => Promise<void>
  installIndexer?: () => Promise<IndexerResult>
}>()
const store = useAppStore()
const { t, localizeServerMessage } = useLocale()
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
const displayedError = computed(() => {
  if (failure.value) return failure.value
  if (liveStatus.value?.error)
    return localizeServerMessage(liveStatus.value.error, t('prowlarr.connectionFailed'))
  return store.state.error
})

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
  if (form.url && !validHttpUrl(form.url)) return t('prowlarr.invalidUrl')
  if (form.indexerUrl && !validHttpUrl(form.indexerUrl)) return t('prowlarr.invalidIndexerUrl')
  if (kind !== 'save' && !form.url) return t('prowlarr.urlRequired')
  if (kind !== 'save' && (clearKey.value || (!keyConfigured.value && !form.apiKey)))
    return t('prowlarr.keyRequired')
  if (kind === 'install' && !form.indexerUrl) return t('prowlarr.indexerRequired')
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
  return apiErrorMessage(error, fallback)
}

async function persist(kind: 'save' | 'test' | 'install') {
  const validation = validate(kind)
  if (validation) throw new Error(validation)
  const value = payload()
  if (!value) throw new Error(t('prowlarr.settingsLoading'))
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
    success.value = t('prowlarr.settingsSaved')
  } catch (error) {
    failure.value = errorMessage(error, t('prowlarr.saveFailed'))
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
    success.value = t('prowlarr.connectionSuccessful')
  } catch (error) {
    failure.value = errorMessage(
      error,
      error instanceof Error ? error.message : t('prowlarr.connectionFailed'),
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
      ? t('prowlarr.alreadyInstalled')
      : t('prowlarr.installed')
  } catch (error) {
    failure.value = errorMessage(
      error,
      error instanceof Error ? error.message : t('prowlarr.installFailed'),
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
        <p class="eyebrow eyebrow--prowlarr">{{ t('common.integration') }}</p>
        <h1>Prowlarr</h1>
        <p>{{ t('prowlarr.intro') }}</p>
      </div>
      <StatusBadge
        v-if="liveStatus"
        :tone="liveStatus.connected ? 'success' : liveStatus.error ? 'danger' : 'neutral'"
        :label="
          liveStatus.connected
            ? t('common.connected')
            : liveStatus.configured
              ? t('common.notConnected')
              : t('common.notConfigured')
        "
      />
    </div>
    <article v-if="source" class="card form-card card--prowlarr">
      <label
        >{{ t('prowlarr.url')
        }}<input
          v-model.trim="form.url"
          type="url"
          placeholder="http://prowlarr:9696"
          :disabled="busy"
      /></label>
      <p class="field-help">
        {{ t('prowlarr.urlHelp') }}
      </p>
      <div class="key-panel">
        <div>
          <strong>{{ t('prowlarr.apiKey') }}</strong>
          <p>
            {{ keyConfigured && !clearKey ? t('prowlarr.keySaved') : t('prowlarr.noKeySaved') }}
          </p>
        </div>
        <button
          v-if="keyConfigured"
          class="text-button"
          type="button"
          :disabled="busy"
          @click="toggleKeyReplacement"
        >
          {{ replaceKey ? t('prowlarr.cancelReplacement') : t('prowlarr.replaceKey') }}
        </button>
      </div>
      <label v-if="showKeyInput"
        >{{ keyConfigured ? t('prowlarr.newApiKey') : t('prowlarr.apiKey')
        }}<input v-model="form.apiKey" type="password" autocomplete="new-password" :disabled="busy"
      /></label>
      <label v-if="keyConfigured" class="check-row"
        ><input
          v-model="clearKey"
          type="checkbox"
          :aria-label="t('prowlarr.clearKeyLabel')"
          :disabled="busy"
        />
        {{ t('prowlarr.clearKey') }}</label
      >
      <label
        >{{ t('prowlarr.indexerUrl')
        }}<input
          v-model.trim="form.indexerUrl"
          type="url"
          placeholder="http://icvdb-torznab:8000/api"
          :disabled="busy"
      /></label>
      <p class="field-help">
        {{ t('prowlarr.indexerHelp') }}
      </p>
      <div class="button-row">
        <button class="button button--prowlarr" type="button" :disabled="busy" @click="save">
          {{ operation === 'save' ? t('common.saving') : t('prowlarr.save') }}
        </button>
        <button class="button button--secondary" type="button" :disabled="busy" @click="test">
          {{ operation === 'test' ? t('prowlarr.testing') : t('prowlarr.test') }}
        </button>
        <button class="button button--prowlarr" type="button" :disabled="busy" @click="install">
          {{ operation === 'install' ? t('prowlarr.adding') : t('prowlarr.add') }}
        </button>
      </div>
      <p v-if="success" role="status" class="success-message">{{ success }}</p>
      <p v-if="displayedError" role="alert" class="inline-error">
        {{ displayedError }}
      </p>
    </article>
  </section>
</template>
