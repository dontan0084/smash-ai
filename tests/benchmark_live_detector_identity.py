import sys
import time
import os
import torch
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.vision import (
    CaptureVideoSource,
    LatestFrameSource,
    PlayerDetector,
    PlayerIdentityManager,
)

from src.vision.player_tracker import (
    TrackedPlayer,
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


def main():

    source = CaptureVideoSource(
        device_index=1,
        width=1920,
        height=1080,
        fps=60.0,
    )

    latest = LatestFrameSource(source)

    TORCH_THREADS = int(
        os.environ.get(
            "TORCH_THREADS",
            torch.get_num_threads(),
        )
    )

    torch.set_num_threads(
        TORCH_THREADS
    )

    print(
        "PyTorch threads:",
        torch.get_num_threads(),
    )

    detector = PlayerDetector(
        model_path=MODEL_PATH,
        confidence_threshold=0.25,
        image_size=320,
    )

    identity = PlayerIdentityManager(
        max_missing_frames=15,
        max_match_distance_px=700.0,
    )

    latest.start()

    last_frame_number = -1

    processed = 0
    skipped = 0

    detector_times = []
    identity_times = []

    print("Detector + Identity benchmark")
    print("20秒間計測します")

    start = time.perf_counter()

    try:

        while (
            time.perf_counter() - start
            < 20.0
        ):

            frame = latest.get_latest()

            if frame is None:
                time.sleep(0.001)
                continue

            if (
                frame.frame_number
                == last_frame_number
            ):
                continue

            if last_frame_number >= 0:

                skipped += max(
                    0,
                    frame.frame_number
                    - last_frame_number
                    - 1,
                )

            last_frame_number = (
                frame.frame_number
            )

            # =========================
            # Detector
            # =========================

            t0 = time.perf_counter()

            detections = detector.detect(
                frame.image
            )

            t1 = time.perf_counter()

            # =========================
            # Detection → Observation
            # =========================

            observations = []

            for detection in detections:

                observations.append(
                    TrackedPlayer(
                        track_id=None,

                        x1=int(detection.x1),
                        y1=int(detection.y1),
                        x2=int(detection.x2),
                        y2=int(detection.y2),

                        confidence=(
                            detection.confidence
                        ),
                    )
                )

            # =========================
            # Logical identity
            # =========================

            players = identity.update(
                observations,
                frame_number=frame.frame_number,
            )

            t2 = time.perf_counter()

            detector_times.append(
                t1 - t0
            )

            identity_times.append(
                t2 - t1
            )

            processed += 1

    finally:

        latest.close()

    elapsed = (
        time.perf_counter()
        - start
    )

    avg_detector = (
        sum(detector_times)
        / len(detector_times)
    )

    avg_identity = (
        sum(identity_times)
        / len(identity_times)
    )

    print()
    print(
        "=== Detector + Identity Result ==="
    )

    print(
        "Processed frames:",
        processed,
    )

    print(
        "Capture frames:",
        latest.received_frames,
    )

    print(
        "Skipped frames:",
        skipped,
    )

    print(
        "Total FPS:",
        f"{processed / elapsed:.2f}",
    )

    print(
        "Detector:",
        f"{avg_detector * 1000:.2f} ms",
    )

    print(
        "Identity:",
        f"{avg_identity * 1000:.3f} ms",
    )


if __name__ == "__main__":
    main()