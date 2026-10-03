import { ref } from 'vue'

export function createNavigationController() {
  const mobileOpen = ref(false)
  const toggle = () => {
    mobileOpen.value = !mobileOpen.value
  }
  const close = () => {
    mobileOpen.value = false
  }
  const onRouteChange = close
  return { mobileOpen, toggle, close, onRouteChange }
}

export const navigation = createNavigationController()
