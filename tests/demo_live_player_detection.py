import sys
import time
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import cv2

from src.vision import (
    CaptureVideoSource,
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
    / "player_v2"
    / "weights"
    / "best.pt"
)


detector = PlayerDetector(
    model_path=MODEL_PATH,
    confidence_threshold=0.25,
    image_size=640,
)


source = CaptureVideoSource(
    device_index=1,
    width=1920,
    height=1080,
    fps=60.0,
)


print("Player Detector 起動")
print("Qキーで終了")


last_time = time.perf_counter()


try:

    while True:

        frame = source.read()

        if frame is None:
            print("映像取得失敗")
            break


        # ======================================
        # fighter検出
        # ======================================

        detections = detector.detect(
            frame.image
        )


        # 表示用にコピー
        display = frame.image.copy()


        # ======================================
        # Bounding Box描画
        # ======================================

        for detection in detections:

            cv2.rectangle(
                display,
                (
                    detection.x1,
                    detection.y1,
                ),
                (
                    detection.x2,
                    detection.y2,
                ),
                (0, 255, 0),
                3,
            )

            text = (
                f"fighter "
                f"{detection.confidence:.2f}"
            )

            cv2.putText(
                display,
                text,
                (
                    detection.x1,
                    max(
                        detection.y1 - 10,
                        20,
                    ),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )


        # ======================================
        # 実測推論FPS
        # ======================================

        now = time.perf_counter()

        elapsed = now - last_time

        if elapsed > 0:
            processing_fps = 1.0 / elapsed
        else:
            processing_fps = 0.0

        last_time = now


        cv2.putText(
            display,
            f"Detection FPS: "
            f"{processing_fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            display,
            f"fighters: "
            f"{len(detections)}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )


        # 表示を縮小
        display = cv2.resize(
            display,
            (1280, 720),
        )


        cv2.imshow(
            "Live Player Detection",
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


print("Player Detector 終了")