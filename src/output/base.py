from abc import ABC, abstractmethod

from src.schemas.controller_state import ControllerState


class ControllerOutput(ABC):

    @abstractmethod
    def send(
        self,
        state: ControllerState,
    ) -> None:
        pass

    def close(self) -> None:
        pass