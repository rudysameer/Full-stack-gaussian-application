import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class ProcessInfo:
    job_id: str
    command: list[str]
    process: subprocess.Popen
    started_at: datetime
    log_file: Path


class ProcessManager:
    def __init__(self, log_directory: str = "logs/jobs"):
        self.processes: dict[str, ProcessInfo] = {}

        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)

    def start(self, command: list[str]) -> str:
        job_id = str(uuid.uuid4())

        log_file = self.log_directory / f"{job_id}.log"

        log_handle = open(log_file, "w")

        process = subprocess.Popen(
            command,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )

        self.processes[job_id] = ProcessInfo(
            job_id=job_id,
            command=command,
            process=process,
            started_at=datetime.now(),
            log_file=log_file,
        )

        return job_id

    def status(self, job_id: str) -> Optional[dict]:
        info = self.processes.get(job_id)

        if info is None:
            return None

        return_code = info.process.poll()

        if return_code is None:
            status = "running"
        elif return_code == 0:
            status = "completed"
        else:
            status = "failed"

        return {
            "job_id": info.job_id,
            "command": info.command,
            "pid": info.process.pid,
            "status": status,
            "return_code": return_code,
            "started_at": info.started_at.isoformat(),
            "log_file": str(info.log_file),
        }

    def get_logs(self, job_id: str) -> Optional[str]:
        info = self.processes.get(job_id)

        if info is None:
            return None

        if not info.log_file.exists():
            return ""

        return info.log_file.read_text()

    def stop(self, job_id: str) -> bool:
        info = self.processes.get(job_id)

        if info is None:
            return False

        if info.process.poll() is None:
            info.process.terminate()
            return True

        return False