import { describe, expect, it } from 'vitest'
import { createNavigationController } from '../composables/navigation'

describe('responsive navigation', () => {
  it('opens, closes, and closes after route navigation', () => {
    const navigation = createNavigationController()
    expect(navigation.mobileOpen.value).toBe(false)
    navigation.toggle()
    expect(navigation.mobileOpen.value).toBe(true)
    navigation.onRouteChange()
    expect(navigation.mobileOpen.value).toBe(false)
  })
})
