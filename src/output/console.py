from src.schemas.controller_state import ControllerState

from .base import ControllerOutput


class ConsoleOutput(ControllerOutput):

    def __init__(self):
        self.frame = 0

    def send(
        self,
        state: ControllerState,
    ) -> None:

        print(
            f"frame={self.frame:03d} "
            f"lx={state.lx:+.2f} "
            f"ly={state.ly:+.2f} "
            f"A={int(state.a)} "
            f"B={int(state.b)} "
            f"X={int(state.x)} "
            f"Y={int(state.y)}"
        )

        self.frame += 1