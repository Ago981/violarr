import { describe, expect, it, vi } from 'vitest'
import { createThemeController } from '../composables/theme'

describe('theme controller', () => {
  it('uses the system default and persists explicit light and dark choices', () => {
    localStorage.clear()
    const media = {
      matches: true,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
    } as unknown as MediaQueryList
    const theme = createThemeController(() => media)

    expect(theme.preference.value).toBe('system')
    expect(theme.resolved.value).toBe('dark')
    theme.setPreference('light')
    expect(document.documentElement.dataset.theme).toBe('light')
    expect(localStorage.getItem('icvdb-theme')).toBe('light')
    theme.toggle()
    expect(theme.preference.value).toBe('dark')
  })

  it('restores System, reacts to system changes, and disposes its listener', () => {
    localStorage.setItem('icvdb-theme', 'light')
    let change: ((event: MediaQueryListEvent) => void) | undefined
    const remove = vi.fn()
    const media = {
      matches: false,
      addEventListener: vi.fn((_name, listener) => {
        change = listener
      }),
      removeEventListener: remove,
    } as unknown as MediaQueryList
    const controller = createThemeController(() => media)

    controller.setPreference('system')
    expect(localStorage.getItem('icvdb-theme')).toBeNull()
    change?.({ matches: true } as MediaQueryListEvent)
    expect(controller.resolved.value).toBe('dark')
    controller.dispose()
    expect(remove).toHaveBeenCalledWith('change', change)
  })

  it('is safe when browser globals are unavailable', () => {
    expect(() => createThemeController(() => null, null, null)).not.toThrow()
  })
})
