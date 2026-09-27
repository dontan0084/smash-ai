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
# 最初の2人
# ==========================================

players = manager.update([
    make_player(10, 200),
    make_player(20, 1500),
])

assert players[0].visible
assert players[1].visible

assert players[0].track_id == 10
assert players[1].track_id == 20

print("Initial assignment: OK")


# ==========================================
# 移動
# ==========================================

players = manager.update([
    make_player(10, 300),
    make_player(20, 1400),
])

assert players[0].track_id == 10
assert players[1].track_id == 20

print("Movement tracking: OK")


# ==========================================
# Player 1を一瞬見失う
# ==========================================

players = manager.update([
    make_player(20, 1300),
])

assert players[0].visible is False
assert players[1].visible is True

print("Temporary loss: OK")


# ==========================================
# Player 1が別Tracker IDで再登場
# ==========================================

players = manager.update([
    make_player(99, 500),
    make_player(20, 1200),
])

# Tracker IDは変わったが、
# Logical Player 1のまま
assert players[0].visible is True
assert players[0].track_id == 99
assert players[0].logical_id == 1

assert players[1].track_id == 20
assert players[1].logical_id == 2

print("Re-identification after ID change: OK")


print()
print("Player Identity test: OK")