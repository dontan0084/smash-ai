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

from src.action_engine import ControllerPipeline
from src.output import ConsoleOutput


output = ConsoleOutput()

pipeline = ControllerPipeline(
    output=output,
    hz=60.0,
)


# ==============================================
# MOVE RIGHT
# ==============================================

print("=== MOVE RIGHT ===")

pipeline.execute(
    ActionToken(
        action_type=ActionType.MOVE,
        direction=Direction.RIGHT,
        strength=0.5,
        duration_frames=3,
    )
)


# ==============================================
# DASH RIGHT
# ==============================================

print()
print("=== DASH RIGHT ===")

pipeline.execute(
    ActionToken(
        action_type=ActionType.DASH,
        direction=Direction.RIGHT,
        duration_frames=3,
    )
)


# ==============================================
# SHORT HOP
# ==============================================

print()
print("=== SHORT HOP ===")

pipeline.execute(
    ActionToken(
        action_type=ActionType.SHORT_HOP,
    )
)


# ==============================================
# UP SPECIAL
# ==============================================

print()
print("=== UP SPECIAL ===")

pipeline.execute(
    ActionToken(
        action_type=ActionType.SPECIAL,
        direction=Direction.UP,
    )
)


# ==============================================
# 終了
# ==============================================

pipeline.close()