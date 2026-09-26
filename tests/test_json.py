import sys
import json
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


# =====================================
# ダミーデータを作る
# =====================================

world_state = WorldState(
    timestamp=10.5,
    frame=630,
    stage="battlefield",

    camera=CameraState(
        x=0.0,
        y=0.0,
        zoom=1.0,
    ),

    player1=PlayerState(
        character="mario",
        x=-0.5,
        y=0.0,
        percent=50.0,
        stocks=3,
        facing="right",
        grounded=True,
        confidence=0.95,
    ),

    player2=PlayerState(
        character="pikachu",
        x=0.5,
        y=0.0,
        percent=80.0,
        stocks=2,
        facing="left",
        grounded=True,
        confidence=0.93,
    ),
)


action = ActionToken(
    action_type=ActionType.DASH,
    direction=Direction.RIGHT,
    strength=1.0,
    duration_frames=5,
)


controller = ControllerState(
    lx=1.0
)


# =====================================
# JSONに変換
# =====================================

data = {
    "world_state": world_state.to_dict(),
    "action": action.to_dict(),
    "controller": controller.to_dict(),
}


json_text = json.dumps(
    data,
    indent=2,
    ensure_ascii=False,
)


print("=== JSON ===")
print(json_text)


# =====================================
# ファイル保存
# =====================================

output_path = Path("recordings") / "schema_test.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        data,
        f,
        indent=2,
        ensure_ascii=False,
    )


print()
print("保存:", output_path)


# =====================================
# ファイル読み込み
# =====================================

with open(output_path, "r", encoding="utf-8") as f:
    loaded_data = json.load(f)


loaded_world_state = WorldState.from_dict(
    loaded_data["world_state"]
)

loaded_action = ActionToken.from_dict(
    loaded_data["action"]
)

loaded_controller = ControllerState.from_dict(
    loaded_data["controller"]
)


print()
print("=== 復元結果 ===")

print(loaded_world_state)
print(loaded_action)
print(loaded_controller)


# =====================================
# 元データと同じか確認
# =====================================

assert loaded_world_state == world_state
assert loaded_action == action
assert loaded_controller == controller


print()
print("JSON round-trip test: OK")