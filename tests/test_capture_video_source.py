import sys
import time
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.vision import CaptureVideoSource


source = CaptureVideoSource(
    device_index=1,
    width=1920,
    height=1080,
    fps=60.0,
)


# ==========================================
# ウォームアップ
# ==========================================

print("ウォームアップ中...")

warmup_start = time.perf_counter()

while time.perf_counter() - warmup_start < 2.0:

    frame = source.read()

    if frame is None:
        raise RuntimeError(
            "Failed to read capture frame"
        )


# ==========================================
# 10秒測定
# ==========================================

print("測定開始")

frames = []

test_start = time.perf_counter()


while True:

    frame = source.read()

    if frame is None:
        raise RuntimeError(
            "Failed to read capture frame"
        )

    frames.append(frame)

    if (
        time.perf_counter()
        - test_start
        >= 10.0
    ):
        break


elapsed = (
    time.perf_counter()
    - test_start
)

source.close()


# ==========================================
# 結果
# ==========================================

actual_fps = len(frames) / elapsed

first = frames[0]
last = frames[-1]


print()
print("取得フレーム数:", len(frames))
print(f"測定時間      : {elapsed:.3f} 秒")
print(f"実測FPS       : {actual_fps:.2f}")

print()
print(
    "画像サイズ     :",
    first.image.shape,
)

print(
    "最初のframe   :",
    first.frame_number,
    f"{first.timestamp:.6f}",
)

print(
    "最後のframe   :",
    last.frame_number,
    f"{last.timestamp:.6f}",
)


assert len(frames) > 500

assert first.image.shape == (
    1080,
    1920,
    3,
)

assert actual_fps > 50.0


print()
print("CaptureVideoSource test: OK")