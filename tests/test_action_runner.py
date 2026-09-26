import sys
import time
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


# ==========================================
# テスト用の出力先
# ==========================================

received_states = []


def mock_output(state):
    received_states.append(state)


engine = ActionEngine()

runner = ActionRunner(
    output_func=mock_output,
    hz=60.0,
)


# ==========================================
# MOVEを6フレーム実行
# ==========================================

action = ActionToken(
    action_type=ActionType.MOVE,
    direction=Direction.RIGHT,
    strength=0.5,
    duration_frames=6,
)

states = engine.compile(action)

start = time.perf_counter()

runner.run(states)

elapsed = time.perf_counter() - start


assert len(received_states) == 6

for state in received_states:
    assert state.lx == 0.5
    assert state.ly == 0.0


expected_seconds = 6 / 60.0


print("受信フレーム数:", len(received_states))
print(f"実測時間        : {elapsed:.4f} 秒")
print(f"理論時間        : {expected_seconds:.4f} 秒")


# Windowsのスケジューリング誤差を考慮して
# 厳密一致ではなく余裕を持たせる
assert abs(
    elapsed - expected_seconds
) < 0.05


print("MOVE timing: OK")


# ==========================================
# SHORT HOP
# ==========================================

received_states.clear()

action = ActionToken(
    action_type=ActionType.SHORT_HOP,
)

states = engine.compile(action)

runner.run(states)


assert len(received_states) == 2

# 1フレーム目
assert received_states[0].x is True
assert received_states[0].y is True

# 2フレーム目
assert received_states[1].x is False
assert received_states[1].y is False


print("SHORT HOP sequence: OK")

# ==========================================
# current_state
# ==========================================

received_states.clear()

action = ActionToken(
    action_type=ActionType.MOVE,
    direction=Direction.RIGHT,
    strength=0.5,
    duration_frames=2,
)

states = engine.compile(
    action,
    previous_state=runner.current_state,
)

runner.run(states)

assert runner.current_state.lx == 0.5
assert runner.current_state.ly == 0.0

print("Current state tracking: OK")


# ==========================================
# Reset
# ==========================================

runner.reset()

assert runner.current_state.lx == 0.0
assert runner.current_state.ly == 0.0

print("Runner reset: OK")

print()
print("Action Runner test: OK")