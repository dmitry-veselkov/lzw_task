import hashlib
import pathlib
from typing import BinaryIO

from .archiver import Archiver
from .archiver_status import ArchiverMode, ArchiverStatus
from .constants import DEFAULT_DICT_LENGTH
from .crc import CRC32
from .file_manager import FileManager
from .meta_info import Password


class Decoder(Archiver):
    """
    Декодировщик, получающий исходный(-ы) файл(-ы)
    из сжатого представления с помощью алгоритма LZW.
    """

    def __init__(self, path: str, password: str | None, dictionary: dict[int, str] | None = None) -> None:
        """
        Инициализация нового декаодировщика для указанного сжатого файла.
        Обработка полученного пути, создание начального словаря и подключение
        алгоритма для проверки целостности.
        """
        super().__init__()

        self._file_manager = FileManager()
        self._crc = CRC32()

        self._compressed_file_path = pathlib.Path(path)
        self._checksum, self._meta_info, footer_size = self._file_manager.load_footer(self._compressed_file_path)

        self._check_password(self._meta_info.password, password)

        self._saved_directory = self._get_saved_directory()
        self._dictionary: dict[int, str] = dictionary or {i: chr(i) for i in range(DEFAULT_DICT_LENGTH)}
        self._previous_str: str = ""

    def run(self) -> ArchiverStatus:
        """
        Основной метод декодировщика. Открывает сжатый файл, декодирует информацию
        и записывает расшифрованные данные в файлы с оригинальными названиями.
        В конце работы проверяет, что контрольные суммы сходятся, и уведомляет
        о статусе своей работы.
        """
        with open(file=self._compressed_file_path, mode="rb") as compressed_file:
            for file_name, compressed_size in self._meta_info.files.items():
                file_path = self._saved_directory / file_name
                self._decode_file(file_path, compressed_size, compressed_file)
                self._previous_str = ""
                self._file_manager.reset()

        if self._compare_checksum():
            return ArchiverStatus(ArchiverMode.DECODER)
        return ArchiverStatus(
            ArchiverMode.DECODER, ValueError("Checksum mismatch: loaded checksum does not match computed value.")
        )

    def _decode_file(self, file_path: pathlib.Path, size: int, compressed_file: BinaryIO) -> None:
        """
        Декодирует один указанный файл с фиксированным размером.
        Параллельно считает контрольную сумму для проверки целостности.
        """
        with open(file=file_path, mode="w", encoding="utf-8") as origin_file:
            bits_counter = 0
            while bits_counter < size:
                code: int | None = self._file_manager.read_code(compressed_file, self.code_length)
                if code is None:
                    break
                bits_counter += self.code_length

                current_str: str = self._get_current_str(code)
                origin_file.write(current_str)
                self._crc.update_checksum(current_str.encode())

                new_str = self._previous_str + current_str[0]
                if new_str not in self._dictionary.values():
                    self._dictionary[len(self._dictionary)] = new_str
                    self._try_update_code_length()
                self._previous_str = current_str

    def _compare_checksum(self) -> bool:
        """
        Сравнение контрольной суммы, полученной в результате декодирования,
        с той, что была записана кодировщиком
        """
        return self._checksum == self._crc.get_checksum()

    def _get_current_str(self, code: int) -> str:
        """
        Получение соответсвующей строки по переданному коду.
        """
        if code in self._dictionary:
            return self._dictionary[code]
        return self._previous_str + self._previous_str[0]

    def _try_update_code_length(self) -> None:
        """
        Реализация механизма обновления длины по правилам декодировщика.
        """
        if len(self._dictionary) >= self._max_code:
            self.code_length += 1
            self._max_code = self._update_max_code()

    def _get_saved_directory(self) -> pathlib.Path:
        """
        Определение директории, в которую будут сохранены декодированные файлы.
        """
        if self._meta_info.has_many_files:
            saved_directory = self._compressed_file_path.parent / self._compressed_file_path.stem
            saved_directory.mkdir(exist_ok=True)
            return saved_directory

        return self._compressed_file_path.parent

    @staticmethod
    def _check_password(pass_info: Password, currrent_pass: str | None) -> None:
        """
        Проверка, что хэш пароля, сгенерированный при кодировании файлов,
        совпадает с хэшем полученного при декодировании пароля.
        """
        if not pass_info.has_password:
            return

        current_encode: bytes | None = None
        if currrent_pass is not None:
            current_encode = hashlib.pbkdf2_hmac('sha256', currrent_pass.encode(), pass_info.salt, 1000)

        if pass_info.password != current_encode:
            raise ValueError("Wrong password!")
