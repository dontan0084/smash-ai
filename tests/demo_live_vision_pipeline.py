import sys
import time
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import cv2

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

        # 高速化した設定
        image_size=320,

        tracker=str(TRACKER_CONFIG),
    )

    identity = PlayerIdentityManager(
        max_missing_frames=15,
        max_match_distance_px=700.0,
    )

    latest.start()

    last_frame_number = -1

    processed_frames = 0
    skipped_frames = 0

    start_time = time.perf_counter()

    print("Live Vision Pipeline 起動")
    print("Qキーで終了")

    try:

        while True:

            frame = latest.get_latest()

            if frame is None:
                time.sleep(0.001)
                continue

            # 同じフレームを2回処理しない
            if (
                frame.frame_number
                == last_frame_number
            ):
                time.sleep(0.001)
                continue

            if last_frame_number >= 0:

                skipped_frames += max(
                    0,
                    frame.frame_number
                    - last_frame_number
                    - 1,
                )

            last_frame_number = (
                frame.frame_number
            )

            inference_start = (
                time.perf_counter()
            )

            tracks = tracker.track(
                frame.image
            )

            players = identity.update(
                tracks
            )

            inference_time = (
                time.perf_counter()
                - inference_start
            )

            processed_frames += 1

            elapsed = (
                time.perf_counter()
                - start_time
            )

            average_fps = (
                processed_frames / elapsed
            )

            current_fps = (
                1.0 / inference_time
                if inference_time > 0
                else 0.0
            )

            display = frame.image.copy()

            # Logical Playerを描画
            for player in players:

                if not player.visible:
                    continue

                if (
                    player.x1 is None
                    or player.y1 is None
                    or player.x2 is None
                    or player.y2 is None
                ):
                    continue

                cv2.rectangle(
                    display,
                    (player.x1, player.y1),
                    (player.x2, player.y2),
                    (0, 255, 0),
                    3,
                )

                text = (
                    f"P{player.logical_id} "
                    f"track={player.track_id} "
                    f"{player.confidence:.2f}"
                )

                cv2.putText(
                    display,
                    text,
                    (
                        player.x1,
                        max(
                            player.y1 - 10,
                            20,
                        ),
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

            info_lines = [
                f"Process FPS: {average_fps:.1f}",
                f"Instant FPS: {current_fps:.1f}",
                f"Capture frame: {frame.frame_number}",
                f"Capture received: {latest.received_frames}",
                f"Skipped: {skipped_frames}",
                f"Tracks: {len(tracks)}",
            ]

            for index, text in enumerate(
                info_lines
            ):
                cv2.putText(
                    display,
                    text,
                    (
                        20,
                        40 + index * 35,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 255),
                    2,
                )

            display = cv2.resize(
                display,
                (1280, 720),
            )

            cv2.imshow(
                "Live Vision Pipeline",
                display,
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:

        latest.close()
        cv2.destroyAllWindows()

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print()
    print("=== Vision Pipeline Result ===")
    print(
        "Processed frames:",
        processed_frames,
    )
    print(
        "Capture frames:",
        latest.received_frames,
    )
    print(
        "Skipped frames:",
        skipped_frames,
    )

    if elapsed > 0:
        print(
            "Processing FPS:",
            f"{processed_frames / elapsed:.2f}",
        )

    print("Live Vision Pipeline 終了")


if __name__ == "__main__":
    main()