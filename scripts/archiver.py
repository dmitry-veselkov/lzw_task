from abc import ABC, abstractmethod

from scripts.constants import BITS_PER_CODE


class Archiver(ABC):
    def __init__(self) -> None:
        self.current_code_length: int = BITS_PER_CODE
        self._max_code: int = self._update_max_code()

    @abstractmethod
    def run(self) -> None:
        pass

    def _update_max_code(self) -> int:
        return int(2**self.current_code_length) - 1
