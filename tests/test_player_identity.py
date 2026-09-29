import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.vision.player_tracker import TrackedPlayer
from src.vision.player_identity import (
    PlayerIdentityManager,
)


def make_player(
    track_id,
    center_x,
    center_y=500,
):
    return TrackedPlayer(
        track_id=track_id,
        x1=center_x - 25,
        y1=center_y - 50,
        x2=center_x + 25,
        y2=center_y + 50,
        confidence=0.9,
    )


manager = PlayerIdentityManager()


# ==========================================
# frame 100
# 最初の2人
# ==========================================

players = manager.update(
    [
        make_player(10, 200),
        make_player(20, 1500),
    ],
    frame_number=100,
)

assert players[0].visible
assert players[1].visible

assert players[0].track_id == 10
assert players[1].track_id == 20

assert players[0].logical_id == 1
assert players[1].logical_id == 2

print("Initial assignment: OK")


# ==========================================
# frame 103
# 3フレーム後に移動
# ==========================================

players = manager.update(
    [
        make_player(10, 300),
        make_player(20, 1400),
    ],
    frame_number=103,
)

assert players[0].track_id == 10
assert players[1].track_id == 20

assert players[0].visible
assert players[1].visible

print("Movement tracking: OK")


# ==========================================
# 速度計算の確認
#
# P1:
# x=200 → 300
# 3 frameで100px移動
#
# vx = 100 / 3
# ==========================================

expected_vx_p1 = 100 / 3

assert abs(
    players[0].vx
    - expected_vx_p1
) < 0.001

expected_vx_p2 = -100 / 3

assert abs(
    players[1].vx
    - expected_vx_p2
) < 0.001

print("Frame-aware velocity: OK")


# ==========================================
# frame 106
# Player 1を一瞬見失う
# ==========================================

players = manager.update(
    [
        make_player(20, 1300),
    ],
    frame_number=106,
)

assert players[0].visible is False
assert players[1].visible is True

assert players[0].missing_frames == 3

print("Temporary loss: OK")


# ==========================================
# frame 109
# Player 1が別Tracker IDで再登場
#
# track_id:
# 10 → 99
#
# ただしLogical PlayerはP1のまま
# ==========================================

players = manager.update(
    [
        make_player(99, 500),
        make_player(20, 1200),
    ],
    frame_number=109,
)

assert players[0].visible is True
assert players[0].track_id == 99
assert players[0].logical_id == 1

assert players[1].visible is True
assert players[1].track_id == 20
assert players[1].logical_id == 2

print("Re-identification after ID change: OK")

# ==========================================
# 足元座標
# ==========================================

p1 = players[0]

assert p1.foot_x == 500
assert p1.foot_y == 550

print("Foot position: OK")

print()
print("Player Identity test: OK")
