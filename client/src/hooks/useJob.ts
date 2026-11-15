import { useEffect, useState } from 'react'

import { getJob, type Job } from '../api'

type JobState = {
  /** The id this state belongs to, so a result for a previous id is never shown for the next one. */
  id: number | null
  job: Job | null
  error: Error | null
}

const EMPTY: JobState = { id: null, job: null, error: null }

/** Polls a job until it ends as `ok` or `error`. With `id` null it does nothing. */
export function useJob(id: number | null, intervalMs = 1500) {
  const [state, setState] = useState<JobState>(EMPTY)

  useEffect(() => {
    if (id === null) return

    let cancelled = false
    let timer: ReturnType<typeof setTimeout> | undefined

    async function poll(jobId: number) {
      try {
        const job = await getJob(jobId)
        if (cancelled) return
        setState({ id: jobId, job, error: null })
        // The next request is scheduled only after this one answered, so slow responses cannot pile up.
        if (job.status !== 'ok' && job.status !== 'error') {
          timer = setTimeout(() => void poll(jobId), intervalMs)
        }
      } catch (e) {
        if (cancelled) return
        setState({ id: jobId, job: null, error: e instanceof Error ? e : new Error(String(e)) })
      }
    }

    void poll(id)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [id, intervalMs])

  const current = state.id === id ? state : EMPTY
  return { job: current.job, error: current.error }
}
