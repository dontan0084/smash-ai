import pygame
import csv
import time
from pathlib import Path

RECORD_SECONDS = 10
POLL_HZ = 240
POLL_INTERVAL = 1.0 / POLL_HZ

output_dir = Path("recordings")
output_dir.mkdir(exist_ok=True)

csv_path = output_dir / "controller.csv"

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("コントローラーが見つかりません")
    raise SystemExit

joystick = pygame.joystick.Joystick(0)

print("Controller:", joystick.get_name())
print(f"{POLL_HZ} Hzで{RECORD_SECONDS}秒間記録します")

records = []

start_time = time.perf_counter()
next_poll = start_time

while True:
    now = time.perf_counter()

    if now < next_poll:
        time.sleep(next_poll - now)
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

    records.append([
        timestamp,
        axes[0],   # lx
        axes[1],   # ly
        axes[2],   # rx
        axes[3],   # ry
        axes[4],   # ZL
        axes[5],   # ZR
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

    next_poll += POLL_INTERVAL

    if timestamp >= RECORD_SECONDS:
        break

pygame.quit()

with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
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

    for row in records:
        writer.writerow([
            f"{row[0]:.6f}",
            *row[1:]
        ])

duration = records[-1][0]
actual_hz = len(records) / duration

print()
print("記録終了")
print("サンプル数:", len(records))
print(f"記録時間: {duration:.3f} 秒")
print(f"実測レート: {actual_hz:.2f} Hz")
print("保存先:", csv_path)