import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.schemas.action import (
    ActionToken,
    ActionType,
)

from src.schemas.controller_state import ControllerState

from src.schemas.world_state import (
    CameraState,
    PlayerState,
    WorldState,
)


def expect_value_error(func):

    try:
        func()

    except ValueError as e:
        print("OK:", e)
        return

    raise AssertionError(
        "ValueErrorが発生するはずでした"
    )


# ======================================
# ActionToken
# ======================================

expect_value_error(
    lambda: ActionToken(
        action_type=ActionType.DASH,
        strength=2.0,
    )
)

expect_value_error(
    lambda: ActionToken(
        action_type=ActionType.DASH,
        duration_frames=0,
    )
)


# ======================================
# ControllerState
# ======================================

expect_value_error(
    lambda: ControllerState(
        lx=1.5
    )
)


# ======================================
# CameraState
# ======================================

expect_value_error(
    lambda: CameraState(
        x=0.0,
        y=0.0,
        zoom=0.0,
    )
)


# ======================================
# PlayerState
# ======================================

expect_value_error(
    lambda: PlayerState(
        character="mario",
        x=0.0,
        y=0.0,
        percent=-10,
    )
)

expect_value_error(
    lambda: PlayerState(
        character="mario",
        x=0.0,
        y=0.0,
        confidence=1.5,
    )
)


# ======================================
# 正常データ
# ======================================

controller = ControllerState(
    lx=1.0,
    ly=-1.0,
)

player1 = PlayerState(
    character="mario",
    x=-0.5,
    y=0.0,
    percent=50.0,
    stocks=3,
    confidence=0.95,
)

player2 = PlayerState(
    character="pikachu",
    x=0.5,
    y=0.0,
    percent=80.0,
    stocks=2,
    confidence=0.93,
)

world = WorldState(
    timestamp=10.5,
    frame=630,
    stage="battlefield",

    camera=CameraState(
        x=0.0,
        y=0.0,
        zoom=1.0,
    ),

    player1=player1,
    player2=player2,
)


print()
print("Validation test: OK")