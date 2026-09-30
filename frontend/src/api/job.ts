import type{
  Job,
  JobLogsResponse,
  StopJobResponse,
} from "../types/job";
import { apiRequest } from "./client";

/**
 * Get detailed information about a job.
 *
 * GET /jobs/{job_id}
 */
export async function getJob(
  jobId: string,
): Promise<Job> {
  return apiRequest<Job>(
    `/jobs/${encodeURIComponent(jobId)}`,
  );
}

/**
 * Get logs for a job.
 *
 * GET /jobs/{job_id}/logs
 */
export async function getJobLogs(
  jobId: string,
): Promise<JobLogsResponse> {
  return apiRequest<JobLogsResponse>(
    `/jobs/${encodeURIComponent(jobId)}/logs`,
  );
}

/**
 * Stop a running job.
 *
 * POST /jobs/{job_id}/stop
 */
export async function stopJob(
  jobId: string,
): Promise<StopJobResponse> {
  return apiRequest<StopJobResponse>(
    `/jobs/${encodeURIComponent(jobId)}/stop`,
    {
      method: "POST",
    },
  );
}