import { fireEvent, render, screen } from '@testing-library/vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DatabaseUpdatesView from '../views/DatabaseUpdatesView.vue'
import { useLocale } from '../i18n'
import { settingsFixture } from './fixtures'

describe('database updates', () => {
  beforeEach(() => useLocale().setLocale('en'))
  it('validates the interval and persists enabled state with seconds', async () => {
    const saveSettings = vi.fn().mockResolvedValue(undefined)
    render(DatabaseUpdatesView, { props: { settings: settingsFixture, saveSettings } })
    await fireEvent.update(screen.getByLabelText('Check interval (hours)'), '0')
    await fireEvent.click(screen.getByRole('button', { name: 'Save update settings' }))
    expect(screen.getByRole('alert')).toBeTruthy()
    expect(saveSettings).not.toHaveBeenCalled()

    await fireEvent.click(screen.getByRole('switch'))
    await fireEvent.update(screen.getByLabelText('Check interval (hours)'), '12')
    await fireEvent.click(screen.getByRole('button', { name: 'Save update settings' }))
    expect(saveSettings.mock.calls[0][0].database_update).toEqual({
      enabled: false,
      interval_seconds: 43200,
    })
  })
})
