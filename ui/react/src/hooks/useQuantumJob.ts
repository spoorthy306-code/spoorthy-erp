import { useState, useEffect, useCallback, useRef } from 'react';

export type JobStatus = 'PENDING' | 'RUNNING' | 'COMPLETE' | 'FAILED';

export interface QuantumJobResult {
  status: JobStatus;
  progress: number;        // 0–100
  result: Record<string, unknown> | null;
  error: string | null;
  jobId: string | null;
}

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1';
const POLL_INTERVAL_MS = 2000;

export function useQuantumJob(): {
  jobState: QuantumJobResult;
  startPolling: (jobId: string) => void;
  stopPolling: () => void;
} {
  const [jobState, setJobState] = useState<QuantumJobResult>({
    status: 'PENDING',
    progress: 0,
    result: null,
    error: null,
    jobId: null,
  });

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const jobIdRef    = useRef<string | null>(null);

  const stopPolling = useCallback((): void => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const poll = useCallback(async (jobId: string): Promise<void> => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_BASE}/quantum-jobs/${jobId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });

      if (!res.ok) {
        setJobState((prev) => ({ ...prev, status: 'FAILED', error: `HTTP ${res.status}` }));
        stopPolling();
        return;
      }

      const data = (await res.json()) as {
        status: JobStatus;
        progress?: number;
        result?: Record<string, unknown>;
        error_message?: string;
      };

      setJobState({
        status: data.status,
        progress: data.progress ?? (data.status === 'COMPLETE' ? 100 : 0),
        result: data.result ?? null,
        error: data.error_message ?? null,
        jobId,
      });

      if (data.status === 'COMPLETE' || data.status === 'FAILED') {
        stopPolling();
      }
    } catch (err) {
      setJobState((prev) => ({
        ...prev,
        status: 'FAILED',
        error: err instanceof Error ? err.message : 'Unknown error',
      }));
      stopPolling();
    }
  }, [stopPolling]);

  const startPolling = useCallback((jobId: string): void => {
    stopPolling();
    jobIdRef.current = jobId;

    setJobState({ status: 'RUNNING', progress: 0, result: null, error: null, jobId });

    // Immediate first poll
    void poll(jobId);

    intervalRef.current = setInterval(() => {
      if (jobIdRef.current) void poll(jobIdRef.current);
    }, POLL_INTERVAL_MS);
  }, [poll, stopPolling]);

  // Clean up on unmount
  useEffect(() => () => stopPolling(), [stopPolling]);

  return { jobState, startPolling, stopPolling };
}
