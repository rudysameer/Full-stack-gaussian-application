from pathlib import Path

from backend.services.job_runner import JobRunner
from backend.services.project_service import ProjectService
from backend.services.runtime_job_registry import RuntimeJobRegistry

class ViewerService:
    def __init__(self, 
            job_runner: JobRunner, 
            project_service: ProjectService,
            runtime_registry: RuntimeJobRegistry,
            ):
        self.job_runner = job_runner
        self.project_service = project_service
        self.runtime_registry = runtime_registry

        self.gs_library_python = (
            "/home/samir-maharjan/anaconda3/envs/gs-library/bin/python"
        )

        self.data_repo = (
            "/home/samir-maharjan/fastapi-backend-gs"
        )

    def run(
        self,
        project_name: str,
        iteration: int,
    ) -> str:

        project = self.project_service.get_project(project_name)

        if project is None:
            raise ValueError("Project not found")

        if not project["training"]["completed"]:
            raise ValueError("Training has not been completed")

        if iteration not in project["training"]["iterations"]:
            raise ValueError(
                f"Training iteration {iteration} is not available"
            )

        output_dir = (
            Path(self.data_repo)
            / "output"
            / project_name
        )

        command = [
            self.gs_library_python,
            "-m",
            "gaussian_splatting.viewer",
            "-d",
            str(output_dir),
            "-i",
            str(iteration),
        ]

        job_id = self.job_runner.run_process(
            command,
            cwd=self.data_repo,
        )

        self.runtime_registry.register(
            project_name=project_name,
            operation="viewer",
            job_id=job_id,
            iteration=iteration,
        )

        return job_id

    def get_status(self, project_name: str):
        runtime_job = self.runtime_registry.get(
            project_name,
            "viewer",
        )

        if runtime_job is None:
            return {
                "status": "stopped",
                "job_id": None,
                "iteration": None,
            }

        job = self.job_runner.status(
            runtime_job["job_id"]
        )

        if job is None:
            self.runtime_registry.remove(
                project_name,
                "viewer",
            )

            return {
                "status": "stopped",
                "job_id": None,
                "iteration": None,
            }

        if job.status in {
            "completed",
            "failed",
        }:
            self.runtime_registry.remove(
                project_name,
                "viewer",
            )

            return {
                "status": "stopped",
                "job_id": None,
                "iteration": None,
            }

        return {
            "status": job.status,
            "job_id": runtime_job["job_id"],
            "iteration": runtime_job["iteration"],
        }