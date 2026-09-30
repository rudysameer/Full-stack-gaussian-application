export interface InputState {
  exists: boolean;
  ready: boolean;
  image_count: number;
}

export type ColmapStatus = 'idle' | 'running' | 'completed' | 'failed';

export type ColmapStage =
  | "feature_extraction"
  | "feature_matching"
  | "mapper"
  | "completed";


export interface ColmapState {
  completed: boolean;
  status: ColmapStatus;
  job_id: string | null;
  progress: number | null;
  stage: ColmapStage | null;
  current: number | null;
  total: number | null;
}

export type TrainingStatus =
  | "idle"
  | "running"
  | "completed"
  | "failed";

export interface TrainingState {
  completed: boolean;
  iterations: number[];
  status: TrainingStatus;
  job_id: string | null;
  progress: number | null;
  current_iteration: number | null;
  target_iteration: number | null;
  loss: number | null;
}

export type ViewerStatus = "stopped" | "running";

export interface ViewerState {
  status: ViewerStatus;
  job_id: string | null;
  iteration: number | null;
}

export interface ProjectActions {
  can_run_colmap: boolean;
  can_train: boolean;
  can_view: boolean;
}

export interface Project {
  project: string;
  input: InputState;
  colmap: ColmapState;
  training: TrainingState;
  viewer: ViewerState;
  actions: ProjectActions;
}

export interface ProjectsResponse {
  projects: Project[];
}

export interface VideoUploadResponse {
  project: string;
  status: string;
  extracted_frames: number;
}

export interface JobStartResponse {
  project: string;
  job_id: string;
  status: string;
}

export interface ViewerStartResponse {
  project: string;
  iteration: number;
  job_id: string;
  status: string;
}
