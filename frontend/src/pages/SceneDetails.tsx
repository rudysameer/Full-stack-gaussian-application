
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import "./SceneDetails.css";
import {
  getProject,
  startColmap,
  startTraining,
  startViewer,
  stopViewer,
  deleteProject,
} from "../api/project";
import { stopJob } from "../api/job";
import type { Project } from "../types/project";

function SceneDetails() {
  const { projectName } = useParams<{
    projectName: string;
  }>();

  const navigate = useNavigate();
  //   this is for viewer
  const viewerUrl =
  import.meta.env.VITE_VIEWER_URL ||
  "http://localhost:8080";


  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

//   this is for viewer
  const [viewerLoading, setViewerLoading] = useState(false);
  const [viewerIteration, setViewerIteration] =
  useState<number | null>(null);

  const [selectedIteration, setSelectedIteration] =
    useState(200);
  const [customIteration, setCustomIteration] =
    useState("");

  const [error, setError] = useState<string | null>(null);

  // for delete scenes
  const [deleteLoading, setDeleteLoading] = useState(false);


  const loadProject = useCallback(async () => {
    if (!projectName) {
      return;
    }

    try {
      const data = await getProject(projectName);
      setProject(data);
      setError(null);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to load scene.");
      }
    } finally {
      setLoading(false);
    }
  }, [projectName]);

  useEffect(() => {
    loadProject();
  }, [loadProject]);

  /*
   * Poll the project while COLMAP or training is running.
   */
  useEffect(() => {
    if (!project) {
      return;
    }

    const isBusy =
      project.colmap.status === "running" ||
      project.training.status === "running"||
      project.viewer.status === "running";

    if (!isBusy) {
      return;
    }

    const interval = window.setInterval(() => {
      loadProject();
    }, 1500);

    return () => {
      window.clearInterval(interval);
    };
  }, [project, loadProject]);

//   viewing url for viewer starts
async function handleOpenViewer(iteration: number) {
  if (!projectName) {
    return;
  }

  try {
    setViewerLoading(true);
    setViewerIteration(iteration);
    setError(null);

    /*
     * Ask the backend to start the Gaussian Splatting viewer.
     */
    const viewer_job = await startViewer(projectName, iteration);
    console.log("VIEWER START RESPONSE:", viewer_job);

    /*
     * The backend response means the viewer job was queued.
     * Viser may need a few seconds before port 8080 is ready.
     *
     * Poll the viewer URL until it responds.
     */
    const maxAttempts = 30;
    const delay = 500;

    let viewerReady = false;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        await fetch(viewerUrl, {
          method: "GET",
          mode: "no-cors",
        });

        viewerReady = true;
        break;
      } catch {
        await new Promise((resolve) =>
          setTimeout(resolve, delay),
        );
      }
    }

    if (!viewerReady) {
      throw new Error(
        "Viewer did not start within the expected time.",
      );
    }

    /*
     * Open the Viser viewer.
     */
    window.open(viewerUrl, "_blank");
  } catch (error) {
    if (error instanceof Error) {
      setError(error.message);
    } else {
      setError("Failed to start viewer.");
    }
  } finally {
    setViewerLoading(false);
    setViewerIteration(null);
  }
}

// stoping the viewer function
async function handleStopViewer() {
  if (!projectName) {
    return;
  }

  try {
    setViewerLoading(true);
    setError(null);

    await stopViewer(projectName);

    await loadProject();
  } catch (error) {
    if (error instanceof Error) {
      setError(error.message);
    } else {
      setError("Failed to stop viewer.");
    }
  } finally {
    setViewerLoading(false);
  }
}
// viewer visor ends here

