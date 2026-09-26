from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ActionType(str, Enum):
    NO_OP = "no_op"

    MOVE = "move"
    DASH = "dash"

    JUMP = "jump"
    SHORT_HOP = "short_hop"

    ATTACK = "attack"
    TILT = "tilt"
    SMASH = "smash"
    AERIAL = "aerial"
    SPECIAL = "special"

    GRAB = "grab"

    SHIELD = "shield"
    DODGE = "dodge"
    ROLL = "roll"

    DROP_THROUGH = "drop_through"


class Direction(str, Enum):
    NEUTRAL = "neutral"

    LEFT = "left"
    RIGHT = "right"

    UP = "up"
    DOWN = "down"


@dataclass
class ActionToken:
    action_type: ActionType
    direction: Direction = Direction.NEUTRAL
    strength: float = 1.0
    duration_frames: Optional[int] = None

    def __post_init__(self):

        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(
                "strength must be between 0.0 and 1.0"
            )

        if (
            self.duration_frames is not None
            and self.duration_frames <= 0
        ):
            raise ValueError(
                "duration_frames must be greater than 0"
            )

    def to_dict(self):
        return {
            "action_type": self.action_type.value,
            "direction": self.direction.value,
            "strength": self.strength,
            "duration_frames": self.duration_frames,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            action_type=ActionType(data["action_type"]),
            direction=Direction(data["direction"]),
            strength=data["strength"],
            duration_frames=data["duration_frames"],
        )