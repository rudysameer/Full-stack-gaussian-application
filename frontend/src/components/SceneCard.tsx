import { API_BASE_URL } from "../api/client";
import type { Project } from "../types/project";

interface SceneCardProps {
  project: Project;
  onOpen: (projectName: string) => void;
}

function getStatus(project: Project): string {
  if (project.colmap.status === "running") {
    return "COLMAP Running";
  }

  if (project.training.status === "running") {
    return "Training";
  }

  if (project.viewer.status === "running") {
    return "Viewer Running";
  }

  if (project.training.completed) {
    return "Ready";
  }

  if (project.colmap.completed) {
    return "COLMAP Complete";
  }

  if (project.input.ready) {
    return "Input Ready";
  }

  return "Not Ready";
}

function getStatusClass(project: Project): string {
  if (project.training.completed) {
    return "status-ready";
  }

  if (
    project.colmap.status === "running" ||
    project.training.status === "running"
  ) {
    return "status-running";
  }

  if (project.input.ready) {
    return "status-input";
  }

  return "status-default";
}

function SceneCard({
  project,
  onOpen,
}: SceneCardProps) {
  const status = getStatus(project);
  const statusClass = getStatusClass(project);

  const thumbnailUrl =
    `${API_BASE_URL}/projects/` +
    `${encodeURIComponent(project.project)}/thumbnail`;

  return (
    <article className="scene-card">
      <div className="scene-thumbnail-wrapper">
        <img
          className="scene-thumbnail"
          src={thumbnailUrl}
          alt={`${project.project} scene`}
        />

        <span
          className={`scene-status ${statusClass}`}
        >
          <span className="status-dot" />
          {status}
        </span>
      </div>

      <div className="scene-card-body">
        <div className="scene-card-title-row">
          <div>
            <h2>{project.project}</h2>
          </div>

          <button
            type="button"
            className="scene-menu-button"
            aria-label={`Options for ${project.project}`}
          >
            •••
          </button>
        </div>

        <div className="scene-divider" />

        <div className="scene-stats">
          <div className="scene-stat">
            <span className="scene-stat-icon">
              ▧
            </span>

            <div>
              <span className="scene-stat-label">
                Input images
              </span>

              <strong>
                {project.input.image_count}
              </strong>
            </div>
          </div>

          <div className="scene-stat">
            <span className="scene-stat-icon">
              ◇
            </span>

            <div>
              <span className="scene-stat-label">
                COLMAP
              </span>

              <strong
                className={
                  project.colmap.completed
                    ? "stat-success"
                    : ""
                }
              >
                {project.colmap.completed
                  ? "Completed"
                  : project.colmap.status}
              </strong>
            </div>
          </div>

          <div className="scene-stat">
            <span className="scene-stat-icon">
              ⚙
            </span>

            <div>
              <span className="scene-stat-label">
                Training
              </span>

              <strong>
                {project.training.iterations.length > 0
                  ? project.training.iterations.join(", ")
                  : "Not trained"}
              </strong>
            </div>
          </div>
        </div>

        <button
          type="button"
          className="open-scene-button"
          onClick={() => onOpen(project.project)}
        >
          <span>Open Scene</span>
          <span className="open-scene-arrow">↗</span>
        </button>
      </div>
    </article>
  );
}

export default SceneCard;