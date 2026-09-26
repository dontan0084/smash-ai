from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class CameraState:
    x: float
    y: float
    zoom: float

    def __post_init__(self):

        if self.zoom <= 0:
            raise ValueError(
                "zoom must be greater than 0"
            )
    


@dataclass
class PlayerState:
    character: str

    x: float
    y: float

    vx: Optional[float] = None
    vy: Optional[float] = None

    percent: Optional[float] = None
    stocks: Optional[int] = None

    facing: Optional[str] = None
    grounded: Optional[bool] = None

    state: Optional[str] = None
    confidence: Optional[float] = None

    def __post_init__(self):

        if not self.character:
            raise ValueError(
                "character must not be empty"
            )

        if self.percent is not None and self.percent < 0:
            raise ValueError(
                "percent must be 0 or greater"
            )

        if self.stocks is not None and self.stocks < 0:
            raise ValueError(
                "stocks must be 0 or greater"
            )

        if (
            self.confidence is not None
            and not 0.0 <= self.confidence <= 1.0
        ):
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if (
            self.facing is not None
            and self.facing not in ("left", "right")
        ):
            raise ValueError(
                "facing must be 'left' or 'right'"
            )


@dataclass
class WorldState:
    timestamp: float
    frame: int
    stage: str

    camera: CameraState

    player1: PlayerState
    player2: PlayerState

    def __post_init__(self):

        if self.timestamp < 0:
            raise ValueError(
                "timestamp must be 0 or greater"
            )

        if self.frame < 0:
            raise ValueError(
                "frame must be 0 or greater"
            )

        if not self.stage:
            raise ValueError(
                "stage must not be empty"
            )

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            timestamp=data["timestamp"],
            frame=data["frame"],
            stage=data["stage"],

            camera=CameraState(**data["camera"]),

            player1=PlayerState(**data["player1"]),
            player2=PlayerState(**data["player2"]),
        )