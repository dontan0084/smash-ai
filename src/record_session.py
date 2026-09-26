import cv2
import pygame
import csv
import json
import time
import threading
from pathlib import Path
from datetime import datetime


RECORD_SECONDS = 10
CONTROLLER_HZ = 240

WIDTH = 1920
HEIGHT = 1080
FPS = 60


# =========================================================
# 保存先
# =========================================================

session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S")

session_dir = Path("recordings") / session_name
session_dir.mkdir(parents=True, exist_ok=True)

video_path = session_dir / "video.avi"
frames_csv_path = session_dir / "frames.csv"
controller_csv_path = session_dir / "controller.csv"
metadata_path = session_dir / "metadata.json"


# =========================================================
# キャプチャーボード
# =========================================================

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

cap.set(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG")
)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, FPS)

if not cap.isOpened():
    print("キャプチャーボードを開けませんでした")
    raise SystemExit


# =========================================================
# VideoWriter
# =========================================================

fourcc = cv2.VideoWriter_fourcc(*"MJPG")

writer = cv2.VideoWriter(
    str(video_path),
    fourcc,
    FPS,
    (WIDTH, HEIGHT)
)

if not writer.isOpened():
    print("動画ファイルを作成できませんでした")
    cap.release()
    raise SystemExit


# =========================================================
# コントローラー
# =========================================================

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("コントローラーが見つかりません")

    cap.release()
    writer.release()
    pygame.quit()

    raise SystemExit

joystick = pygame.joystick.Joystick(0)

print("Controller:", joystick.get_name())


# =========================================================
# ウォームアップ
# =========================================================

print("キャプチャーをウォームアップ中...")

warmup_start = time.perf_counter()

while time.perf_counter() - warmup_start < 2:
    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")

        cap.release()
        writer.release()
        pygame.quit()

        raise SystemExit


# =========================================================
# 記録用
# =========================================================

frame_records = []
controller_records = []

stop_event = threading.Event()

start_time = None


# =========================================================
# コントローラー記録スレッド
# =========================================================

def record_controller():

    poll_interval = 1.0 / CONTROLLER_HZ

    next_poll = start_time

    while not stop_event.is_set():

        now = time.perf_counter()

        if now < next_poll:
            time.sleep(min(next_poll - now, 0.001))
            continue

        pygame.event.pump()

        timestamp = time.perf_counter() - start_time

        axes = [
            joystick.get_axis(i)
            for i in range(joystick.get_numaxes())
        ]

        buttons = [
            joystick.get_button(i)
            for i in range(joystick.get_numbuttons())
        ]

        controller_records.append([
            timestamp,

            axes[0],       # lx
            axes[1],       # ly

            axes[2],       # rx
            axes[3],       # ry

            axes[4],       # zl
            axes[5],       # zr

            buttons[0],    # A
            buttons[1],    # B
            buttons[2],    # X
            buttons[3],    # Y

            buttons[9],    # L
            buttons[10],   # R

            buttons[6],    # +
            buttons[4],    # -

            buttons[7],    # 左スティック押し込み
            buttons[8],    # 右スティック押し込み
        ])

        next_poll += poll_interval


# =========================================================
# 同時記録開始
# =========================================================

print()
print("記録開始")

start_time = time.perf_counter()

controller_thread = threading.Thread(
    target=record_controller
)

controller_thread.start()

frame_number = 0


while True:

    ret, frame = cap.read()

    if not ret:
        print("フレーム取得失敗")
        break

    timestamp = time.perf_counter() - start_time

    # 動画保存
    writer.write(frame)

    # この動画フレームの取得時刻
    frame_records.append([
        frame_number,
        timestamp
    ])

    frame_number += 1

    if timestamp >= RECORD_SECONDS:
        break


end_time = time.perf_counter()

stop_event.set()

controller_thread.join()

cap.release()
writer.release()
pygame.quit()


# =========================================================
# frames.csv
# =========================================================

with open(frames_csv_path, "w", newline="") as f:

    csv_writer = csv.writer(f)

    csv_writer.writerow([
        "frame",
        "timestamp"
    ])

    for frame_number, timestamp in frame_records:

        csv_writer.writerow([
            frame_number,
            f"{timestamp:.6f}"
        ])


# =========================================================
# controller.csv
# =========================================================

with open(controller_csv_path, "w", newline="") as f:

    csv_writer = csv.writer(f)

    csv_writer.writerow([
        "timestamp",

        "lx",
        "ly",

        "rx",
        "ry",

        "zl",
        "zr",

        "a",
        "b",
        "x",
        "y",

        "l",
        "r",

        "plus",
        "minus",

        "lstick",
        "rstick",
    ])

    for row in controller_records:

        csv_writer.writerow([
            f"{row[0]:.6f}",
            *row[1:]
        ])


# =========================================================
# metadata.json
# =========================================================

duration = end_time - start_time

video_fps = len(frame_records) / duration
controller_rate = len(controller_records) / duration

metadata = {
    "duration_seconds": duration,

    "video": {
        "width": WIDTH,
        "height": HEIGHT,
        "requested_fps": FPS,
        "frames": len(frame_records),
        "measured_fps": video_fps,
        "codec": "MJPG",
        "file": "video.avi",
    },

    "controller": {
        "name": joystick.get_name(),
        "requested_hz": CONTROLLER_HZ,
        "samples": len(controller_records),
        "measured_hz": controller_rate,
        "file": "controller.csv",
    }
}

with open(metadata_path, "w") as f:
    json.dump(
        metadata,
        f,
        indent=2,
        ensure_ascii=False
    )


# =========================================================
# 結果
# =========================================================

print()
print("記録終了")
print(f"記録時間              : {duration:.3f} 秒")
print(f"映像フレーム数        : {len(frame_records)}")
print(f"映像実測FPS           : {video_fps:.2f}")
print(f"コントローラーサンプル: {len(controller_records)}")
print(f"コントローラー実測Hz  : {controller_rate:.2f}")
print()
print("保存先:", session_dir)