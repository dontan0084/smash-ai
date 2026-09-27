import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import cv2

from src.vision import (
    CaptureVideoSource,
    PlayerTracker,
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


tracker = PlayerTracker(
    model_path=MODEL_PATH,

    # Trackerへ低confidence候補も渡す
    confidence_threshold=0.05,

    image_size=640,
    tracker=str(
        ROOT_DIR
        / "configs"
        / "botsort_smash.yaml"
    ),
)


source = CaptureVideoSource(
    device_index=1,
    width=1920,
    height=1080,
    fps=60.0,
)


print("Player Tracking 起動")
print("Qキーで終了")


try:

    while True:

        frame = source.read()

        if frame is None:
            break

        players = tracker.track(
            frame.image
        )

        display = frame.image.copy()

        for player in players:

            cv2.rectangle(
                display,
                (player.x1, player.y1),
                (player.x2, player.y2),
                (0, 255, 0),
                3,
            )

            text = (
                f"ID {player.track_id} "
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

        cv2.putText(
            display,
            f"tracks: {len(players)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )

        display = cv2.resize(
            display,
            (1280, 720),
        )

        cv2.imshow(
            "Live Player Tracking",
            display,
        )

        if (
            cv2.waitKey(1) & 0xFF
            == ord("q")
        ):
            break


finally:

    source.close()
    cv2.destroyAllWindows()


print("Player Tracking 終了")