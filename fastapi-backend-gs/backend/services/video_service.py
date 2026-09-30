from pathlib import Path
import shutil
import cv2


class VideoService:

    def __init__(self, data_directory: str = "data"):
        self.data_directory = Path(data_directory)

    def process_video(
        self,
        project_name: str,
        video_file,
        frame_skip: int = 15,
    ) -> int:

        project_directory = (
            self.data_directory / project_name
        )

        if project_directory.exists():
            raise ValueError(
                "Project already exists"
            )

        input_directory = (
            project_directory / "input"
        )

        input_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Save uploaded video temporarily
        video_name = Path(
            video_file.filename
        ).name

        video_path = (
            project_directory / video_name
        )

        with video_path.open("wb") as file:
            shutil.copyfileobj(
                video_file.file,
                file,
            )

        # Open video
        cap = cv2.VideoCapture(
            str(video_path)
        )

        if not cap.isOpened():
            raise ValueError(
                "Could not open uploaded video"
            )

        frame_count = 0
        saved_count = 0

        while True:
            success, frame = cap.read()

            if not success:
                break

            if frame_count % frame_skip == 0:

                frame_name = (
                    f"frame_{saved_count:04d}.jpg"
                )

                frame_path = (
                    input_directory / frame_name
                )

                cv2.imwrite(
                    str(frame_path),
                    frame,
                )

                saved_count += 1

            frame_count += 1

        cap.release()

        if saved_count == 0:
            raise ValueError(
                "No frames could be extracted from video"
            )

        return saved_count