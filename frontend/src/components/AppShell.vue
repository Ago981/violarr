<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { navigation } from '../composables/navigation'
import { createThemeController } from '../composables/theme'

const route = useRoute()
const theme = createThemeController()
const menuButton = ref<HTMLButtonElement | null>(null)
const sidebar = ref<HTMLElement | null>(null)
const main = ref<HTMLElement | null>(null)
const desktop = ref(true)
let media: MediaQueryList | null = null
function syncLayout() {
  desktop.value = media?.matches ?? true
}
function openNavigation() {
  navigation.toggle()
  if (navigation.mobileOpen.value)
    nextTick(() => sidebar.value?.querySelector<HTMLAnchorElement>('a')?.focus())
}
function closeNavigation() {
  navigation.close()
  menuButton.value?.focus()
}
function focusableLinks() {
  return [...(sidebar.value?.querySelectorAll<HTMLAnchorElement>('a') ?? [])]
}
function onKeydown(event: KeyboardEvent) {
  if (!navigation.mobileOpen.value) return
  if (event.key === 'Escape') {
    event.preventDefault()
    closeNavigation()
    return
  }
  if (event.key !== 'Tab') return
  const links = focusableLinks()
  if (!links.length) return
  if (!sidebar.value?.contains(document.activeElement)) {
    event.preventDefault()
    ;(event.shiftKey ? links[links.length - 1] : links[0]).focus()
  } else if (!event.shiftKey && document.activeElement === links[links.length - 1]) {
    event.preventDefault()
    links[0].focus()
  } else if (event.shiftKey && document.activeElement === links[0]) {
    event.preventDefault()
    links[links.length - 1].focus()
  }
}
watch(
  () => route.fullPath,
  async () => {
    const wasOpen = navigation.mobileOpen.value
    navigation.onRouteChange()
    if (wasOpen) {
      await nextTick()
      main.value?.focus()
    }
  },
)
onMounted(() => {
  media = window.matchMedia('(min-width: 801px)')
  syncLayout()
  media.addEventListener('change', syncLayout)
  document.addEventListener('keydown', onKeydown)
})
onBeforeUnmount(() => {
  media?.removeEventListener('change', syncLayout)
  document.removeEventListener('keydown', onKeydown)
  theme.dispose()
})
const links = [
  ['/', 'Dashboard'],
  ['/settings', 'General'],
  ['/database', 'Database updates'],
  ['/result-processing', 'Result processing'],
  ['/prowlarr', 'Prowlarr'],
  ['/advanced', 'Advanced'],
]
</script>
<template>
  <div class="app-shell">
    <header class="topbar">
      <button
        ref="menuButton"
        class="icon-button menu-button"
        type="button"
        aria-label="Open navigation"
        :aria-expanded="navigation.mobileOpen.value"
        aria-controls="primary-navigation"
        @click="openNavigation"
      >
        ☰
      </button>
      <RouterLink class="brand" to="/" aria-label="ICVDB Torznab dashboard"
        ><span class="brand-mark">I</span><span>ICVDB Torznab</span></RouterLink
      >
      <label class="theme-select"
        ><span class="sr-only">Color theme</span
        ><select
          aria-label="Color theme"
          :value="theme.preference.value"
          @change="
            theme.setPreference(
              ($event.target as HTMLSelectElement).value as 'system' | 'light' | 'dark',
            )
          "
        >
          <option value="system">System</option>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select></label
      >
    </header>
    <div
      v-if="navigation.mobileOpen.value"
      class="scrim"
      aria-hidden="true"
      @click="closeNavigation"
    />
    <aside
      id="primary-navigation"
      ref="sidebar"
      class="sidebar"
      :class="{ 'sidebar--open': navigation.mobileOpen.value }"
      aria-label="Primary navigation"
      :aria-hidden="!desktop && !navigation.mobileOpen.value"
      :inert="!desktop && !navigation.mobileOpen.value"
    >
      <nav>
        <RouterLink v-for="[path, label] in links" :key="path" :to="path">{{ label }}</RouterLink>
      </nav>
      <p class="sidebar-note">Local, self-hosted indexer bridge</p>
    </aside>
    <main id="main-content" ref="main" class="main" tabindex="-1"><RouterView /></main>
  </div>
</template>
