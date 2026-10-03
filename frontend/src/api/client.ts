import type { AppStatus, IndexerResult, ProwlarrStatus, PublicSettings, ResultProcessing } from './types'

export class ApiError extends Error {
  constructor(message: string, readonly status: number | null = null) {
    super(message)
    this.name = 'ApiError'
  }
}

export const REQUEST_TIMEOUT_MS = 10_000

export async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController()
  let timedOut = false
  const forwardAbort = () => controller.abort(init?.signal?.reason)
  if (init?.signal?.aborted) forwardAbort()
  else init?.signal?.addEventListener('abort', forwardAbort, { once: true })
  const timeout = setTimeout(() => { timedOut = true; controller.abort() }, REQUEST_TIMEOUT_MS)
  let response: Response
  try {
    response = await fetch(path, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
      signal: controller.signal,
    })
  } catch (error) {
    if (timedOut) throw new ApiError('The request timed out. Please try again.')
    if (init?.signal?.aborted || (error instanceof DOMException && error.name === 'AbortError')) {
      throw new ApiError('The request was canceled.')
    }
    throw new ApiError('The service could not be reached. Check that it is running and try again.')
  } finally {
    clearTimeout(timeout)
    init?.signal?.removeEventListener('abort', forwardAbort)
  }
  if (!response.ok) {
    let detail: unknown
    try {
      const body = await response.json() as { detail?: unknown }
      detail = body.detail
    } catch {
      detail = null
    }
    const message = typeof detail === 'string' && detail.trim()
      ? detail
      : `Request failed (${response.status}). Please try again.`
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

const json = (body: unknown): RequestInit => ({ method: 'PUT', body: JSON.stringify(body) })

export const api = {
  status: () => requestJson<AppStatus>('/webapi/status'),
  settings: () => requestJson<PublicSettings>('/webapi/settings'),
  saveSettings: (settings: PublicSettings) => requestJson<PublicSettings>('/webapi/settings', json(settings)),
  resultProcessing: () => requestJson<ResultProcessing>('/webapi/result-processing'),
  saveResultProcessing: (value: ResultProcessing) => requestJson<ResultProcessing>('/webapi/result-processing', json(value)),
  prowlarrStatus: () => requestJson<ProwlarrStatus>('/webapi/prowlarr/status'),
  testProwlarr: () => requestJson<{ connected: true; error: null }>('/webapi/prowlarr/test', { method: 'POST' }),
  installIndexer: () => requestJson<IndexerResult>('/webapi/prowlarr/indexer', { method: 'POST' }),
}
