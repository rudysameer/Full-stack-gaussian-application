export type JobStatus =
  | "queued"
  | "running"
  | "completed"
  | "failed"
  | "stopped";

export interface Job {
  job_id: string;
  status: JobStatus;

  current_step: number | null;
  total_steps: number | null;

  progress: number | null;
  stage: string | null;
  current: number | null;
  total: number | null;

  current_iteration: number | null;
  target_iteration: number | null;
  loss: number | null;

  return_code: number | null;
  started_at: string;
}

export interface JobLogsResponse {
  job_id: string;
  logs: string;
}

export interface StopJobResponse {
  job_id: string;
  status: string;
}