from .archiver import Archiver
from .archiver_status import ArchiverMode, ArchiverProgress, ArchiverStatus
from .constants import DEFAULT_DICT_LENGTH
from .file_manager import FileManager


class Encoder(Archiver):
    """Кодировщик, который сжимает файл с помощью алгоритма LZW"""

    def __init__(self, file_path: str, dictionary: dict[str, int] | None = None) -> None:
        """Инициализация нового архиватора для указанного файла и переданного (опционально) словаря"""
        super().__init__(file_path)

        self._origin_file_path: str = file_path
        self._compressed_file_path: str = file_path.rsplit('.', 1)[0] + ".lzw"
        self._file_manager = FileManager(archiver=self, write_file=self._compressed_file_path)

        self._dictionary = dictionary or {chr(i): i for i in range(DEFAULT_DICT_LENGTH)}
        self._current_str: str = ""

    def run(self) -> ArchiverStatus:
        """Основной цикл работы архиватора. По окончании возвращает статус своей работы"""
        with open(file=self._origin_file_path, mode="r") as file:
            while True:
                symbol: str = file.read(1)
                if not symbol:
                    break
                code: int | None = self._get_code(symbol)
                if code is None:
                    continue
                self._file_manager.write_code(code)
                self._try_update_code_length()

            if self._current_str:
                self._file_manager.write_code(self._dictionary[self._current_str])

        self._file_manager.write_remaining_bits()
        return ArchiverStatus(ArchiverMode.ENCODER, ArchiverProgress.SUCCESS, self._file_name)

    def _try_update_code_length(self) -> None:
        """Динамически обновляет длину кода для лучшего сжатия"""
        if len(self._dictionary) > self._max_code:
            self.current_code_length += 1
            self._max_code = self._update_max_code()

    def _get_code(self, symbol: str) -> int | None:
        """По переданной подстроке возвращает уже существующий код или генерирует новый"""
        new_str: str = self._current_str + symbol

        if new_str in self._dictionary:
            self._current_str = new_str
            return None
        else:
            code = self._dictionary[self._current_str]
            self._dictionary[new_str] = len(self._dictionary)
            self._current_str = symbol
            return code
