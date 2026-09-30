import re


class TrainingProgressParser:
    PATTERN = re.compile(
        r"Training progress:\s+(\d+)%.*?\|\s*(\d+)/(\d+)"
        r".*?Loss=([0-9.]+)"
    )

    def parse(self, line: str) -> dict | None:
        match = self.PATTERN.search(line)

        if not match:
            return None

        progress = float(match.group(1))
        current_iteration = int(match.group(2))
        target_iteration = int(match.group(3))
        loss = None

        if match.group(4) is not None:
            loss = float(match.group(4))

        return {
            "progress": progress,
            "current_iteration": current_iteration,
            "target_iteration": target_iteration,
            "loss": loss
        }