from fastapi import FastAPI, File, HTTPException, Query, UploadFile # type: ignore
from backend.services.process_manager import ProcessManager

from backend.services.job_runner import JobRunner
from backend.services.colmap_service import ColmapService
from backend.services.training_service import TrainingService
from backend.services.viewer_service import ViewerService
from backend.services.project_service import ProjectService
from backend.services.runtime_job_registry import RuntimeJobRegistry
from backend.services.video_service import VideoService
# for eliminatinf cors errors when frontend and backend are running on different ports
from fastapi.middleware.cors import CORSMiddleware
# for putting thubnail of the video in the frontend
from fastapi.responses import FileResponse
from pathlib import Path


app = FastAPI(title="Gaussian SPlatting Backend")

# CORS middleware configuration to allow requests from the frontend running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# for colmap commands running running 3 colmap commands sequentially
job_runner = JobRunner()
# tracks project_name, operation, job_id, and iteration for each running job
# (project, operation) → job, iteration=can be None if not applicable
runtime_registry = RuntimeJobRegistry()


# for managing projects and their input data
# checkd number of project and other status of the project
# it takes job_runner and runtime_registry as arguments to manage the jobs and their status
project_service = ProjectService(job_runner, runtime_registry)

colmap_service = ColmapService(job_runner ,project_service ,runtime_registry)
training_service = TrainingService(job_runner ,project_service ,runtime_registry)
viewer_service = ViewerService(job_runner,project_service ,runtime_registry)

# extracting input frames for uploaded video
video_service = VideoService()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = job_runner.status(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "job_id": job.job_id,
        "status": job.status,
        # current step and total steps of the job/process/command
        "current_step": job.current_step,
        "total_steps": job.total_steps,
        # for both training and colmap
        "progress": job.progress,
        #colmap progress status for colmap purpose only
        "stage": job.stage,
        "current": job.current,
        "total": job.total,

        # training progress status for training purpose only
        "current_iteration": job.current_iteration,
        "target_iteration": job.target_iteration,
        "loss": job.loss,
        # return code of the process, None if the process is still running
        "return_code": job.return_code,
        "started_at": job.started_at.isoformat(),
    }


@app.get("/jobs/{job_id}/logs")
def get_job_logs(job_id: str):
    logs = job_runner.get_logs(job_id)

    if logs is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return {
        "job_id": job_id,
        "logs": logs,
    }

# stop a running job id 
@app.post("/jobs/{job_id}/stop")
def stop_job(job_id: str):
    stopped = job_runner.stop(job_id)

    if not stopped:
        raise HTTPException(
            status_code=404,
            detail="Job not found or already finished",
        )

    return {
        "job_id": job_id,
        "status": "stopped",
    }

# colmap endpoints
@app.post("/projects/{project_name}/colmap")
def start_colmap(project_name: str):

    try:
        job_id = colmap_service.run(project_name)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {
        "project": project_name,
        "job_id": job_id,
        "status": "running",
    }


# training endpoints
@app.post("/projects/{project_name}/train")
def start_training(
    project_name: str, 
    # 200 means if no value is provided, default training iterations will be 200
    iteration: int = Query(200, gt=0, description="Number of training iterations")
    ):

    try:
        job_id = training_service.run(project_name,iteration)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    
    return {
        "project": project_name,
        "job_id": job_id,
        "status": "queued",
    }

# viewer endpoints
@app.post("/projects/{project_name}/viewer")
def start_viewer(project_name: str, iteration: int = Query(..., description="Training iteration to view")):
    try:
        job_id = viewer_service.run(
            project_name,
            iteration
        )

    except ValueError as error:
        detail = str(error)

        if detail == "Project not found":
            raise HTTPException(
                status_code=404,
                detail=detail,
            )

        raise HTTPException(
            status_code=400,
            detail=detail,
        )

    return {
        "project": project_name,
        "iteration": iteration,
        "job_id": job_id,
        "status": "queued",
    }

# stopping the viewer
@app.post("/projects/{project_name}/viewer/stop")
def stop_viewer(project_name: str):
    stopped = job_runner.stop_viewer(project_name)

    if not stopped:
        raise HTTPException(
            status_code=404,
            detail="Viewer is not running",
        )

    return {
        "project": project_name,
        "status": "stopped",
    }


# project endpoints
# returns list of projects
@app.get("/projects")
def get_projects():
    projects = project_service.list_projects()

    return {
        "projects": projects,
    }

# uploading video and extracting frames from the video
@app.post("/projects/{project_name}/video")
def upload_video(
    project_name: str,
    video: UploadFile = File(...),
):

    try:
        extracted_frames = (
            video_service.process_video(
                project_name,
                video,
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {
        "project": project_name,
        "status": "completed",
        "extracted_frames": extracted_frames,
    }


# returns specific project details
@app.get("/projects/{project_name}")
def get_project(project_name: str):
    project = project_service.get_project(project_name)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project

# for returning the thumbnail of the video in the frontend
@app.get("/projects/{project_name}/thumbnail")
def get_project_thumbnail(project_name: str):
    project_directory = Path("data") / project_name
    input_directory = project_directory / "input"

    if not input_directory.exists():
        raise HTTPException(
            status_code=404,
            detail="Project input directory not found",
        )

    frames = sorted(input_directory.glob("*.jpg"))

    if not frames:
        raise HTTPException(
            status_code=404,
            detail="No input frames found for this project",
        )

    return FileResponse(
        frames[0],
        media_type="image/jpeg",
    )

# for delteing the scene cards
@app.delete("/projects/{project_name}")
def delete_project(project_name: str):
    try:
        deleted = project_service.delete_project(project_name)
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e),
        )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return {
        "project": project_name,
        "status": "deleted",
    }