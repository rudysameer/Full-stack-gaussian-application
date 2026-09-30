import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import Thread
import os
from backend.services.progress_parser_training import TrainingProgressParser


@dataclass
class JobInfo:
    job_id: str
    status: str
    started_at: datetime

    current_step: int = 0
    total_steps: int = 0

    # every job can remember what command created it. 
    command: list[str] | None = None

    # used for both colmap and training progress status
    progress: float | None = None

    # prgress status for colmap purpose only
    current: int | None = None
    total: int | None = None
    stage: str | None = None

    # progress status for training purpose only
    current_iteration: int | None = None
    target_iteration: int | None = None
    loss: float | None = None

    return_code: int | None = None
    log_file: Path | None = None
    process: subprocess.Popen | None = None


class JobRunner:
    def __init__(self, log_directory: str = "logs/jobs"):
        self.jobs: dict[str, JobInfo] = {}

        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # training progress parser
        self.training_progress_parser = TrainingProgressParser()

    # Start multiple processes sequentially, where the next one only starts if the previous one succeeds
    def run_pipeline(
            self, 
            commands: list[list[str]],
            cwd: str | None = None, 
        )-> str:
        job_id = str(uuid.uuid4())

        log_file = self.log_directory / f"{job_id}.log"

        job = JobInfo(
            job_id=job_id,
            status="queued",
            started_at=datetime.now(),
            total_steps=len(commands),
            log_file=log_file,
        )

        self.jobs[job_id] = job

        thread = Thread(
            target=self._execute_pipeline,
            args=(job, commands, cwd),
            daemon=True,
        )

        thread.start()

        return job_id

    def _execute_pipeline(
        self,
        job: JobInfo,
        commands: list[list[str]],
        cwd: str | None = None,
    ):
        job.status = "running"

        with open(job.log_file, "w") as log:
            for index, command in enumerate(commands, start=1):
                job.current_step = index

                log.write(
                    f"\n===== STEP {index}/{len(commands)} =====\n"
                )

                log.write(
                    "COMMAND: "
                    + " ".join(command)
                    + "\n\n"
                )

                log.flush()

                # it inherits vscode terminal environment from where the command will run
                # it consists of problematic environment through which it is failling
                # removing those environment
                env = os.environ.copy()
                # these are problmetic environment
                for variable in [
                    "GTK_EXE_PREFIX",
                    "GTK_PATH",
                    "LOCPATH",
                    "GSETTINGS_SCHEMA_DIR",
                    "GIO_MODULE_DIR",
                    "XDG_DATA_DIRS",
                ]:
                    env.pop(variable, None)


                process = subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    cwd=cwd,
                )

                return_code = process.wait()

                if return_code != 0:
                    job.status = "failed"
                    job.return_code = return_code

                    log.write(
                        f"\n===== STEP {index} FAILED =====\n"
                    )

                    return

                log.write(
                    f"\n===== STEP {index} COMPLETED =====\n"
                )

            job.status = "completed"
            job.return_code = 0

            log.write("\n===== PIPELINE COMPLETED =====\n")


    # for long countinously runniing process

    def run_process(
        self,
        command: list[str],
        cwd: str | None = None,
        progress_parser=None,
    ) -> str:
        job_id = str(uuid.uuid4())

        log_file = self.log_directory / f"{job_id}.log"

        job = JobInfo(
            job_id=job_id,
            status="queued",
            started_at=datetime.now(),
            command=command,
            current_step=1,
            total_steps=1,
            log_file=log_file,
        )

        self.jobs[job_id] = job

        thread = Thread(
            target=self._execute_process,
            args=(job, command, cwd, progress_parser),
            daemon=True,
        )

        thread.start()

        return job_id

    # execute a long running process of above function
    # Start one process and wait for it to finish
    def _execute_process(
        self,
        job: JobInfo,
        command: list[str],
        cwd: str | None = None,
        progress_parser=None,
    ):
        job.status = "running"

        with open(job.log_file, "w") as log:
            log.write("COMMAND: " + " ".join(command) + "\n\n")
            log.flush()

            env = os.environ.copy()

            for variable in [
                "GTK_EXE_PREFIX",
                "GTK_PATH",
                "LOCPATH",
                "GSETTINGS_SCHEMA_DIR",
                "GIO_MODULE_DIR",
                "XDG_DATA_DIRS",
            ]:
                env.pop(variable, None)

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,# line buffered
                env=env,
                cwd=cwd,
            )

            job.process = process
            # writing stdout in real time to log file
            for line in process.stdout:
                log.write(line)
                log.flush()

                # writing stdout to extract training progress information
                # this is directly using trainig parser
                # progress = self.training_progress_parser.parse(line)
                # if progress is not None:
                #     job.progress = progress["progress"]
                #     job.current_iteration = progress["current_iteration"]
                #     job.target_iteration = progress["target_iteration"]

                # instead of directly using training progress parser we use progress pareser to choose trainng or colmap parser
                if progress_parser is not None:
                    progress = progress_parser.parse(line)

                    if progress is not None:
                        job.progress = progress.get("progress")

                        job.stage = progress.get("stage")

                        job.current = progress.get("current")

                        job.total = progress.get("total")

                        if "current_iteration" in progress:
                            job.current_iteration = (
                                progress["current_iteration"]
                            )

                        if "target_iteration" in progress:
                            job.target_iteration = (
                                progress["target_iteration"]
                            )
                        if "loss" in progress and progress["loss"] is not None:
                            job.loss = progress["loss"]



            # wait for the process to finish and get the return code
            return_code = process.wait()

            job.return_code = return_code
            job.process = None

            if return_code == 0:
                job.status = "completed"
            else:
                job.status = "failed"


    def status(self, job_id: str):
        return self.jobs.get(job_id)

    def get_logs(self, job_id: str):
        job = self.jobs.get(job_id)

        if job is None:
            return None

        if job.log_file is None:
            return ""

        if not job.log_file.exists():
            return ""

        return job.log_file.read_text()

    # Stop a running viewer process
    def stop_viewer(self, project_name: str) -> bool:
        for job in self.jobs.values():

            if job.process is None:
                continue

            if job.status != "running":
                continue

            if job.command is None:
                continue

            command_text = " ".join(job.command)

            # Make sure this is a Gaussian Splatting viewer process
            if "gaussian_splatting.viewer" not in command_text:
                continue

            # Make sure this viewer belongs to the requested project
            if project_name not in command_text:
                continue

            process = job.process

            # Check whether the process has already exited
            if process.poll() is not None:
                job.process = None
                return False

            # Ask the viewer process to terminate
            process.terminate()

            try:
                # Give it a few seconds to shut down cleanly
                process.wait(timeout=3)

            except subprocess.TimeoutExpired:
                # It did not terminate, so force kill it
                process.kill()
                process.wait()

            job.process = None
            job.return_code = process.returncode
            job.status = "stopped"

            return True

        return False
