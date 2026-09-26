import time
from collections.abc import Callable

from src.schemas.controller_state import ControllerState


class ActionRunner:

    def __init__(
        self,
        output_func: Callable[[ControllerState], None],
        hz: float = 60.0,
    ):
        if hz <= 0:
            raise ValueError(
                "hz must be greater than 0"
            )

        self.output_func = output_func
        self.hz = hz
        self.frame_interval = 1.0 / hz

        # 現在Switchへ送っている入力状態
        self.current_state = ControllerState()

    def run(
        self,
        states: list[ControllerState],
    ) -> None:

        if not states:
            return

        start_time = time.perf_counter()

        for frame_index, state in enumerate(states):

            target_time = (
                start_time
                + frame_index * self.frame_interval
            )

            self._wait_until(target_time)

            self.output_func(state)

            # 最後に送った入力を記憶
            self.current_state = state

        end_time = (
            start_time
            + len(states) * self.frame_interval
        )

        self._wait_until(end_time)

    def reset(self) -> None:

        neutral = ControllerState()

        self.output_func(neutral)

        self.current_state = neutral

    def _wait_until(
        self,
        target_time: float,
    ) -> None:

        while True:

            now = time.perf_counter()
            remaining = target_time - now

            if remaining <= 0:
                return

            time.sleep(
                min(remaining, 0.001)
            )