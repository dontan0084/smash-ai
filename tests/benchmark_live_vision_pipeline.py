import sys
import time
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.vision import (
    CaptureVideoSource,
    LatestFrameSource,
    PlayerTracker,
    PlayerIdentityManager,
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

TRACKER_CONFIG = (
    ROOT_DIR
    / "configs"
    / "bytetrack_smash.yaml"
)


def main():

    source = CaptureVideoSource(
        device_index=1,
        width=1920,
        height=1080,
        fps=60.0,
    )

    latest = LatestFrameSource(source)

    tracker = PlayerTracker(
        model_path=MODEL_PATH,
        confidence_threshold=0.05,
        image_size=320,
        tracker=str(TRACKER_CONFIG),
    )

    identity = PlayerIdentityManager(
        max_missing_frames=15,
        max_match_distance_px=700.0,
    )

    latest.start()

    last_frame_number = -1

    processed = 0
    skipped = 0

    tracker_times = []
    identity_times = []

    print("Vision benchmark start")
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

            # ---------------------------
            # Tracker
            # ---------------------------

            t0 = time.perf_counter()

            tracks = tracker.track(
                frame.image
            )

            t1 = time.perf_counter()

            # ---------------------------
            # Identity
            # ---------------------------

            players = identity.update(
                tracks
            )

            t2 = time.perf_counter()

            tracker_times.append(
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

    average_tracker = (
        sum(tracker_times)
        / len(tracker_times)
    )

    average_identity = (
        sum(identity_times)
        / len(identity_times)
    )

    print()
    print("=== Headless Vision Benchmark ===")

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
        "Tracker:",
        f"{average_tracker * 1000:.2f} ms",
    )

    print(
        "Identity:",
        f"{average_identity * 1000:.3f} ms",
    )


if __name__ == "__main__":
    main()