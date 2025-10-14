from typing import TextIO

from .archiver import Archiver
from .archiver_status import ArchiverMode, ArchiverProgress, ArchiverStatus
from .constants import DEFAULT_DICT_LENGTH
from .file_manager import FileManager
from .crc import CRC32


class Encoder(Archiver):
    """
    Кодировщик, который сжимает файл с помощью алгоритма LZW

    Ход работы кодировищка:
    1. Получить список файлов
    2. Закодировать каждый файл, параллельно высчитывая контрольную сумму и размер каждого сжатого файла
    3. Дописать в конец файла: контрольную сумму, объем мета-информации и саму мета-информацию:
        для каждого файла указать название и размер сжатой информации.
    """

    def __init__(self, path: str, dictionary: dict[str, int] | None = None) -> None:
        """Инициализация нового архиватора для указанного файла и переданного (опционально) словаря"""
        super().__init__(path)
        self._compressed_file_path: str = self._directory / 'pupupu.lzw'

        self._file_manager = FileManager(archiver=self, write_file=self._compressed_file_path)
        self._crc = CRC32()

        self._dictionary = dictionary or {chr(i): i for i in range(DEFAULT_DICT_LENGTH)}
        self._current_str: str = ""

    def run(self) -> ArchiverStatus:
        """Основной цикл работы архиватора. По окончании возвращает статус своей работы"""
        for file_path in self._files:
            with open(file=file_path, mode="r", encoding='utf-8') as file:
                self._endode_file(file, file_path.name)
            self._file_manager.write_remaining_bits()
            self._meta_info[file_path.name] += 8
            self._current_str = ""
            self._file_manager.reset()

        checksum = self._crc.get_checksum()
        print(checksum)
        self._file_manager.write_footer(checksum, self._meta_info)
        return ArchiverStatus(ArchiverMode.ENCODER, ArchiverProgress.SUCCESS)

    def _endode_file(self, file: TextIO, name: str) -> None:
        while True:
            symbol: str = file.read(1)
            if not symbol:
                break
            self._crc.update_checksum(symbol.encode())
            code: int | None = self._get_code(symbol)
            if code is None:
                continue
            self._file_manager.write_code(code)
            self._meta_info[name] += self.current_code_length
            self._try_update_code_length()

        if self._current_str:
            self._file_manager.write_code(self._dictionary[self._current_str])

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
