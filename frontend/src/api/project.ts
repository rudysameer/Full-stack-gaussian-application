import type {
  JobStartResponse,
  Project,
  ProjectsResponse,
  VideoUploadResponse,
  ViewerStartResponse,
} from "../types/project";
import { apiRequest } from "./client";

/**
 * Get all projects/scenes.
 *
 * GET /projects
 */
export async function getProjects(): Promise<Project[]> {
  const response = await apiRequest<ProjectsResponse>("/projects");

  return response.projects;
}

/**
 * Get a single project.
 *
 * GET /projects/{project_name}
 */
export async function getProject(
  projectName: string,
): Promise<Project> {
  return apiRequest<Project>(
    `/projects/${encodeURIComponent(projectName)}`,
  );
}

/**
 * Upload a video and extract frames.
 *
 * POST /projects/{project_name}/video
 */
export async function uploadVideo(
  projectName: string,
  videoFile: File,
): Promise<VideoUploadResponse> {
  const formData = new FormData();

  formData.append("video", videoFile);

  return apiRequest<VideoUploadResponse>(
    `/projects/${encodeURIComponent(projectName)}/video`,
    {
      method: "POST",
      body: formData,
    },
  );
}

/**
 * Start COLMAP processing.
 *
 * POST /projects/{project_name}/colmap
 */
export async function startColmap(
  projectName: string,
): Promise<JobStartResponse> {
  return apiRequest<JobStartResponse>(
    `/projects/${encodeURIComponent(projectName)}/colmap`,
    {
      method: "POST",
    },
  );
}

/**
 * Start Gaussian Splatting training.
 *
 * POST /projects/{project_name}/train?iteration=...
 */
export async function startTraining(
  projectName: string,
  iteration: number = 200,
): Promise<JobStartResponse> {
  const params = new URLSearchParams({
    iteration: String(iteration),
  });

  return apiRequest<JobStartResponse>(
    `/projects/${encodeURIComponent(projectName)}/train?${params.toString()}`,
    {
      method: "POST",
    },
  );
}

/**
 * Start the viewer for a selected training iteration.
 *
 * POST /projects/{project_name}/viewer?iteration=...
 */
export async function startViewer(
  projectName: string,
  iteration: number,
): Promise<ViewerStartResponse> {
  const params = new URLSearchParams({
    iteration: String(iteration),
  });

  return apiRequest<ViewerStartResponse>(
    `/projects/${encodeURIComponent(projectName)}/viewer?${params.toString()}`,
    {
      method: "POST",
    },
  );
}

/**
 * Stop the viewer for a selected project.

 */
export async function stopViewer(
  projectName: string,
): Promise<{ project: string; status: string }> {
  return apiRequest(
    `/projects/${encodeURIComponent(projectName)}/viewer/stop`,
    {
      method: "POST",
    },
  );
}

/**
 * Delete the project for selected project

 */
export async function deleteProject(projectName: string) {
  return apiRequest(`/projects/${projectName}`, {
    method: "DELETE",
  });
}