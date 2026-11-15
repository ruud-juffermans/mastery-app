import { useState } from 'react'

import { postPing } from './api'
import { useJob } from './hooks/useJob'

function App() {
  const [jobId, setJobId] = useState<number | null>(null)
  const [starting, setStarting] = useState(false)
  const [startError, setStartError] = useState<string | null>(null)
  const { job, error } = useJob(jobId)

  const finished = job?.status === 'ok' || job?.status === 'error' || error !== null
  const thinking = starting || (jobId !== null && !finished)

  async function ping() {
    setStarting(true)
    setStartError(null)
    setJobId(null)
    try {
      const created = await postPing()
      setJobId(created.id)
    } catch (e) {
      setStartError(e instanceof Error ? e.message : String(e))
    } finally {
      setStarting(false)
    }
  }

  return (
    <main>
      <h1>Mastery</h1>
      <button onClick={ping} disabled={thinking}>
        Ping
      </button>

      {thinking && <p>Thinking...</p>}
      {job?.status === 'ok' && <p>{String(job.output?.message ?? '')}</p>}
      {job?.status === 'error' && <p role="alert">{job.error}</p>}
      {error && <p role="alert">{error.message}</p>}
      {startError && <p role="alert">{startError}</p>}
    </main>
  )
}

export default App
