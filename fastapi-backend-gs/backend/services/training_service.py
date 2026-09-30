from pathlib import Path
from fastapi import HTTPException # type: ignore
from backend.services.job_runner import JobRunner
from backend.services.project_service import ProjectService
from backend.services.runtime_job_registry import RuntimeJobRegistry
from backend.services.progress_parser_training import TrainingProgressParser

class TrainingService:
    def __init__(
            self, 
            job_runner: JobRunner,
            project_service: ProjectService,
            runtime_registry: RuntimeJobRegistry,

        ):
        self.job_runner = job_runner
        self.project_service = project_service
        self.runtime_registry = runtime_registry

        self.official_python = (
            "/home/samir-maharjan/anaconda3/envs/official-gsplat/bin/python"
        )

        self.official_gsplat_repo = (
            "/home/samir-maharjan/official-gsplat/gaussian-splatting"
        )

        self.data_repo = (
            "/home/samir-maharjan/fastapi-backend-gs"
        )

    def run(
        self,
        project_name: str,
        iteration,
        ) -> str:
        project = self.project_service.get_project(project_name)
        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )
        
        if not self.project_service.is_colmap_completed(project_name):
            raise ValueError(
                "COLMAP has not been completed"
            )

        source_dir = (
            Path(self.data_repo)
            / "data"
            / project_name
        )

        output_dir = (
            Path(self.data_repo)
            / "output"
            / project_name
        )
        output_dir.mkdir(parents=True, exist_ok=True)


        command = [
            self.official_python,
            "train.py",
            "-s",
            str(source_dir),
            "-m",
            str(output_dir),
            "--iterations",
            str(iteration),
            "--checkpoint_iterations",
            str(iteration),
            "--save_iterations",
            str(iteration),
        ]

        # for pipeline running, we can use run_pipeline, but since we only have one command to run for training, we can use run_process instead
        # return self.job_runner.run_pipeline(
        #     [command],
        #     cwd=self.official_gsplat_repo,
        # )
        # parser is for reading the training progress from the logs and updating the progress status in the job_runner
        parser = TrainingProgressParser()

        job_id = self.job_runner.run_process(
            command,
            cwd=self.official_gsplat_repo,
            progress_parser=parser,
        )

        self.runtime_registry.register(
            project_name=project_name,
            operation="training",
            job_id=job_id,
            iteration=iteration,
        )

        return job_id

    def get_status(self, project_name: str):
        runtime_job = self.runtime_registry.get(
            project_name,
            "training",
        )

        if runtime_job is None:
            return {
                "status": "idle",
                "job_id": None,
                "iteration": None,
                "progress": None,
                "current_iteration": None,
                "target_iteration": None,
            }

        job = self.job_runner.status(
            runtime_job["job_id"]
        )

        if job is None:
            self.runtime_registry.remove(
                project_name,
                "training",
            )

            return {
                "status": "idle",
                "job_id": None,
                "iteration": None,
                "progress": None,
                "current_iteration": None,
                "target_iteration": None,

            }

        if job.status in {
            "completed",
            "failed",
        }:
            self.runtime_registry.remove(
                project_name,
                "training",
            )

        return {
            "status": job.status,
            "job_id": runtime_job["job_id"],
            "iteration": runtime_job["iteration"],
            "progress": job.progress,
            "current_iteration": job.current_iteration,
            "target_iteration": job.target_iteration,
        }
