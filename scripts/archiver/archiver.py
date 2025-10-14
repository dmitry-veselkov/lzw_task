import pathlib
from abc import ABC, abstractmethod
from pathlib import Path

from .archiver_status import ArchiverStatus
from .constants import BITS_PER_CODE


class Archiver(ABC):
    """Бозовый класс архиватора, реализизации которого - конкретные режимы его работы"""

    def __init__(self, path: str) -> None:
        """Инициализация нового архиватора для переданного файла"""
        (self._files, self._directory) = self._parse_files_path(path)
        self._meta_info = {file_path.name: 0 for file_path in self._files}
        self.current_code_length: int = BITS_PER_CODE
        self._max_code: int = self._update_max_code()

    @abstractmethod
    def run(self) -> ArchiverStatus:
        """Запуск архиватора в выбранном режиме"""
        pass

    def _update_max_code(self) -> int:
        """Обновление максимального кода, который может быть записан данным количеством бит"""
        return int(2 ** self.current_code_length) - 1

    @staticmethod
    def _parse_files_path(path: str) -> tuple[list[pathlib.Path], pathlib.Path]:
        """Разбор полученных из командной строки путей на список файлов и их директорию"""
        path = pathlib.Path(path)
        if path.is_file():
            return [path], path.parents[0]
        if path.is_dir():
            files = []
            for file in path.iterdir():
                if file.is_file():
                    files.append(file)
            return files, path

        raise FileNotFoundError(f"No such file or directory: '{path}'")
