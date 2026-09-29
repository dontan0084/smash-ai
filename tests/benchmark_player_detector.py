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

IMAGE_SIZE = (384, 640)

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

VAL_DIR = (
    ROOT_DIR
    / "datasets"
    / "player_detection"
    / "images"
    / "val"
)

PYTORCH_MODEL = (
    ROOT_DIR
    / "runs"
    / "player_detection"
    / "player_v3"
    / "weights"
    / "best.pt"
)

OPENVINO_MODEL = (
    ROOT_DIR
    / "runs"
    / "player_detection"
    / "player_v3"
    / "weights"
    / "best_openvino_model"
)


def benchmark(
    name: str,
    model_path: Path,
    images,
):

    detector = PlayerDetector(
        model_path=model_path,
        confidence_threshold=0.25,
        image_size=IMAGE_SIZE,
    )

    # ======================================
    # Warm-up
    # ======================================

    for image in images[:5]:
        detector.detect(image)

    # ======================================
    # Benchmark
    # ======================================

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

    print()
    print(f"=== {name} ===")
    print(
        f"images           : {len(images)}"
    )
    print(
        f"average          : "
        f"{average * 1000:.2f} ms"
    )
    print(
        f"estimated FPS    : {fps:.2f}"
    )
    print(
        f"total detections : "
        f"{total_detections}"
    )

    return average


def main():

    image_paths = sorted(
        VAL_DIR.glob("*.jpg")
    )

    if not image_paths:
        raise RuntimeError(
            "No validation images found"
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

    pytorch_time = benchmark(
        "PyTorch",
        PYTORCH_MODEL,
        images,
    )

    openvino_time = benchmark(
        "OpenVINO",
        OPENVINO_MODEL,
        images,
    )

    speedup = (
        pytorch_time
        / openvino_time
    )

    print()
    print("======================")
    print(
        f"OpenVINO speedup: "
        f"{speedup:.2f}x"
    )
    print("======================")


if __name__ == "__main__":
    main()