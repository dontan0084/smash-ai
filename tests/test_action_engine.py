import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.schemas.action import (
    ActionToken,
    ActionType,
    Direction,
)

from src.action_engine import ActionEngine


engine = ActionEngine()


# ==============================================
# NO_OP
# ==============================================

action = ActionToken(
    action_type=ActionType.NO_OP,
)

states = engine.compile(action)

assert len(states) == 1

assert states[0].lx == 0.0
assert states[0].ly == 0.0
assert states[0].a is False

print("NO_OP: OK")


# ==============================================
# MOVE RIGHT
# ==============================================

action = ActionToken(
    action_type=ActionType.MOVE,
    direction=Direction.RIGHT,
    strength=0.5,
    duration_frames=3,
)

states = engine.compile(action)

assert len(states) == 3

for state in states:
    assert state.lx == 0.5
    assert state.ly == 0.0

print("MOVE RIGHT: OK")


# ==============================================
# MOVE LEFT
# ==============================================

action = ActionToken(
    action_type=ActionType.MOVE,
    direction=Direction.LEFT,
    strength=0.7,
)

states = engine.compile(action)

assert states[0].lx == -0.7
assert states[0].ly == 0.0

print("MOVE LEFT: OK")


# ==============================================
# MOVE UP
# ==============================================

action = ActionToken(
    action_type=ActionType.MOVE,
    direction=Direction.UP,
    strength=0.8,
)

states = engine.compile(action)

assert states[0].lx == 0.0
assert states[0].ly == -0.8

print("MOVE UP: OK")


# ==============================================
# MOVE DOWN
# ==============================================

action = ActionToken(
    action_type=ActionType.MOVE,
    direction=Direction.DOWN,
    strength=0.6,
)

states = engine.compile(action)

assert states[0].lx == 0.0
assert states[0].ly == 0.6

print("MOVE DOWN: OK")


# ==============================================
# DASH RIGHT
# ==============================================

action = ActionToken(
    action_type=ActionType.DASH,
    direction=Direction.RIGHT,
    duration_frames=5,
)

states = engine.compile(action)

assert len(states) == 5

for state in states:
    assert state.lx == 1.0
    assert state.ly == 0.0

print("DASH RIGHT: OK")


# ==============================================
# DASH LEFT
# ==============================================

action = ActionToken(
    action_type=ActionType.DASH,
    direction=Direction.LEFT,
)

states = engine.compile(action)

assert states[0].lx == -1.0
assert states[0].ly == 0.0

print("DASH LEFT: OK")

# ==============================================
# DASH RIGHT FROM HELD RIGHT
# ==============================================

from src.schemas.controller_state import ControllerState


previous_state = ControllerState(
    lx=0.5
)

action = ActionToken(
    action_type=ActionType.DASH,
    direction=Direction.RIGHT,
    duration_frames=3,
)

states = engine.compile(
    action,
    previous_state=previous_state,
)

# 最初にニュートラル
assert len(states) == 4

assert states[0].lx == 0.0

# その後フル入力
for state in states[1:]:
    assert state.lx == 1.0

print("DASH flick reset: OK")

# ==============================================
# 不正なDASH方向
# ==============================================

try:

    action = ActionToken(
        action_type=ActionType.DASH,
        direction=Direction.UP,
    )

    engine.compile(action)

except ValueError:
    print("Invalid DASH direction: OK")

else:
    raise AssertionError(
        "DASH + UP should raise ValueError"
    )

# ==============================================
# JUMP
# ==============================================

action = ActionToken(
    action_type=ActionType.JUMP,
)

states = engine.compile(action)

# Xを8フレーム押して、
# 最後に1フレーム離す
assert len(states) == 9

for state in states[:8]:
    assert state.x is True
    assert state.y is False

assert states[8].x is False
assert states[8].y is False

print("JUMP: OK")


# ==============================================
# JUMP 独自の保持時間
# ==============================================

action = ActionToken(
    action_type=ActionType.JUMP,
    duration_frames=4,
)

states = engine.compile(action)

assert len(states) == 5

for state in states[:4]:
    assert state.x is True

assert states[4].x is False

print("JUMP duration: OK")


# ==============================================
# SHORT HOP
# ==============================================

action = ActionToken(
    action_type=ActionType.SHORT_HOP,
)

states = engine.compile(action)

assert len(states) == 2

# 最初のフレーム
assert states[0].x is True
assert states[0].y is True

# 次のフレーム
assert states[1].x is False
assert states[1].y is False

print("SHORT HOP: OK")

# ==============================================
# ATTACK
# ==============================================

action = ActionToken(
    action_type=ActionType.ATTACK,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].a is True
assert states[1].a is False

print("ATTACK: OK")


# ==============================================
# SPECIAL NEUTRAL
# ==============================================

action = ActionToken(
    action_type=ActionType.SPECIAL,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].b is True
assert states[0].lx == 0.0
assert states[0].ly == 0.0

assert states[1].b is False

print("SPECIAL NEUTRAL: OK")


# ==============================================
# SPECIAL UP
# ==============================================

action = ActionToken(
    action_type=ActionType.SPECIAL,
    direction=Direction.UP,
)

states = engine.compile(action)

assert states[0].b is True
assert states[0].lx == 0.0
assert states[0].ly == -1.0

print("SPECIAL UP: OK")


# ==============================================
# GRAB
# ==============================================

