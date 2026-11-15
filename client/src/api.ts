// The only file that knows the API's URLs. Requests go to `/api` on the page's own origin;
// Vite forwards them to the API (see `server.proxy` in vite.config.ts).

export type JobStatus = 'queued' | 'running' | 'ok' | 'error'

export type Job = {
  id: number
  agent: string
  status: JobStatus
  output: Record<string, unknown> | null
  error: string | null
  provider: string | null
  model: string | null
}

async function request(path: string, init?: RequestInit): Promise<Job> {
  const response = await fetch(path, init)
  if (!response.ok) {
    throw new Error(`${init?.method ?? 'GET'} ${path} failed with ${response.status}`)
  }
  return (await response.json()) as Job
}

export function postPing(): Promise<Job> {
  return request('/api/jobs/ping', { method: 'POST' })
}

export function getJob(id: number): Promise<Job> {
  return request(`/api/jobs/${id}`)
}
