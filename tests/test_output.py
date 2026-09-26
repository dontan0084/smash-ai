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

from src.action_engine import (
    ActionEngine,
    ActionRunner,
)

from src.output import ConsoleOutput


engine = ActionEngine()

output = ConsoleOutput()

runner = ActionRunner(
    output_func=output.send,
    hz=60.0,
)


# =========================================
# DASH RIGHT
# =========================================

print("=== DASH RIGHT ===")

action = ActionToken(
    action_type=ActionType.DASH,
    direction=Direction.RIGHT,
    duration_frames=3,
)

states = engine.compile(action)

runner.run(states)


# =========================================
# SHORT HOP
# =========================================

print()
print("=== SHORT HOP ===")

action = ActionToken(
    action_type=ActionType.SHORT_HOP,
)

states = engine.compile(action)

runner.run(states)


print()
print("Output test: OK")