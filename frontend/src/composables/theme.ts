import { computed, ref } from 'vue'

export type ThemePreference = 'system' | 'light' | 'dark'
const storageKey = 'icvdb-theme'

export function createThemeController(
  mediaFactory: () => MediaQueryList | null = () =>
    typeof window === 'undefined' || !window.matchMedia
      ? null
      : window.matchMedia('(prefers-color-scheme: dark)'),
  storage: Storage | null = typeof localStorage === 'undefined' ? null : localStorage,
  root: HTMLElement | null = typeof document === 'undefined' ? null : document.documentElement,
) {
  const stored = storage?.getItem(storageKey)
  const preference = ref<ThemePreference>(
    stored === 'light' || stored === 'dark' ? stored : 'system',
  )
  const media = mediaFactory()
  const systemDark = ref(media?.matches ?? false)
  const resolved = computed(() =>
    preference.value === 'system' ? (systemDark.value ? 'dark' : 'light') : preference.value,
  )

  function apply() {
    if (root) root.dataset.theme = resolved.value
  }
  function setPreference(value: ThemePreference) {
    preference.value = value
    if (value === 'system') storage?.removeItem(storageKey)
    else storage?.setItem(storageKey, value)
    apply()
  }
  function toggle() {
    setPreference(
      preference.value === 'system' ? 'light' : preference.value === 'light' ? 'dark' : 'system',
    )
  }
  const onSystemChange = (event: MediaQueryListEvent) => {
    systemDark.value = event.matches
    if (preference.value === 'system') apply()
  }
  media?.addEventListener?.('change', onSystemChange)
  function dispose() {
    media?.removeEventListener?.('change', onSystemChange)
  }
  apply()
  return { preference, resolved, setPreference, toggle, dispose }
}
