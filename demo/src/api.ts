const API_BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  return res.json()
}

export const api = {
  destinations: {
    list: () => request<{ destinations: import('./types').Destination[]; total: number }>('/destinations'),
    sync: () => request<import('./types').SyncResponse>('/destinations/sync', { method: 'POST' }),
    near: (body: import('./types').NearSearchRequest) =>
      request<{ destinations: import('./types').Destination[]; total: number }>('/destinations/near', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
  },
  planner: {
    generatePlan: (body: import('./types').GeneratePlanRequest) =>
      request<import('./types').GeneratePlanResponse>('/planner/generate-plan', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
  },
  jobs: {
    sync: () => request<{ job_id: string }>('/jobs/sync', { method: 'POST' }),
    getStatus: (id: string) => request<import('./types').JobStatus>(`/jobs/${id}`),
  },
}
