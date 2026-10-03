import { fireEvent, render, screen, waitFor } from '@testing-library/vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { describe, expect, it, vi } from 'vitest'
import AppShell from '../components/AppShell.vue'

describe('mobile application shell', () => {
  it('traps focus, closes on Escape, returns focus, and focuses content after navigation', async () => {
    vi.stubGlobal(
      'matchMedia',
      vi.fn(() => ({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() })),
    )
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<p>Home</p>' } },
        { path: '/settings', component: { template: '<p>Settings</p>' } },
        { path: '/database', component: { template: '<p>Database</p>' } },
        { path: '/result-processing', component: { template: '<p>Results</p>' } },
        { path: '/prowlarr', component: { template: '<p>Prowlarr</p>' } },
        { path: '/advanced', component: { template: '<p>Advanced</p>' } },
      ],
    })
    await router.push('/')
    await router.isReady()
    render(AppShell, { global: { plugins: [router] } })
    const menu = screen.getByRole('button', { name: 'Open navigation' })
    await fireEvent.click(menu)
    const links = screen.getByRole('navigation').querySelectorAll('a')
    expect(document.activeElement).toBe(links[0])
    menu.focus()
    await fireEvent.keyDown(document, { key: 'Tab' })
    expect(document.activeElement).toBe(links[0])
    links[links.length - 1].focus()
    await fireEvent.keyDown(document, { key: 'Tab' })
    expect(document.activeElement).toBe(links[0])
    await fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
    expect(document.activeElement).toBe(links[links.length - 1])
    await fireEvent.keyDown(document, { key: 'Escape' })
    expect(document.activeElement).toBe(menu)

    await fireEvent.click(menu)
    await fireEvent.click(screen.getByRole('link', { name: 'General' }))
    await router.isReady()
    await waitFor(() => expect(document.activeElement).toBe(screen.getByRole('main')))
  })
})
