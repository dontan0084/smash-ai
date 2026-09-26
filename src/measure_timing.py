import cv2
import time
import statistics

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG")
)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 60)

print(
    "Capture:",
    cap.get(cv2.CAP_PROP_FRAME_WIDTH),
    "x",
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
    "@",
    cap.get(cv2.CAP_PROP_FPS)
)

print("ウォームアップ中...")

warmup_start = time.perf_counter()

while time.perf_counter() - warmup_start < 3:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        cap.release()
        raise SystemExit

print("測定開始")

timestamps = []
start = time.perf_counter()

while True:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        break

    now = time.perf_counter()
    timestamps.append(now)

    if now - start >= 10:
        break

end = time.perf_counter()
cap.release()

intervals = [
    (timestamps[i] - timestamps[i - 1]) * 1000
    for i in range(1, len(timestamps))
]

elapsed = end - start
fps = len(timestamps) / elapsed

print()
print("取得フレーム数:", len(timestamps))
print(f"測定時間      : {elapsed:.3f} s")
print(f"実測FPS       : {fps:.2f}")
print(f"平均間隔      : {statistics.mean(intervals):.3f} ms")
print(f"中央値        : {statistics.median(intervals):.3f} ms")
print(f"最小間隔      : {min(intervals):.3f} ms")
print(f"最大間隔      : {max(intervals):.3f} ms")

print(f"20ms超え      : {sum(x > 20 for x in intervals)} 回")
print(f"25ms超え      : {sum(x > 25 for x in intervals)} 回")
print(f"30ms超え      : {sum(x > 30 for x in intervals)} 回")