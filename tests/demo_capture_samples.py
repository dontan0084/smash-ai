import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.vision import (
    CaptureVideoSource,
    sample_frames,
)


source = CaptureVideoSource(
    device_index=1,
    width=1920,
    height=1080,
    fps=60.0,
)


print("Switch映像から画像を抽出します")
print("30フレームに1枚保存します")


try:

    saved = sample_frames(
        source=source,
        output_dir="recordings/sample_frames",
        every_n_frames=30,
        max_saved_frames=20,
    )

finally:
    source.close()


print()
print("保存枚数:", saved)
print(
    "保存先:",
    "recordings/sample_frames",
)

print()
print("Frame sampling: OK")