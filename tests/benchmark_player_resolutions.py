import sys
import time
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import cv2

from src.vision.player_detector import (
    PlayerDetector,
)


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

MODEL_PATH = (
    ROOT_DIR
    / "runs"
    / "player_detection"
    / "player_v3"
    / "weights"
    / "best.pt"
)

VAL_DIR = (
    ROOT_DIR
    / "datasets"
    / "player_detection"
    / "images"
    / "val"
)

IMAGE_SIZES = [
    640,
    512,
    416,
    320,
]


def benchmark(
    image_size,
    images,
):

    detector = PlayerDetector(
        model_path=MODEL_PATH,
        confidence_threshold=0.25,
        image_size=image_size,
    )

    # warm-up
    for image in images[:5]:
        detector.detect(image)

    times = []
    total_detections = 0

    for image in images:

        start = time.perf_counter()

        detections = detector.detect(
            image
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        times.append(elapsed)

        total_detections += len(
            detections
        )

    average = (
        sum(times)
        / len(times)
    )

    fps = 1.0 / average

    return (
        average,
        fps,
        total_detections,
    )


def main():

    image_paths = sorted(
        VAL_DIR.glob("*.jpg")
    )

    images = []

    for path in image_paths:

        image = cv2.imread(
            str(path)
        )

        if image is None:
            raise RuntimeError(
                f"Could not read: {path}"
            )

        images.append(image)

    print(
        "Benchmark images:",
        len(images),
    )

    print()

    for image_size in IMAGE_SIZES:

        average, fps, detections = (
            benchmark(
                image_size,
                images,
            )
        )

        print(
            f"=== imgsz={image_size} ==="
        )

        print(
            f"average          : "
            f"{average * 1000:.2f} ms"
        )

        print(
            f"estimated FPS    : "
            f"{fps:.2f}"
        )

        print(
            f"total detections : "
            f"{detections}"
        )

        print()


if __name__ == "__main__":
    main()