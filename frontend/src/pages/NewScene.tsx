import type {
  ChangeEvent,
  DragEvent,
  FormEvent
} from "react";

import {
  useRef,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import { uploadVideo } from "../api/project";

function NewScene() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [projectName, setProjectName] = useState("");
  const [videoFile, setVideoFile] = useState<File | null>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{
    project: string;
    extractedFrames: number;
  } | null>(null);

  function handleFile(file: File | undefined) {
    if (!file) {
      return;
    }

    setError(null);
    setSuccess(null);

    if (!file.type.startsWith("video/")) {
      setError("Please select a video file.");
      return;
    }

    setVideoFile(file);
  }

  function handleFileInput(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    handleFile(event.target.files?.[0]);
  }

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);

    handleFile(event.dataTransfer.files?.[0]);
  }

  function removeFile() {
    setVideoFile(null);
    setError(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function formatFileSize(bytes: number): string {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError(null);
    setSuccess(null);

    const trimmedName = projectName.trim();

    if (!trimmedName) {
      setError("Please enter a scene name.");
      return;
    }

    if (!videoFile) {
      setError("Please select a video.");
      return;
    }

    try {
      setIsUploading(true);

      const response = await uploadVideo(
        trimmedName,
        videoFile,
      );

      setSuccess({
        project: response.project,
        extractedFrames: response.extracted_frames,
      });

      setProjectName("");
      setVideoFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to upload video.");
      }
    } finally {
      setIsUploading(false);
    }
  }

  if (success) {
    return (
      <main className="new-scene-page">
        <section className="new-scene-success">
          <div className="success-icon">✓</div>

          <span className="section-eyebrow">
            SCENE CREATED
          </span>

          <h1>{success.project}</h1>

          <p>
            Your video was successfully processed and{" "}
            <strong>
              {success.extractedFrames} frames
            </strong>{" "}
            were extracted.
          </p>

          <div className="success-actions">
            <button
              type="button"
              className="primary-button"
              onClick={() => navigate("/scenes")}
            >
              View My Scenes
              <span>→</span>
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() => setSuccess(null)}
            >
              Create Another
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="new-scene-page">
      <section className="new-scene-header">
        <button
          type="button"
          className="back-button"
          onClick={() => navigate("/")}
        >
          <span>←</span>
          Back
        </button>

        <div>
          <span className="section-eyebrow">
            CREATE
          </span>

          <h1>New Scene</h1>

          <p>
            Upload a video to create a new Gaussian
            Splatting scene.
          </p>
        </div>
      </section>

      <form
        className="new-scene-form"
        onSubmit={handleSubmit}
      >
        <section className="create-section">
          <div className="create-section-heading">
            <div className="step-number">01</div>

            <div>
              <h2>Name your scene</h2>
              <p>
                Give your scene a unique name.
              </p>
            </div>
          </div>

          <div className="field-wrapper">
            <label htmlFor="project-name">
              Scene name
            </label>

            <input
              id="project-name"
              type="text"
              value={projectName}
              onChange={(event) =>
                setProjectName(event.target.value)
              }
              placeholder="e.g. living_room"
              disabled={isUploading}
              autoComplete="off"
            />

            <span className="field-hint">
              Use a simple name such as{" "}
              <strong>my_room</strong> or{" "}
              <strong>car_scene</strong>.
            </span>
          </div>
        </section>

        <section className="create-section">
          <div className="create-section-heading">
            <div className="step-number">02</div>

            <div>
              <h2>Upload your video</h2>
              <p>
                Choose a video containing the scene you
                want to reconstruct.
              </p>
            </div>
          </div>

          <div
            className={`video-dropzone ${
              isDragging ? "dragging" : ""
            } ${videoFile ? "has-file" : ""}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() =>
              !videoFile &&
              fileInputRef.current?.click()
            }
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileInput}
              hidden
            />

            {!videoFile ? (
              <>
                <div className="upload-icon">
                  ↑
                </div>

                <h3>
                  Drop your video here
                </h3>

                <p>
                  or click to browse your files
                </p>

                <span className="upload-format">
                  MP4, MOV, AVI and other video formats
                </span>
              </>
            ) : (
              <div
                className="selected-video"
                onClick={(event) =>
                  event.stopPropagation()
                }
              >
                <div className="video-file-icon">
                  ▶
                </div>

                <div className="video-file-info">
                  <strong>
                    {videoFile.name}
                  </strong>

                  <span>
                    {formatFileSize(videoFile.size)}
                  </span>
                </div>

                <button
                  type="button"
                  className="remove-file-button"
                  onClick={removeFile}
                  disabled={isUploading}
                  aria-label="Remove video"
                >
                  ×
                </button>
              </div>
            )}
          </div>
        </section>

        {error && (
          <div className="new-scene-error">
            <span>!</span>
            <p>{error}</p>
          </div>
        )}

        <div className="new-scene-submit">
          <button
            type="submit"
            className="create-scene-button"
            disabled={isUploading}
          >
            {isUploading ? (
              <>
                <span className="loading-spinner" />
                Processing video...
              </>
            ) : (
              <>
                Create Scene
                <span>→</span>
              </>
            )}
          </button>

          <p>
            Your video will be processed and frames will be
            extracted automatically.
          </p>
        </div>
      </form>
    </main>
  );
}

export default NewScene;
