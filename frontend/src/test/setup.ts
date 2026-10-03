import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/vue'

if (typeof localStorage?.getItem !== 'function') {
  const values = new Map<string, string>()
  Object.defineProperty(globalThis, 'localStorage', { value: {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
    removeItem: (key: string) => values.delete(key),
    clear: () => values.clear(),
  } })
}
if (typeof window.matchMedia !== 'function') {
  Object.defineProperty(window, 'matchMedia', { value: () => ({
    matches: false,
    media: '',
    onchange: null,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    addListener: () => undefined,
    removeListener: () => undefined,
    dispatchEvent: () => false,
  }) })
}

afterEach(() => cleanup())
