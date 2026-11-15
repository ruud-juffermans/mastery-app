import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'

import { getJob, type Job, type JobStatus } from '../api'
import { useJob } from './useJob'

vi.mock('../api')

const mockedGetJob = vi.mocked(getJob)

function job(status: JobStatus): Job {
  return {
    id: 1,
    agent: 'ping',
    status,
    output: status === 'ok' ? { message: 'pong' } : null,
    error: status === 'error' ? 'boom' : null,
    provider: null,
    model: null,
  }
}

/** Lets the pending fetch resolve and its state update land, without moving the clock. */
async function settle() {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(0)
  })
}

async function tick(ms = 1500) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms)
  })
}

beforeEach(() => {
  vi.useFakeTimers()
  mockedGetJob.mockReset()
})

afterEach(() => {
  vi.useRealTimers()
})

test('polls until the job is ok, then stops', async () => {
  mockedGetJob
    .mockResolvedValueOnce(job('queued'))
    .mockResolvedValueOnce(job('running'))
    .mockResolvedValueOnce(job('ok'))

  const { result } = renderHook(() => useJob(1))

  await settle()
  expect(result.current.job?.status).toBe('queued')

  await tick()
  expect(result.current.job?.status).toBe('running')

  await tick()
  expect(result.current.job?.status).toBe('ok')

  await tick()
  await tick()
  expect(mockedGetJob).toHaveBeenCalledTimes(3)
})

test('a job that ends in error also stops the polling', async () => {
  mockedGetJob.mockResolvedValueOnce(job('queued')).mockResolvedValueOnce(job('error'))

  const { result } = renderHook(() => useJob(1))

  await settle()
  await tick()
  expect(result.current.job?.status).toBe('error')
  expect(result.current.job?.error).toBe('boom')

  await tick()
  expect(mockedGetJob).toHaveBeenCalledTimes(2)
})

test('unmounting while the job is queued stops the polling', async () => {
  mockedGetJob.mockResolvedValue(job('queued'))

  const { result, unmount } = renderHook(() => useJob(1))

  await settle()
  expect(result.current.job?.status).toBe('queued')
  expect(mockedGetJob).toHaveBeenCalledTimes(1)

  unmount()
  await tick()
  await tick()
  expect(mockedGetJob).toHaveBeenCalledTimes(1)
})

test('a failed request is reported and stops the polling', async () => {
  mockedGetJob.mockRejectedValueOnce(new Error('GET /api/jobs/1 failed with 500'))

  const { result } = renderHook(() => useJob(1))

  await settle()
  expect(result.current.job).toBeNull()
  expect(result.current.error?.message).toContain('500')

  await tick()
  expect(mockedGetJob).toHaveBeenCalledTimes(1)
})

test('does nothing without an id', async () => {
  const { result } = renderHook(() => useJob(null))

  await tick()
  expect(result.current).toEqual({ job: null, error: null })
  expect(mockedGetJob).not.toHaveBeenCalled()
})
