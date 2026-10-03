import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, REQUEST_TIMEOUT_MS, requestJson } from '../api/client'

afterEach(() => vi.useRealTimers())

describe('API client', () => {
  it('normalizes JSON and non-JSON failures without exposing response internals', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail: 'Interval must be at least 60 seconds' }),
      { status: 422, headers: { 'Content-Type': 'application/json' } },
    )))

    await expect(requestJson('/webapi/settings')).rejects.toEqual(
      expect.objectContaining({ message: 'Interval must be at least 60 seconds', status: 422 }),
    )

    vi.mocked(fetch).mockResolvedValueOnce(new Response('proxy failure', { status: 502 }))
    await expect(requestJson('/webapi/status')).rejects.toEqual(
      new ApiError('Request failed (502). Please try again.', 502),
    )
  })

  it('aborts requests after the bounded timeout', async () => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn((_path, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
    })))

    const request = requestJson('/webapi/status')
    const rejection = expect(request).rejects.toEqual(new ApiError('The request timed out. Please try again.'))
    await vi.advanceTimersByTimeAsync(REQUEST_TIMEOUT_MS)

    await rejection
  })

  it('respects caller cancellation and removes the forwarding listener', async () => {
    const caller = new AbortController()
    const remove = vi.spyOn(caller.signal, 'removeEventListener')
    vi.stubGlobal('fetch', vi.fn((_path, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
    })))

    const request = requestJson('/webapi/status', { signal: caller.signal })
    caller.abort()

    await expect(request).rejects.toEqual(new ApiError('The request was canceled.'))
    expect(remove).toHaveBeenCalledWith('abort', expect.any(Function))
  })
})
