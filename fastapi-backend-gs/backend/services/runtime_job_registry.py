class RuntimeJobRegistry:
    def __init__(self):
        self.jobs = {}

    def register(
        self,
        project_name: str,
        operation: str,
        job_id: str,
        iteration: int | None = None,
    ):
        self.jobs[project_name, operation] = {
            "job_id": job_id,
            "iteration": iteration,
        }

    def get(
        self,
        project_name: str,
        operation: str,
    ):
        return self.jobs.get(
            (project_name, operation)
        )

    def remove(
        self,
        project_name: str,
        operation: str,
    ):
        self.jobs.pop(
            (project_name, operation),
            None,
        )