import sys
import time
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.vision import (
    CaptureVideoSource,
    LatestFrameSource,
)


source = CaptureVideoSource(
    device_index=1,
    width=1920,
    height=1080,
    fps=60.0,
)

latest = LatestFrameSource(
    source
)

latest.start()

print(
    "LatestFrameSource test start"
)

time.sleep(2.0)

first = latest.get_latest()

if first is None:
    raise RuntimeError(
        "No frame received"
    )

print(
    "First frame:",
    first.frame_number,
)

# Detectorなどの重い処理を想定
time.sleep(1.0)

second = latest.get_latest()

if second is None:
    raise RuntimeError(
        "No second frame"
    )

print(
    "Second frame:",
    second.frame_number,
)

difference = (
    second.frame_number
    - first.frame_number
)

print(
    "Frame difference:",
    difference,
)

print(
    "Capture received:",
    latest.received_frames,
)

latest.close()

assert difference >= 40

print()
print(
    "LatestFrameSource test: OK"
)