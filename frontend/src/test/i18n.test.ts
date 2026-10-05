import { describe, expect, it } from 'vitest'
import { createLocaleController, LOCALE_STORAGE_KEY } from '../i18n'

describe('locale controller', () => {
  it('defaults invalid or missing preferences to Italian and persists English selection', () => {
    localStorage.clear()
    const locale = createLocaleController(localStorage, document)

    expect(locale.current.value).toBe('it')
    expect(locale.t('navigation.dashboard')).toBe('Panoramica')
    expect(document.documentElement.lang).toBe('it')

    locale.setLocale('en')
    expect(locale.t('navigation.dashboard')).toBe('Dashboard')
    expect(localStorage.getItem(LOCALE_STORAGE_KEY)).toBe('en')
    expect(document.title).toBe('Violarr')

    localStorage.setItem(LOCALE_STORAGE_KEY, 'invalid')
    expect(createLocaleController(localStorage, document).current.value).toBe('it')
  })
})
