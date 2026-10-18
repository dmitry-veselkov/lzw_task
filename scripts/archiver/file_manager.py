import pathlib
import pickle
import struct
from typing import BinaryIO

from .constants import CHECKSUM_BYTES, META_LENGTH_BYTES
from .meta_info import MetaInfo


class FileManager:
    """
    Файловый менеджер, необходимый для записи в бинарные файлы и чтения данных из них.
    Запись и чтение реализованы в формате, обеспечивающим корректную работу алгоритма LZW.
    """

    def __init__(self) -> None:
        """
        Инициализация нового файлого менеджера.
        """
        self._buffer: int = 0
        self._buffer_length: int = 0

    def write_code(self, file_path: pathlib.Path, code: int, code_length: int) -> None:
        """
        Запись в файл переданного числового кода в виде фиксированного числа бит.
        """
        self._buffer = (self._buffer << code_length) | code
        self._buffer_length += code_length

        while self._buffer_length >= 8:
            byte = self._buffer >> self._buffer_length - 8
            with open(file=file_path, mode="ab") as file:
                file.write(bytes([byte]))
            self._buffer_length -= 8
            self._buffer = self._buffer & ((1 << self._buffer_length) - 1)

    def write_remaining_bits(self, file_path: pathlib.Path) -> None:
        """
        Запись в файл оставшихся битов (< 8 бит), которые не были обработаны в основной цикле.
        """
        if self._buffer_length > 0:
            byte = self._buffer << 8 - self._buffer_length
            with open(file=file_path, mode='ab') as file:
                file.write(bytes([byte]))

    def read_code(self, compressed_file: BinaryIO, code_length: int) -> int | None:
        """
        Чтение кода фиксированной длины из сжатого файла.
        """
        while self._buffer_length < code_length:
            byte = compressed_file.read(1)
            if not byte:
                return None
            self._buffer = (self._buffer << 8) | byte[0]
            self._buffer_length += 8

        self._buffer_length = self._buffer_length - code_length
        return (self._buffer >> self._buffer_length) & ((1 << code_length) - 1)

    def reset(self) -> None:
        """
        Сброс значений полей файлового менеждера к стартовым.
        """
        self._buffer = 0
        self._buffer_length = 0

    @staticmethod
    def write_footer(file_path: pathlib.Path, checksum: int, meta_info: MetaInfo) -> None:
        """
        Запись в бинарный файл футера со служебной информацией, которая необходима
        для корректной последующей распакодки: названия исходных файлов, размер
        каждого файла в сжатом виде и контрольная сумма.
        """
        with open(file_path, 'ab') as file:
            binary_meta = pickle.dumps(meta_info)
            meta_length = len(binary_meta)
            file.write(binary_meta)
            file.write(struct.pack('>H', meta_length))
            file.write(struct.pack(">I", checksum))

    @staticmethod
    def load_footer(file_path: pathlib.Path) -> tuple[int, MetaInfo, int]:
        """
        Чтение футера из сжатого файла:
        - целочисленная контрольная сумма;
        - словарь с мета-информацией о пароле и файлах.
        """
        offset = META_LENGTH_BYTES + CHECKSUM_BYTES

        with open(file_path, mode="rb") as file:
            file.seek(-offset, 2)
            meta_length_bytes = file.read(META_LENGTH_BYTES)
            checksum_bytes = file.read(CHECKSUM_BYTES)

            checksum = int.from_bytes(checksum_bytes)
            meta_length = int.from_bytes(meta_length_bytes)

            file.seek(-(offset + meta_length), 2)
            meta_info_bytes = file.read(meta_length)
            meta_info = pickle.loads(meta_info_bytes)

            return checksum, meta_info, meta_length + offset

    @staticmethod
    def get_files_with_dir(str_path: str) -> tuple[list[pathlib.Path], pathlib.Path]:
        """
        Возвращает список файлов и директорию, в которой они лежат.
        Если передано имя файла, вернет список с одним этим файлом и его директорию.
        Не поддерживает глубокое чтение: вложенные директории опускаются.
        """
        path = pathlib.Path(str_path)
        if path.is_file():
            return [path], path.parents[0]
        if path.is_dir():
            files = []
            for file in path.iterdir():
                if file.is_file():
                    files.append(file)
            return files, path

        raise FileNotFoundError(f"No such file or directory: '{path}'")
