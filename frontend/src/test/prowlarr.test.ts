import { fireEvent, render, screen, waitFor } from '@testing-library/vue'
import { describe, expect, it, vi } from 'vitest'
import ProwlarrView from '../views/ProwlarrView.vue'
import type { PublicSettings } from '../api/types'
import { settingsFixture } from './fixtures'

describe('Prowlarr settings', () => {
  it('shows fresh key entry and saves current values before test and install', async () => {
    const fresh = {
      ...settingsFixture,
      prowlarr: { url: '', indexer_url: '', api_key_configured: false },
    }
    const calls: string[] = []
    const saveSettings = vi.fn(async (_settings: PublicSettings) => {
      calls.push('save')
    })
    const testConnection = vi.fn(async () => {
      calls.push('test')
    })
    const installIndexer = vi.fn(async () => {
      calls.push('install')
      return { created: true, already_installed: false, indexer_id: 7 }
    })
    render(ProwlarrView, {
      props: { settings: fresh, status: null, saveSettings, testConnection, installIndexer },
    })

    await fireEvent.update(screen.getByLabelText('Prowlarr URL'), 'http://prowlarr:9696')
    await fireEvent.update(screen.getByLabelText('API key'), 'new-secret')
    await fireEvent.update(
      screen.getByLabelText('Indexer URL as seen by Prowlarr'),
      'http://bridge:8000/api',
    )
    await fireEvent.click(screen.getByRole('button', { name: 'Test connection' }))
    await waitFor(() => expect(calls).toEqual(['save', 'test']))
    expect(saveSettings.mock.calls[0][0].prowlarr.api_key).toBe('new-secret')

    await fireEvent.click(screen.getByRole('button', { name: 'Add ICVDB to Prowlarr' }))
    await waitFor(() => expect(calls).toEqual(['save', 'test', 'save', 'install']))
    expect(saveSettings.mock.calls[1][0].prowlarr).not.toHaveProperty('api_key')
  })

  it('masks saved keys, omits unchanged keys, and supports explicit clearing', async () => {
    const save = vi.fn().mockResolvedValue(undefined)
    render(ProwlarrView, { props: { settings: settingsFixture, status: null, saveSettings: save } })
    expect(screen.getByText('A key is saved')).toBeTruthy()
    await fireEvent.click(screen.getByRole('button', { name: 'Save Prowlarr settings' }))
    expect(save.mock.calls[0][0].prowlarr).not.toHaveProperty('api_key')

    await fireEvent.click(screen.getByRole('button', { name: 'Replace key' }))
    await fireEvent.update(screen.getByLabelText('New API key'), 'replacement')
    await fireEvent.click(screen.getByRole('button', { name: 'Save Prowlarr settings' }))
    expect(save.mock.calls[1][0].prowlarr.api_key).toBe('replacement')

    await fireEvent.click(screen.getByLabelText('Clear saved API key'))
    await fireEvent.click(screen.getByRole('button', { name: 'Save Prowlarr settings' }))
    expect(save.mock.calls[2][0].prowlarr.api_key).toBe('')
  })

  it('reports connection and both indexer installation outcomes', async () => {
    const testConnection = vi.fn().mockResolvedValue(undefined)
    const install = vi
      .fn()
      .mockResolvedValueOnce({ created: false, already_installed: true, indexer_id: null })
      .mockResolvedValueOnce({ created: true, already_installed: false, indexer_id: 7 })
    render(ProwlarrView, {
      props: {
        settings: settingsFixture,
        status: { configured: true, connected: true, indexer_installed: false, error: null },
        saveSettings: vi.fn().mockResolvedValue(undefined),
        testConnection,
        installIndexer: install,
      },
    })
    await fireEvent.click(screen.getByRole('button', { name: 'Test connection' }))
    expect(await screen.findByText('Connection successful.')).toBeTruthy()
    await fireEvent.click(screen.getByRole('button', { name: 'Add ICVDB to Prowlarr' }))
    expect(await screen.findByText('ICVDB is already installed.')).toBeTruthy()
    await fireEvent.click(screen.getByRole('button', { name: 'Add ICVDB to Prowlarr' }))
    expect(await screen.findByText('ICVDB was added to Prowlarr.')).toBeTruthy()
  })

  it('retains form state after save failure and prevents duplicate operations', async () => {
    let reject!: (error: Error) => void
    const saveSettings = vi.fn(
      () =>
        new Promise<void>((_resolve, fail) => {
          reject = fail
        }),
    )
    render(ProwlarrView, { props: { settings: settingsFixture, status: null, saveSettings } })
    await fireEvent.click(screen.getByRole('button', { name: 'Replace key' }))
    await fireEvent.update(screen.getByLabelText('New API key'), 'retry-secret')

    const save = screen.getByRole('button', { name: 'Save Prowlarr settings' }) as HTMLButtonElement
    await fireEvent.click(save)
    await fireEvent.click(save)
    expect(saveSettings).toHaveBeenCalledOnce()
    expect(screen.getByRole('button', { name: 'Test connection' })).toHaveProperty('disabled', true)
    reject(new Error('rejected'))

    const alert = await screen.findByRole('alert')
    expect(alert.classList.contains('inline-error')).toBe(true)
    expect((screen.getByLabelText('New API key') as HTMLInputElement).value).toBe('retry-secret')
  })
})
