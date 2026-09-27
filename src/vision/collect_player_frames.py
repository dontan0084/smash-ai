from datetime import datetime
from pathlib import Path

import cv2

from src.vision import CaptureVideoSource


EVERY_N_FRAMES = 12
MAX_IMAGES = 60

OUTPUT_ROOT = Path(
    "recordings/player_collection"
)


def main():

    session_name = datetime.now().strftime(
        "session_%Y%m%d_%H%M%S"
    )

    output_dir = (
        OUTPUT_ROOT
        / session_name
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    source = CaptureVideoSource(
        device_index=1,
        width=1920,
        height=1080,
        fps=60.0,
    )

    saved = 0

    print("データ収集開始")
    print("保存先:", output_dir)
    print()
    print(
        f"{EVERY_N_FRAMES}フレームに1枚、"
        f"最大{MAX_IMAGES}枚保存します"
    )

    try:

        while saved < MAX_IMAGES:

            frame = source.read()

            if frame is None:
                raise RuntimeError(
                    "Failed to read frame"
                )

            if (
                frame.frame_number
                % EVERY_N_FRAMES
                != 0
            ):
                continue

            filename = (
                f"frame_"
                f"{frame.frame_number:08d}.jpg"
            )

            path = (
                output_dir
                / filename
            )

            if not cv2.imwrite(
                str(path),
                frame.image,
            ):
                raise RuntimeError(
                    f"Could not save: {path}"
                )

            saved += 1

            print(
                f"\r保存: "
                f"{saved}/{MAX_IMAGES}",
                end="",
            )

    finally:
        source.close()

    print()
    print()
    print("収集完了")
    print("保存枚数:", saved)
    print("保存先:", output_dir)


if __name__ == "__main__":
    main()