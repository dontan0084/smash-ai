from src.schemas.action import ActionToken
from src.schemas.controller_state import ControllerState

from src.action_engine.engine import ActionEngine
from src.action_engine.runner import ActionRunner
from src.output.base import ControllerOutput


class ControllerPipeline:

    def __init__(
        self,
        output: ControllerOutput,
        hz: float = 60.0,
    ):
        self.engine = ActionEngine()
        self.output = output

        self.runner = ActionRunner(
            output_func=self.output.send,
            hz=hz,
        )

    @property
    def current_state(self) -> ControllerState:
        return self.runner.current_state

    def execute(
        self,
        action: ActionToken,
    ) -> list[ControllerState]:

        states = self.engine.compile(
            action,
            previous_state=self.runner.current_state,
        )

        self.runner.run(states)

        return states

    def reset(self) -> None:
        self.runner.reset()

    def close(self) -> None:
        self.reset()
        self.output.close()