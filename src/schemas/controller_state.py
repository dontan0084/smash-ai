from dataclasses import dataclass, asdict


@dataclass
class ControllerState:

    lx: float = 0.0
    ly: float = 0.0

    rx: float = 0.0
    ry: float = 0.0

    a: bool = False
    b: bool = False
    x: bool = False
    y: bool = False

    l: bool = False
    r: bool = False
    zl: bool = False
    zr: bool = False

    plus: bool = False
    minus: bool = False

    lstick: bool = False
    rstick: bool = False

    def __post_init__(self):

        axes = {
            "lx": self.lx,
            "ly": self.ly,
            "rx": self.rx,
            "ry": self.ry,
        }

        for name, value in axes.items():
            if not -1.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between -1.0 and 1.0"
                )

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    