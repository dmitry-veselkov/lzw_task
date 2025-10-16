from abc import ABC, abstractmethod

from .archiver_status import ArchiverStatus
from .constants import BITS_PER_CODE


class Archiver(ABC):
    """
    Бозовый класс архиватора, реализизации которого - конкретные режимы его работы:
    - Encoder - кодировщик;
    - Decoder - декодировщик.
    """

    def __init__(self) -> None:
        """
        Инициализация нового архиватора со стартовыми значениями
        текущей и максимальной длины кода.
        """
        self.code_length: int = BITS_PER_CODE
        self._max_code: int = self._update_max_code()

    @abstractmethod
    def run(self) -> ArchiverStatus:
        """
        Запуск архиватора в выбранном режиме.
        """
        pass

    def _update_max_code(self) -> int:
        """
        Обновление максимального кода, который может быть записан данным количеством бит.
        """
        return int(2**self.code_length) - 1
