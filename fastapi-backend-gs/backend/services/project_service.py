from pathlib import Path
from backend.services.job_runner import JobRunner
from backend.services.runtime_job_registry import RuntimeJobRegistry
import shutil

class ProjectService:
    def __init__(
        self,
        job_runner: JobRunner,
        runtime_registry: RuntimeJobRegistry,
        data_directory: str = "data",
        output_directory: str = "output",
    ):
        self.job_runner = job_runner
        self.runtime_registry = runtime_registry
        
        self.data_directory = Path(data_directory)
        self.output_directory = Path(output_directory)


    def list_projects(self) -> list[dict]:
        if not self.data_directory.exists():
            return []

        projects = []

        for directory in self.data_directory.iterdir():
            if not directory.is_dir():
                continue

            # uses the get_project method to get the project details from below method
            project = self.get_project(directory.name)

            if project is not None:
                projects.append(project)

        return sorted(
            projects,
            key=lambda project: project["project"],
        )
    
    def get_project(self, project_name: str):
        project_directory = self.data_directory / project_name

        if not project_directory.exists():
            return None

        # -------------------------
        # Input
        # -------------------------

        input_directory = project_directory / "input"

        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
        }

        input_images = []

        if input_directory.exists():
            input_images = [
                file
                for file in input_directory.iterdir()
                if file.is_file()
                and file.suffix.lower() in image_extensions
            ]

        input_exists = input_directory.exists()
        input_ready = len(input_images) > 0

        # -------------------------
        # COLMAP
        # -------------------------

        sparse_directory = project_directory / "sparse" / "0"

        colmap_completed = (
            (sparse_directory / "cameras.bin").exists()
            and (sparse_directory / "images.bin").exists()
            and (sparse_directory / "points3D.bin").exists()
        )

        # -------------------------
        # Training
        # -------------------------

        output_project_directory = (
            self.output_directory / project_name
        )

        point_cloud_directory = (
            output_project_directory / "point_cloud"
        )

        training_iterations = []

        if point_cloud_directory.exists():
            for directory in point_cloud_directory.iterdir():
                if not directory.is_dir():
                    continue

                if not directory.name.startswith("iteration_"):
                    continue

                iteration_string = directory.name.replace(
                    "iteration_",
                    "",
                )

                if not iteration_string.isdigit():
                    continue

                iteration = int(iteration_string)

                point_cloud_file = (
                    directory / "point_cloud.ply"
                )

                if point_cloud_file.exists():
                    training_iterations.append(iteration)

        training_iterations.sort()

        training_completed = len(training_iterations) > 0

        #--------------------------------------------------------------
        # runtime information to return the status of the project, if colmap or training is running for the project
        #---------------------------------------------------------------
        colmap_runtime = self._get_runtime_status(
            project_name,
            "colmap",
        )

        training_runtime = self._get_runtime_status(
            project_name,
            "training",
        )

        viewer_runtime = self._get_runtime_status(
            project_name,
            "viewer",
        )
        # for viewer stop makes more senese thean idle
        if viewer_runtime["status"] == "idle":
            viewer_runtime["status"] = "stopped"

        # -------------------------
        # action status what us allowed and what is not
        #---------------------------
        actions = {
            "can_run_colmap": (
                input_ready
                and colmap_runtime["status"] != "running"
            ),

            "can_train": (
                colmap_completed
                and training_runtime["status"] != "running"
            ),

            "can_view": training_completed,
        }

        # -------------------------
        # Final project status
        # -------------------------

        return {
            "project": project_name,

            "input": {
                "exists": input_exists,
                "ready": input_ready,
                "image_count": len(input_images),
            },

            "colmap": {
                "completed": colmap_completed,
                #colmap runtime status
                "status": colmap_runtime["status"],
                "job_id": colmap_runtime["job_id"],
                "progress": colmap_runtime["progress"],
                "stage": colmap_runtime["stage"],
                "current": colmap_runtime["current"],
                "total": colmap_runtime["total"],
            },

            "training": {
                "completed": training_completed,
                "iterations": training_iterations,
                # training runtime status
                "status": training_runtime["status"],
                "job_id": training_runtime["job_id"],
                "progress": training_runtime["progress"],
                "current_iteration": training_runtime["current_iteration"],
                "target_iteration": training_runtime["target_iteration"],
                "loss": training_runtime["loss"],
            },

            "viewer": {
                #viewer runtime status
                "status": viewer_runtime["status"],
                "job_id": viewer_runtime["job_id"],
            },
            # actions what are allowed and what are not
            "actions": actions,
            
        }

    # validation to start colmap or training, check if input data is ready and colmap is completed before training
    def is_input_ready(self, project_name: str) -> bool:
        project = self.get_project(project_name)

        if project is None:
            return False

        return project["input"]["ready"]


    def is_colmap_completed(self, project_name: str) -> bool:
        project = self.get_project(project_name)

        if project is None:
            return False

        return project["colmap"]["completed"]

    # runtime status helper for the project, check if colmap or training is running for the project
    def _get_runtime_status(
        self,
        project_name: str,
        operation: str,
    ):
        runtime_job = self.runtime_registry.get(
            project_name,
            operation,
        )

        if runtime_job is None:
            return {
                "status": "idle",
                "job_id": None,
                # for both training and colmap
                "progress": None,
                # for colmap progress only
                "stage": None,
                "current": None,
                "total": None,
                # for training progress only
                "current_iteration": None,
                "target_iteration": None,
                "loss": None,
            }

        job = self.job_runner.status(
            runtime_job["job_id"]
        )

        if job is None:
            self.runtime_registry.remove(
                project_name,
                operation,
            )

            return {
                "status": "idle",
                "job_id": None,
                "progress": None,
                "stage": None,
                "current": None,
                "total": None,
                "current_iteration": None,
                "target_iteration": None,
                "loss": None,
            }   

        if job.status in {
            "completed",
            "failed",
        }:
            self.runtime_registry.remove(
                project_name,
                operation,
            )

        return {
            "status": job.status,
            "job_id": runtime_job["job_id"],
            # for both training and colmap
            "progress": job.progress,
            # for colmap progress only
            "stage": job.stage,
            "current": job.current,
            "total": job.total,
            # for training progress only
            "current_iteration": job.current_iteration,
            "target_iteration": job.target_iteration,
            # for loss
            "loss": job.loss,
            
        }
    # to delete the scenes
    def delete_project(self, project_name: str):
        project_directory = self.data_directory / project_name
        output_directory = self.output_directory / project_name

        if not project_directory.exists():
            return False

        # Don't allow deletion while a job is running
        for operation in ["colmap", "training", "viewer"]:
            runtime_job = self.runtime_registry.get(
                project_name,
                operation,
            )

            if runtime_job is not None:
                job = self.job_runner.status(runtime_job["job_id"])

                if job is not None and job.status == "running":
                    raise ValueError(
                        f"Cannot delete project while {operation} is running"
                    )

        # Delete input/COLMAP data
        shutil.rmtree(project_directory)

        # Delete trained models
        if output_directory.exists():
            shutil.rmtree(output_directory)

        return True