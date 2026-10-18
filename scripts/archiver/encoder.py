import hashlib
import os
import pathlib
from typing import TextIO

from .archiver import Archiver
from .archiver_status import ArchiverMode, ArchiverStatus
from .constants import DEFAULT_DICT_LENGTH
from .crc import CRC32
from .file_manager import FileManager
from .meta_info import MetaInfo, Password


class Encoder(Archiver):
    """
    Кодировщик, сжимающий файл(-ы) с помощью алгоритма LZW
    """

    def __init__(
        self,
        path: str,
        archive_name: str,
        password: str | None,
        dictionary: dict[str, int] | None = None,
    ) -> None:
        """
        Инициализация нового архиватора для указанного файла (директории файлов).
        Обработка полученного пути, создание начального словаря и подключение
        алгоритма для проверки целостности.
        """
        super().__init__()

        self._file_manager = FileManager()
        self._crc = CRC32()

        (self._files, self._directory) = FileManager.get_files_with_dir(path)
        if archive_name == "" and len(self._files) == 1:
            archive_name = self._files[0].stem
        self._compressed_file_path = self._directory / f'{archive_name}.lzw'

        salt = os.urandom(16)
        self._password = self._get_password(password, salt)
        self._meta_info = self._get_meta_info(self._password, salt, self._files)

        self._dictionary = dictionary or {chr(i): i for i in range(DEFAULT_DICT_LENGTH)}
        self._current_str: str = ""

    def run(self) -> ArchiverStatus:
        """
        Основной цикл работы архиватора. Сжимает каждый файл, а затем
        вызывает метод для записи в конец файла мета-информации: контрольной суммы,
        названий исходных файлов и пр.
        """
        for file_path in self._files:
            with open(file=file_path, mode="r", encoding='utf-8') as file:
                self._endode_file(file, file_path.name)
            self._current_str = ""
            self._file_manager.reset()

        checksum = self._crc.get_checksum()
        self._file_manager.write_footer(self._compressed_file_path, checksum, self._meta_info)
        return ArchiverStatus(ArchiverMode.ENCODER)

    def _endode_file(self, file: TextIO, name: str) -> None:
        """
        Записывает в архив сжатое представление переданного файла, параллельно
        высчитывая контрольную сумму и размер сжатой информации.
        """
        while True:
            symbol: str = file.read(1)
            if not symbol:
                break
            self._crc.update_checksum(symbol.encode())
            code: int | None = self._get_code(symbol)
            if code is None:
                continue
            self._file_manager.write_code(self._compressed_file_path, code, self.code_length)
            self._meta_info.files[name] += self.code_length
            self._try_update_code_length()

        if self._current_str:
            code = self._dictionary[self._current_str]
            self._file_manager.write_code(self._compressed_file_path, code, self.code_length)

        self._file_manager.write_remaining_bits(self._compressed_file_path)
        self._meta_info.files[name] += 8

    def _try_update_code_length(self) -> None:
        """
        Реализация механизма обновления длины кода для лучшего сжатия
        """
        if len(self._dictionary) > self._max_code:
            self.code_length += 1
            self._max_code = self._update_max_code()

    def _get_code(self, symbol: str) -> int | None:
        """
        Получение по переданной строке уже существующего кода или генерация нового
        """
        new_str: str = self._current_str + symbol

        if new_str in self._dictionary:
            self._current_str = new_str
            return None
        else:
            code = self._dictionary[self._current_str]
            self._dictionary[new_str] = len(self._dictionary)
            self._current_str = symbol
            return code

    @staticmethod
    def _get_password(password: str | None, salt: bytes) -> bytes | None:
        """
        Получение хэша пароля, указанного при вызове архиватора.
        """
        if password is None:
            return None
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 1000)

    @staticmethod
    def _get_meta_info(password: bytes | None, salt: bytes, files: list[pathlib.Path]) -> MetaInfo:
        """
        Получение мета-информации, которая будет записана как футер сжатого файла
        для корректного декодирования.
        """
        return MetaInfo(
            password=Password(has_password=password is not None, password=password, salt=salt),
            files={file_path.name: 0 for file_path in files},
        )