action = ActionToken(
    action_type=ActionType.GRAB,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].zr is True
assert states[1].zr is False

print("GRAB: OK")


# ==============================================
# SHIELD
# ==============================================

action = ActionToken(
    action_type=ActionType.SHIELD,
    duration_frames=4,
)

states = engine.compile(action)

assert len(states) == 5

for state in states[:4]:
    assert state.zl is True

assert states[4].zl is False

print("SHIELD: OK")

# ==============================================
# TILT RIGHT
# ==============================================

action = ActionToken(
    action_type=ActionType.TILT,
    direction=Direction.RIGHT,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].rx == 1.0
assert states[0].ry == 0.0

assert states[1].rx == 0.0
assert states[1].ry == 0.0

print("TILT RIGHT: OK")


# ==============================================
# TILT UP
# ==============================================

action = ActionToken(
    action_type=ActionType.TILT,
    direction=Direction.UP,
)

states = engine.compile(action)

assert states[0].rx == 0.0
assert states[0].ry == -1.0

print("TILT UP: OK")


# ==============================================
# TILT NEUTRAL は不正
# ==============================================

try:

    action = ActionToken(
        action_type=ActionType.TILT,
        direction=Direction.NEUTRAL,
    )

    engine.compile(action)

except ValueError:
    print("Invalid TILT direction: OK")

else:
    raise AssertionError(
        "TILT + NEUTRAL should raise ValueError"
    )


# ==============================================
# AERIAL NEUTRAL
# ==============================================

action = ActionToken(
    action_type=ActionType.AERIAL,
    direction=Direction.NEUTRAL,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].a is True
assert states[1].a is False

print("AERIAL NEUTRAL: OK")


# ==============================================
# AERIAL LEFT
# ==============================================

action = ActionToken(
    action_type=ActionType.AERIAL,
    direction=Direction.LEFT,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].rx == -1.0
assert states[0].ry == 0.0

assert states[1].rx == 0.0
assert states[1].ry == 0.0

print("AERIAL LEFT: OK")


# ==============================================
# AERIAL DOWN
# ==============================================

action = ActionToken(
    action_type=ActionType.AERIAL,
    direction=Direction.DOWN,
)

states = engine.compile(action)

assert states[0].rx == 0.0
assert states[0].ry == 1.0

print("AERIAL DOWN: OK")

# ==============================================
# SMASH RIGHT
# ==============================================

action = ActionToken(
    action_type=ActionType.SMASH,
    direction=Direction.RIGHT,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].lx == 1.0
assert states[0].a is True

assert states[1].lx == 0.0
assert states[1].a is False

print("SMASH RIGHT: OK")


# ==============================================
# SMASH UP
# ==============================================

action = ActionToken(
    action_type=ActionType.SMASH,
    direction=Direction.UP,
)

states = engine.compile(action)

assert states[0].ly == -1.0
assert states[0].a is True

print("SMASH UP: OK")


# ==============================================
# SMASH FROM HELD RIGHT
# ==============================================

previous_state = ControllerState(
    lx=0.5
)

action = ActionToken(
    action_type=ActionType.SMASH,
    direction=Direction.RIGHT,
)

states = engine.compile(
    action,
    previous_state=previous_state,
)

assert len(states) == 3

# 一度ニュートラル
assert states[0].lx == 0.0

# その後スマッシュ
assert states[1].lx == 1.0
assert states[1].a is True

# 最後に離す
assert states[2].lx == 0.0
assert states[2].a is False

print("SMASH flick reset: OK")


# ==============================================
# DODGE
# ==============================================

action = ActionToken(
    action_type=ActionType.DODGE,
)

states = engine.compile(action)

assert len(states) == 3

assert states[0].zl is True
assert states[0].ly == 0.0

assert states[1].zl is True
assert states[1].ly == 1.0

assert states[2].zl is False
assert states[2].ly == 0.0

print("DODGE: OK")


# ==============================================
# ROLL RIGHT
# ==============================================

action = ActionToken(
    action_type=ActionType.ROLL,
    direction=Direction.RIGHT,
)

states = engine.compile(action)

assert len(states) == 3

assert states[0].zl is True
assert states[0].lx == 0.0

assert states[1].zl is True
assert states[1].lx == 1.0

assert states[2].zl is False
assert states[2].lx == 0.0

print("ROLL RIGHT: OK")


# ==============================================
# ROLL LEFT
# ==============================================

action = ActionToken(
    action_type=ActionType.ROLL,
    direction=Direction.LEFT,
)

states = engine.compile(action)

assert states[1].lx == -1.0

print("ROLL LEFT: OK")


# ==============================================
# DROP THROUGH
# ==============================================

action = ActionToken(
    action_type=ActionType.DROP_THROUGH,
)

states = engine.compile(action)

assert len(states) == 2

assert states[0].ly == 1.0
assert states[1].ly == 0.0

print("DROP THROUGH: OK")


# ==============================================
# DROP THROUGH FROM HELD DOWN
# ==============================================

previous_state = ControllerState(
    ly=0.5
)

states = engine.compile(
    ActionToken(
        action_type=ActionType.DROP_THROUGH,
    ),
    previous_state=previous_state,
)

assert len(states) == 3

assert states[0].ly == 0.0
assert states[1].ly == 1.0
assert states[2].ly == 0.0

print("DROP THROUGH flick reset: OK")



print()
print("Action Engine test: OK")