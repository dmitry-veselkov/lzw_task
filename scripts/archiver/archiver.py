from abc import ABC, abstractmethod
from pathlib import Path

from .archiver_status import ArchiverStatus
from .constants import BITS_PER_CODE


class Archiver(ABC):
    """Бозовый класс архиватора, реализизации которого - конкретные режимы его работы"""

    def __init__(self, file_path: str) -> None:
        """Инициализация нового архиватора для переданного файла"""
        self._file_name = Path(file_path).stem
        self.current_code_length: int = BITS_PER_CODE
        self._max_code: int = self._update_max_code()

    @abstractmethod
    def run(self) -> ArchiverStatus:
        """Запуск архиватора в выбранном режиме"""
        pass

    def _update_max_code(self) -> int:
        """Обновление максимального кода, который может быть записан данным количеством бит"""
        return int(2**self.current_code_length) - 1
