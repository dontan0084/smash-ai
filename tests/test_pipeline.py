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

from src.schemas.controller_state import ControllerState

from src.output.base import ControllerOutput
from src.action_engine import ControllerPipeline


# ==============================================
# テスト用Output
# ==============================================

class MockOutput(ControllerOutput):

    def __init__(self):
        self.received = []
        self.closed = False

    def send(
        self,
        state: ControllerState,
    ) -> None:
        self.received.append(state)

    def close(self) -> None:
        self.closed = True


# ==============================================
# Pipeline作成
# ==============================================

output = MockOutput()

pipeline = ControllerPipeline(
    output=output,
    hz=60.0,
)


# ==============================================
# MOVE RIGHT
# ==============================================

action = ActionToken(
    action_type=ActionType.MOVE,
    direction=Direction.RIGHT,
    strength=0.5,
    duration_frames=3,
)

states = pipeline.execute(action)

assert len(states) == 3
assert len(output.received) == 3

for state in states:
    assert state.lx == 0.5
    assert state.ly == 0.0

assert pipeline.current_state.lx == 0.5

print("MOVE pipeline: OK")


# ==============================================
# DASH RIGHT
#
# 直前が lx=0.5 なので
# neutral → full right
# になるはず
# ==============================================

output.received.clear()

action = ActionToken(
    action_type=ActionType.DASH,
    direction=Direction.RIGHT,
    duration_frames=2,
)

states = pipeline.execute(action)

assert len(states) == 3

assert states[0].lx == 0.0
assert states[1].lx == 1.0
assert states[2].lx == 1.0

assert len(output.received) == 3

assert pipeline.current_state.lx == 1.0

print("Previous state pipeline: OK")


# ==============================================
# SHORT HOP
# ==============================================

output.received.clear()

action = ActionToken(
    action_type=ActionType.SHORT_HOP,
)

states = pipeline.execute(action)

assert len(states) == 2

assert states[0].x is True
assert states[0].y is True

assert states[1].x is False
assert states[1].y is False

assert pipeline.current_state == ControllerState()

print("SHORT HOP pipeline: OK")


# ==============================================
# SMASH LEFT
# ==============================================

output.received.clear()

action = ActionToken(
    action_type=ActionType.SMASH,
    direction=Direction.LEFT,
)

states = pipeline.execute(action)

assert states[0].lx == -1.0
assert states[0].a is True

assert states[-1] == ControllerState()

print("SMASH pipeline: OK")


# ==============================================
# RESET
# ==============================================

pipeline.execute(
    ActionToken(
        action_type=ActionType.MOVE,
        direction=Direction.RIGHT,
        duration_frames=1,
    )
)

assert pipeline.current_state.lx == 1.0

pipeline.reset()

assert pipeline.current_state == ControllerState()

print("Pipeline reset: OK")


# ==============================================
# CLOSE
# ==============================================

pipeline.close()

assert output.closed is True
assert pipeline.current_state == ControllerState()

print("Pipeline close: OK")


print()
print("Controller Pipeline test: OK")