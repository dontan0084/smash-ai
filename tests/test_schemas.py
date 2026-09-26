import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from src.schemas.world_state import (
    CameraState,
    PlayerState,
    WorldState,
)

from src.schemas.action import (
    ActionToken,
    ActionType,
    Direction,
)

from src.schemas.controller_state import ControllerState


camera = CameraState(
    x=0.0,
    y=0.0,
    zoom=1.0
)

player1 = PlayerState(
    character="mario",
    x=-0.5,
    y=0.0,
    percent=50.0,
    stocks=3,
    facing="right",
    grounded=True,
    confidence=0.95
)

player2 = PlayerState(
    character="pikachu",
    x=0.5,
    y=0.0,
    percent=80.0,
    stocks=2,
    facing="left",
    grounded=True,
    confidence=0.93
)

world_state = WorldState(
    timestamp=10.5,
    frame=630,
    stage="battlefield",
    camera=camera,
    player1=player1,
    player2=player2
)

action = ActionToken(
    action_type=ActionType.DASH,
    direction=Direction.RIGHT,
    strength=1.0,
    duration_frames=5
)

controller = ControllerState(
    lx=1.0
)


print("=== WorldState ===")
print(world_state)

print()
print("=== ActionToken ===")
print(action)

print()
print("=== ControllerState ===")
print(controller)

print()
print("Phase 0 schema test: OK")