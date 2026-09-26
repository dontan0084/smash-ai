import cv2
import time

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
    cap.get(cv2.CAP_PROP_FPS),
)

# 起動直後の状態を測定に含めない
print("ウォームアップ中...")

warmup_start = time.perf_counter()

while time.perf_counter() - warmup_start < 2.0:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        cap.release()
        exit()

print("測定開始")

frame_count = 0
start = time.perf_counter()

while True:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        break

    frame_count += 1

    elapsed = time.perf_counter() - start

    if elapsed >= 10:
        break

fps = frame_count / elapsed

print(f"frames: {frame_count}")
print(f"time  : {elapsed:.3f}")
print(f"FPS   : {fps:.2f}")

cap.release()