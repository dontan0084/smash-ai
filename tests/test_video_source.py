import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import cv2
import numpy as np

from src.vision.video_source import (
    FileVideoSource,
)


# ==========================================
# テスト動画を作る
# ==========================================

test_dir = Path("recordings")
test_dir.mkdir(exist_ok=True)

video_path = test_dir / "video_source_test.avi"


width = 320
height = 240
fps = 60
frames_to_create = 120


writer = cv2.VideoWriter(
    str(video_path),
    cv2.VideoWriter_fourcc(*"MJPG"),
    fps,
    (width, height),
)

assert writer.isOpened()


for i in range(frames_to_create):

    image = np.zeros(
        (height, width, 3),
        dtype=np.uint8,
    )

    writer.write(image)


writer.release()


# ==========================================
# FileVideoSourceで読む
# ==========================================

source = FileVideoSource(
    str(video_path)
)


frames = []

while True:

    frame = source.read()

    if frame is None:
        break

    frames.append(frame)


source.close()


# ==========================================
# チェック
# ==========================================

assert len(frames) == 120

assert frames[0].frame_number == 0
assert frames[1].frame_number == 1
assert frames[-1].frame_number == 119

assert abs(
    frames[0].timestamp - 0.0
) < 0.001

assert abs(
    frames[60].timestamp - 1.0
) < 0.001

assert frames[0].image.shape == (
    240,
    320,
    3,
)


print("Frames:", len(frames))
print("FPS:", source.fps)
print(
    "Frame 60 timestamp:",
    frames[60].timestamp,
)

print()
print("VideoSource test: OK")