// for deleting the scenes function
async function handleDeleteScene() {
  if (!project) {
    return;
  }

  const confirmed = window.confirm(
    `Are you sure you want to delete "${project.project}"?\n\n` +
    `This will delete the scene, COLMAP data, and trained models. ` +
    `This action cannot be undone.`,
  );

  if (!confirmed) {
    return;
  }

  try {
    setDeleteLoading(true);

    await deleteProject(project.project);

    navigate("/scenes");
  } catch (error) {
    console.error("Failed to delete scene:", error);

    alert("Failed to delete scene. Please try again.");
  } finally {
    setDeleteLoading(false);
  }
}

  async function handleRunColmap() {
    if (!projectName) {
      return;
    }

    try {
      setActionLoading(true);
      setError(null);

      await startColmap(projectName);

      await loadProject();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to start COLMAP.");
      }
    } finally {
      setActionLoading(false);
    }
  }

  async function handleStopColmap() {
    if (!project?.colmap.job_id) {
      return;
    }

    try {
      setActionLoading(true);
      setError(null);

      await stopJob(project.colmap.job_id);

      await loadProject();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to stop COLMAP.");
      }
    } finally {
      setActionLoading(false);
    }
  }

  async function handleStartTraining() {
    if (!projectName) {
      return;
    }

    const iteration =
      customIteration.trim() !== ""
        ? Number(customIteration)
        : selectedIteration;

    if (!Number.isInteger(iteration) || iteration <= 0) {
      setError(
        "Training iteration must be a positive integer.",
      );
      return;
    }

    try {
      setActionLoading(true);
      setError(null);

      await startTraining(projectName, iteration);

      await loadProject();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to start training.");
      }
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return (
      <main className="scene-details-page">
        <div className="scene-details-loading">
          <div className="loading-spinner" />
          <p>Loading scene...</p>
        </div>
      </main>
    );
  }

  if (error && !project) {
    return (
      <main className="scene-details-page">
        <div className="scene-details-error">
          <h1>Scene not found</h1>
          <p>{error}</p>

          <button
            type="button"
            className="primary-button"
            onClick={() => navigate("/scenes")}
          >
            Back to My Scenes
          </button>
        </div>
      </main>
    );
  }

  if (!project) {
    return null;
  }
  console.log("VIEWER STATE:", project.viewer);

  const colmapRunning =
    project.colmap.status === "running";

  const trainingRunning =
    project.training.status === "running";

  const trainingAvailable =
    project.actions.can_train &&
    project.colmap.completed &&
    !trainingRunning;

  return (
    <main className="scene-details-page">
      <div className="scene-details-container">

        {/* Header */}

        <header className="scene-details-header">
          <button
            type="button"
            className="back-button"
            onClick={() => navigate("/scenes")}
          >
            <span>←</span>
            My Scenes
          </button>

          <div className="scene-details-title">
            <div>
              <span className="section-eyebrow">
                SCENE
              </span>

              <h1>{project.project}</h1>

              <p>
                Gaussian Splatting reconstruction pipeline
              </p>
            </div>

            <div
              className={`details-status ${
                project.training.completed
                  ? "status-ready"
                  : project.colmap.completed
                    ? "status-colmap"
                    : "status-input"
              }`}
            >
              <span className="status-dot" />

              {project.training.completed
                ? "Ready"
                : project.colmap.completed
                  ? "COLMAP Complete"
                  : project.input.ready
                    ? "Input Ready"
                    : "Not Ready"}
            </div>
              {/* Delete scene */}
              <button
                type="button"
                className="delete-scene-button"
                disabled={deleteLoading}
                onClick={handleDeleteScene}
              >
                {deleteLoading
                  ? "Deleting..."
                  : "Delete Scene"}
              </button>
          </div>
        </header>

        {/* Error */}

        {error && (
          <div className="new-scene-error">
            <span>!</span>
            <p>{error}</p>
          </div>
        )}

        {/* Input */}

        <section className="pipeline-card">
          <div className="pipeline-card-header">
            <div className="pipeline-step complete">
              <span>01</span>
            </div>

            <div>
              <h2>Input</h2>
              <p>
                Source images extracted from your video.
              </p>
            </div>

            <div className="pipeline-card-status completed-label">
              ✓ Ready
            </div>
          </div>

          <div className="input-summary">
            <div className="input-summary-icon">
              ▧
            </div>

            <div>
              <strong>
                {project.input.image_count} images
              </strong>

              <span>
                Ready for camera reconstruction
              </span>
            </div>
          </div>
        </section>

        {/* COLMAP */}

        <section className="pipeline-card">
          <div className="pipeline-card-header">
            <div
              className={`pipeline-step ${
                project.colmap.completed
                  ? "complete"
                  : colmapRunning
                    ? "active"
                    : ""
              }`}
            >
              <span>02</span>
            </div>

            <div>
              <h2>COLMAP Reconstruction</h2>

              <p>
                Estimate camera poses and reconstruct the
                scene.
              </p>
            </div>

            <div className="pipeline-card-status">
              {project.colmap.completed ? (
                <span className="completed-label">
                  ✓ Completed
                </span>
              ) : colmapRunning ? (
                <span className="running-label">
                  ● Running
                </span>
              ) : (
                <span>Not started</span>
              )}
            </div>
          </div>

          {colmapRunning ? (
            <div className="progress-area">
              <div className="progress-top">
                <span>
                  {formatColmapStage(
                    project.colmap.stage,
                  )}
                </span>

                <strong>
                  {Math.round(
                    project.colmap.progress ?? 0,
                  )}
                  %
                </strong>
              </div>

              <div className="progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${Math.min(
                      project.colmap.progress ?? 0,
                      100,
                    )}%`,
                  }}
                />
              </div>

              {project.colmap.current !== null &&
                project.colmap.total !== null && (
                  <p className="progress-detail">
                    Processing{" "}
                    {project.colmap.current} of{" "}
                    {project.colmap.total}
                  </p>
                )}

              <button
                type="button"
                className="stop-button"
                disabled={actionLoading}
                onClick={handleStopColmap}
              >
                Stop COLMAP
              </button>
            </div>
          ) : project.colmap.completed ? (
            <div className="completed-box">
              <span className="completed-check">
                ✓
              </span>

              <div>
                <strong>
                  Camera reconstruction completed
                </strong>

                <p>
                  The scene is ready for Gaussian
                  Splatting training.
                </p>
              </div>
            </div>
          ) : (
            <div className="pipeline-action">
              <div>
                <strong>
                  Camera reconstruction required
                </strong>

                <p>
                  Run COLMAP before starting Gaussian
                  Splatting training.
                </p>
              </div>

              <button
                type="button"
                className="primary-action-button"
                disabled={
                  actionLoading ||
                  !project.actions.can_run_colmap
                }
                onClick={handleRunColmap}
              >
                {actionLoading
                  ? "Starting..."
                  : "Run COLMAP"}
                <span>→</span>
              </button>
            </div>
          )}
        </section>

        {/* Training */}

        <section
          className={`pipeline-card ${
            !project.colmap.completed
              ? "pipeline-disabled"
              : ""
          }`}
        >
          <div className="pipeline-card-header">
            <div
              className={`pipeline-step ${
                trainingRunning
                  ? "active"
                  : project.training.completed
                    ? "complete"
                    : ""
              }`}
            >
              <span>03</span>
            </div>

            <div>
              <h2>Gaussian Splatting Training</h2>

              <p>
                Train the Gaussian representation of your
                scene.
              </p>
            </div>

            <div className="pipeline-card-status">
              {trainingRunning ? (
                <span className="running-label">
                  ● Running
                </span>
              ) : project.training.completed ? (
                <span className="completed-label">
                  ✓ Trained
                </span>
              ) : (
                <span>Not started</span>
              )}
            </div>
          </div>

          {!project.colmap.completed ? (
            <div className="locked-box">
              <span>🔒</span>

              <div>
                <strong>
                  Complete COLMAP first
                </strong>

                <p>
                  Training becomes available after camera
                  reconstruction is finished.
                </p>
              </div>
            </div>
          ) : trainingRunning ? (
            <div className="progress-area">
              <div className="progress-top">
                <span>
                  Training Gaussian model
                </span>

                <strong>
                  {Math.round(
                    project.training.progress ?? 0,
                  )}
                  %
                </strong>
              </div>

              <div className="progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{
                    width: `${Math.min(
                      project.training.progress ?? 0,
                      100,
                    )}%`,
                  }}
                />
              </div>

              <p className="progress-detail">
                Iteration{" "}
                {project.training.current_iteration ??
                  0}{" "}
                /{" "}
                {project.training.target_iteration ??
                  0}
              </p>
            </div>
          ) : (
            <>
              <div className="training-results">
                <span className="training-results-label">
                  Available trained iterations
                </span>

                <div className="iteration-list">
                  {project.training.iterations.length >
                  0 ? (
                    project.training.iterations.map(
                      (iteration) => (
                        <span
                          key={iteration}
                          className="iteration-chip"
                        >
                          {iteration}
                        </span>
                      ),
                    )
                  ) : (
                    <span className="no-iterations">
                      No trained iterations yet
                    </span>
                  )}
                </div>
              </div>

              <div className="training-controls">
                <div className="iteration-select-wrapper">
                  <label htmlFor="iteration">
                    Training iterations
                  </label>

                  <select
                    id="iteration"
                    value={selectedIteration}
                    onChange={(event) => {
                      setSelectedIteration(
                        Number(event.target.value),
                      );

                      setCustomIteration("");
                    }}
                  >
                    <option value={100}>
                      100 iterations
                    </option>

                    <option value={200}>
                      200 iterations
                    </option>

                    <option value={500}>
                      500 iterations
                    </option>

                    <option value={1000}>
                      1,000 iterations
                    </option>

                    <option value={3000}>
                      3,000 iterations
                    </option>

                    <option value={5000}>
                      5,000 iterations
                    </option>
                  </select>
                </div>

                <div className="custom-iteration">
                  <label htmlFor="custom-iteration">
                    Or custom
                  </label>

                  <input
                    id="custom-iteration"
                    type="number"
                    min="1"
                    step="1"
                    placeholder="e.g. 2000"
                    value={customIteration}
                    onChange={(event) =>
                      setCustomIteration(
                        event.target.value,
                      )
                    }
                  />
                </div>

                <button
                  type="button"
                  className="primary-action-button"
                  disabled={
                    actionLoading ||
                    !trainingAvailable
                  }
                  onClick={handleStartTraining}
                >
                  {actionLoading
                    ? "Starting..."
                    : "Start Training"}
                  <span>→</span>
                </button>
              </div>
            </>
          )}
        </section>

        {/* Current trained models */}

        {project.training.iterations.length > 0 && (
          <section className="trained-results-card">
            <div>
              <span className="section-eyebrow">
                RESULTS
              </span>

              <h2>Trained Models</h2>

              <p>
                These iterations are available for viewing.
              </p>
            </div>

            <div className="trained-results-list">
              {project.training.iterations.map(
                (iteration) => (
                  <div
                    className="trained-result"
                    key={iteration}
                  >
                    <div>
                      <span>Iteration</span>
                      <strong>{iteration}</strong>
                    </div>

                    {/* button for starting/seeing viewer */}
                    {project.viewer.status === "running" ? (
                      <button
                        type="button"
                        className="viewer-stop-button"
                        disabled={viewerLoading}
                        onClick={handleStopViewer}
                      >
                        {viewerLoading ? "Stopping..." : "Stop Viewer"}
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="viewer-action-button"
                        disabled={viewerLoading}
                        onClick={() => handleOpenViewer(iteration)}
                      >
                        {viewerLoading && viewerIteration === iteration
                          ? "Opening..."
                          : "Open Viewer"}
                      </button>
                    )}
                  </div>
                ),
              )}
            </div>
          </section>
        )}

      </div>
    </main>
  );
}

function formatColmapStage(
  stage: string | null,
): string {
  switch (stage) {
    case "feature_extraction":
      return "Extracting features";

    case "feature_matching":
      return "Matching features";

    case "mapper":
      return "Reconstructing cameras";

    case "completed":
      return "Completed";

    default:
      return "Processing COLMAP";
  }
}

export default SceneDetails;