import { create } from 'zustand';

export type JobStatus = 'PENDING' | 'RUNNING' | 'COMPLETE' | 'FAILED';

export interface QuantumJob {
  job_id: string;
  job_type: string;
  status: JobStatus;
  progress: number;
  result: Record<string, unknown> | null;
  error: string | null;
  started_at: string;
  completed_at: string | null;
}

interface QuantumStore {
  activeJobs:  QuantumJob[];
  jobHistory:  QuantumJob[];
  addJob:      (job: QuantumJob) => void;
  updateJob:   (job_id: string, updates: Partial<QuantumJob>) => void;
  archiveJob:  (job_id: string) => void;
  clearHistory: () => void;
}

export const useQuantumStore = create<QuantumStore>()((set, get) => ({
  activeJobs:  [],
  jobHistory:  [],

  addJob: (job) =>
    set((s) => ({ activeJobs: [...s.activeJobs, job] })),

  updateJob: (job_id, updates) =>
    set((s) => ({
      activeJobs: s.activeJobs.map((j) =>
        j.job_id === job_id ? { ...j, ...updates } : j
      ),
    })),

  archiveJob: (job_id) => {
    const job = get().activeJobs.find((j) => j.job_id === job_id);
    if (!job) return;
    set((s) => ({
      activeJobs: s.activeJobs.filter((j) => j.job_id !== job_id),
      jobHistory: [job, ...s.jobHistory.slice(0, 199)],   // keep last 200
    }));
  },

  clearHistory: () => set({ jobHistory: [] }),
}));
