import csv
from pathlib import Path

import cv2

from src.vision.video_source import VideoSource


def sample_frames(
    source: VideoSource,
    output_dir: str | Path,
    every_n_frames: int = 30,
    max_saved_frames: int | None = None,
) -> int:

    if every_n_frames <= 0:
        raise ValueError(
            "every_n_frames must be greater than 0"
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_path = output_dir / "frames.csv"

    saved_count = 0

    with open(
        metadata_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow([
            "filename",
            "frame_number",
            "timestamp",
        ])

        while True:

            frame = source.read()

            if frame is None:
                break

            # 指定フレーム間隔で保存
            if (
                frame.frame_number
                % every_n_frames
                != 0
            ):
                continue

            filename = (
                f"frame_"
                f"{frame.frame_number:08d}.jpg"
            )

            image_path = (
                output_dir / filename
            )

            success = cv2.imwrite(
                str(image_path),
                frame.image,
            )

            if not success:
                raise RuntimeError(
                    f"Failed to save image: "
                    f"{image_path}"
                )

            writer.writerow([
                filename,
                frame.frame_number,
                f"{frame.timestamp:.6f}",
            ])

            saved_count += 1

            if (
                max_saved_frames is not None
                and saved_count >= max_saved_frames
            ):
                break

    return saved_count