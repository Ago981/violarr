import { fireEvent, render, screen } from '@testing-library/vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DashboardView from '../views/DashboardView.vue'
import { useLocale } from '../i18n'
import { statusFixture } from './fixtures'

describe('dashboard', () => {
  beforeEach(() => useLocale().setLocale('en'))
  it('renders live service, snapshot, processing, and Prowlarr states', () => {
    render(DashboardView, {
      props: { status: statusFixture, loading: false, error: null },
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    expect(screen.getByText('PostgreSQL connected')).toBeTruthy()
    expect(screen.getByText('db-2026-08-21')).toBeTruthy()
    expect(screen.getByText('Italian preferred')).toBeTruthy()
    expect(screen.getByText('Connected; indexer not installed')).toBeTruthy()
  })

  it('shows loading and actionable failure states', async () => {
    const { rerender } = render(DashboardView, {
      props: { status: null, loading: true, error: null },
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    expect(screen.getByText('Loading system status…')).toBeTruthy()
    await rerender({ status: null, loading: false, error: 'The service could not be reached.' })
    expect(screen.getByRole('alert').textContent).toContain('The service could not be reached.')
  })

  it('provides a disabled manual refresh while refreshing', async () => {
    let finish!: () => void
    const refresh = vi.fn(
      () =>
        new Promise<void>((resolve) => {
          finish = resolve
        }),
    )
    render(DashboardView, {
      props: { status: statusFixture, loading: false, error: null, onRefresh: refresh },
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })

    const button = screen.getByRole('button', { name: 'Refresh status' }) as HTMLButtonElement
    await fireEvent.click(button)
    expect(refresh).toHaveBeenCalledOnce()
    expect(button.disabled).toBe(true)
    expect(button.textContent).toContain('Refreshing')
    finish()
  })
})
