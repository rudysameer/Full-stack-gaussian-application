from pathlib import Path
from fastapi import HTTPException # type: ignore

from backend.services.job_runner import JobRunner
from backend.services.project_service import ProjectService
from backend.services.runtime_job_registry import RuntimeJobRegistry
from backend.services.progress_parser_colmap import ColmapProgressParser

class ColmapService:
    def __init__(
            self,
            job_runner: JobRunner, 
            project_service: ProjectService,
            runtime_registry: RuntimeJobRegistry,

        ):
        self.job_runner = job_runner
        self.project_service = project_service
        self.runtime_registry = runtime_registry
        # official -repo environment and paths
        self.official_python = (
            "/home/samir-maharjan/anaconda3/envs/official-gsplat/bin/python"
        )

        self.official_gsplat_repo = (
            "/home/samir-maharjan/official-gsplat/gaussian-splatting"
        )

        # fastapi repo data input path
        self.data_input_repo = (
            "/home/samir-maharjan/fastapi-backend-gs"
        )


    def run(self, project_name: str) -> str:
        project = self.project_service.get_project(project_name)
        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        if not self.project_service.is_input_ready(project_name):
            raise ValueError(
                "Project input is missing or not ready"
            )



        project_dir = Path(
            self.data_input_repo
        ) / "data" / project_name

        command = [
            self.official_python,
            "convert.py",
            "-s",
            str(project_dir),
            "--no_gpu",
        ]

        # image count needed to pass as paramter for colmap progress parser to calculate the progress percentage
        image_count = project["input"]["image_count"]

        parser = ColmapProgressParser(total_images=image_count)

        # doing .run_process instead of .run_pipeline because we only have one command to run for colmap
        # pipline is used when we have multiple commands to run sequentially, where the next command only runs if the previous one succeeds
        # return self.job_runner.run_pipeline([command], cwd=str(self.official_gsplat_repo))


        # start the actual colmap command in a separate process and return the job_id
        job_id = self.job_runner.run_process(
            command, 
            cwd=str(self.official_gsplat_repo),
            progress_parser=parser
        )

        # Remember which job belongs to this project
        self.runtime_registry.register(
            project_name=project_name,
            operation="colmap",
            job_id=job_id,
            iteration=None,
        )

        return job_id

    def get_status(self, project_name: str):
        runtime_job = self.runtime_registry.get(
            project_name,
            "colmap",
        )

        if runtime_job is None:
            return {
                "status": "idle",
                "job_id": None,
            }

        job = self.job_runner.status(
            runtime_job["job_id"]
        )

        if job is None:
            self.runtime_registry.remove(
                project_name,
                "colmap",
            )

            return {
                "status": "idle",
                "job_id": None,
            }

        if job.status in {
            "completed",
            "failed",
        }:
            self.runtime_registry.remove(
                project_name,
                "colmap",
            )

        return {
            "status": job.status,
            "job_id": runtime_job["job_id"],
        }
