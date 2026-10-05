import { describe, expect, it, vi } from 'vitest'
import { createAppStore } from '../composables/appStore'
import { settingsFixture, statusFixture } from './fixtures'

describe('application store orchestration', () => {
  it('deduplicates concurrent mount loads and requests live Prowlarr status once', async () => {
    const client = {
      status: vi.fn().mockResolvedValue(statusFixture),
      settings: vi.fn().mockResolvedValue(settingsFixture),
      prowlarrStatus: vi.fn().mockResolvedValue(statusFixture.prowlarr),
      saveSettings: vi.fn(),
      saveResultProcessing: vi.fn(),
      testProwlarr: vi.fn(),
      installIndexer: vi.fn(),
    }
    const store = createAppStore(client)

    await Promise.all([store.loadAll(), store.loadAll()])

    expect(client.status).toHaveBeenCalledOnce()
    expect(client.settings).toHaveBeenCalledOnce()
    expect(client.prowlarrStatus).toHaveBeenCalledOnce()
  })
})
