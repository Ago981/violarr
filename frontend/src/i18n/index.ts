import { computed, ref } from 'vue'
import { englishMessages, italianMessages, type MessageKey } from './messages'

export type Locale = 'it' | 'en'
export const LOCALE_STORAGE_KEY = 'violarr-locale'

const catalogs = { it: italianMessages, en: englishMessages }
const knownServerMessages: Record<string, MessageKey> = {
  'Prowlarr is not configured': 'error.prowlarrNotConfigured',
  'Prowlarr is unavailable': 'error.prowlarrUnavailable',
  'Unable to connect to Prowlarr': 'error.prowlarrUnreachable',
  'Prowlarr returned invalid JSON': 'error.prowlarrInvalidJson',
}

export function createLocaleController(
  storage: Storage | null = typeof localStorage === 'undefined' ? null : localStorage,
  page: Document | null = typeof document === 'undefined' ? null : document,
) {
  const stored = storage?.getItem(LOCALE_STORAGE_KEY)
  const current = ref<Locale>(stored === 'en' ? 'en' : 'it')
  const messages = computed(() => catalogs[current.value])

  function t(key: MessageKey, values: Record<string, string | number> = {}) {
    return Object.entries(values).reduce(
      (message, [name, value]) => message.replaceAll(`{${name}}`, String(value)),
      messages.value[key] as string,
    )
  }

  function applyMetadata() {
    if (!page) return
    page.documentElement.lang = current.value
    page.title = t('app.title')
    page.querySelector('meta[name="description"]')?.setAttribute('content', t('app.subtitle'))
  }

  function setLocale(locale: Locale) {
    current.value = locale
    storage?.setItem(LOCALE_STORAGE_KEY, locale)
    applyMetadata()
  }

  function localizeServerMessage(message: string, fallback: string) {
    const key = knownServerMessages[message]
    if (key) return t(key)
    return current.value === 'en' ? message : fallback
  }

  applyMetadata()
  return { current, t, setLocale, localizeServerMessage }
}

const locale = createLocaleController()
export function useLocale() {
  return locale
}
