import { reactive } from 'vue'
import { api, ApiError } from '../api/client'
import type {
  AppStatus,
  IndexerResult,
  ProwlarrStatus,
  PublicSettings,
  ResultProcessing,
} from '../api/types'

type ApiClient = Pick<
  typeof api,
  | 'status'
  | 'settings'
  | 'saveSettings'
  | 'saveResultProcessing'
  | 'prowlarrStatus'
  | 'testProwlarr'
  | 'installIndexer'
>

function message(error: unknown) {
  return error instanceof ApiError
    ? error.message
    : 'An unexpected error occurred. Please try again.'
}

export function createAppStore(client: ApiClient = api) {
  const state = reactive({
    status: null as AppStatus | null,
    settings: null as PublicSettings | null,
    prowlarrStatus: null as ProwlarrStatus | null,
    loading: false,
    saving: false,
    error: null as string | null,
    feedback: null as string | null,
  })
  let loadPromise: Promise<void> | null = null

  async function loadAll(force = false) {
    if (loadPromise) return loadPromise
    if (!force && state.status && state.settings) return
    state.loading = true
    state.error = null
    loadPromise = Promise.all([
      client.status(),
      client.settings(),
      client.prowlarrStatus().catch(() => null),
    ])
      .then(([status, settings, prowlarr]) => {
        state.status = prowlarr ? { ...status, prowlarr } : status
        state.prowlarrStatus = prowlarr
        state.settings = settings
      })
      .catch((error) => {
        state.error = message(error)
      })
      .finally(() => {
        state.loading = false
        loadPromise = null
      })
    return loadPromise
  }

  async function saveSettings(settings: PublicSettings) {
    state.saving = true
    state.error = null
    state.feedback = null
    try {
      state.settings = await client.saveSettings(settings)
      state.feedback = 'Settings saved.'
      state.status = await client.status()
      return state.settings
    } catch (error) {
      state.error = message(error)
      throw error
    } finally {
      state.saving = false
    }
  }

  async function saveResultProcessing(value: ResultProcessing) {
    state.saving = true
    state.error = null
    state.feedback = null
    try {
      const saved = await client.saveResultProcessing(value)
      if (state.settings) state.settings.result_processing = saved
      state.feedback = 'Result processing saved.'
      state.status = await client.status()
    } catch (error) {
      state.error = message(error)
      throw error
    } finally {
      state.saving = false
    }
  }

  async function refreshProwlarr() {
    try {
      state.prowlarrStatus = await client.prowlarrStatus()
      if (state.status) state.status.prowlarr = state.prowlarrStatus
    } catch (error) {
      state.error = message(error)
      throw error
    }
  }
  async function testProwlarr() {
    await client.testProwlarr()
    await refreshProwlarr()
  }
  async function installIndexer(): Promise<IndexerResult> {
    const result = await client.installIndexer()
    await refreshProwlarr()
    return result
  }
  return {
    state,
    loadAll,
    saveSettings,
    saveResultProcessing,
    refreshProwlarr,
    testProwlarr,
    installIndexer,
  }
}

const appStore = createAppStore()
export function useAppStore() {
  return appStore
}
