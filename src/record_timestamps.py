import cv2
import csv
import time
from pathlib import Path

output_dir = Path("recordings")
output_dir.mkdir(exist_ok=True)

csv_path = output_dir / "frame_timestamps.csv"

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG")
)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 60)

if not cap.isOpened():
    print("キャプチャーボードを開けませんでした")
    raise SystemExit

print("ウォームアップ中...")

warmup_start = time.perf_counter()

while time.perf_counter() - warmup_start < 2:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        cap.release()
        raise SystemExit

print("記録開始")

timestamps = []

start_time = time.perf_counter()

while True:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        break

    timestamp = time.perf_counter() - start_time

    timestamps.append(timestamp)

    if timestamp >= 10:
        break

cap.release()

# キャプチャ終了後にCSVへまとめて保存
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(["frame", "timestamp"])

    for frame_number, timestamp in enumerate(timestamps):
        writer.writerow([
            frame_number,
            f"{timestamp:.6f}"
        ])

elapsed = timestamps[-1]
fps = len(timestamps) / elapsed

print()
print("記録終了")
print("フレーム数:", len(timestamps))
print(f"記録時間: {elapsed:.3f} 秒")
print(f"実測FPS: {fps:.2f}")
print("保存先:", csv_path)