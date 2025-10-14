from typing import BinaryIO
import struct
import pickle

from .archiver import Archiver


class FileManager:
    """
    Файловый менеджер, необходимый для записи и чтения в бинарные файлы данных
    в том формате, который требует алгоритм LWZ
    """

    def __init__(self, archiver: Archiver, write_file: str, read_file: str | None = None) -> None:
        """Инициализация нового файлого менеджера"""
        self._archiver = archiver
        self._write_file = write_file
        self._read_file = read_file

        self._buffer: int = 0
        self._buffer_length: int = 0

    def write_code(self, code: int) -> None:
        """Запись в файл переданного числового кода"""
        self._buffer = (self._buffer << self._archiver.current_code_length) | code
        self._buffer_length += self._archiver.current_code_length

        while self._buffer_length >= 8:
            byte = self._buffer >> self._buffer_length - 8
            with open(file=self._write_file, mode="ab") as file:
                file.write(bytes([byte]))
            self._buffer_length -= 8
            self._buffer = self._buffer & ((1 << self._buffer_length) - 1)

    def write_remaining_bits(self) -> None:
        """Запись в файл оставшихся битов, которые не были обработаны в основной цикле"""
        if self._buffer_length > 0:
            byte = self._buffer << 8 - self._buffer_length
            with open(self._write_file, 'ab') as file:
                file.write(bytes([byte]))

    def write_footer(self, checksum: int, meta_info: dict[str, int]) -> None:
        with open(self._write_file, 'ab') as file:
            binary_meta = pickle.dumps(meta_info)
            meta_length = len(binary_meta)
            print(meta_length)
            file.write(binary_meta)
            file.write(struct.pack('>H', meta_length))
            file.write(struct.pack(">I", checksum))

    @staticmethod
    def load_footer(file_path: str) -> tuple[int, dict[str, int]]:
        with open(file_path, mode="rb+") as file:
            checksum = int.from_bytes(FileManager._load_end_data(file, bytes_num=4))
            meta_length = int.from_bytes(FileManager._load_end_data(file, bytes_num=2))

            meta_info = pickle.loads(FileManager._load_end_data(file, bytes_num=meta_length))

            file.seek(0, 0)
            return checksum, meta_info

    @staticmethod
    def _load_end_data(file: BinaryIO, bytes_num: int) -> bytes:
        file.seek(-bytes_num, 2)
        data = file.read(bytes_num)
        file.seek(-bytes_num, 2)
        file.truncate()
        # file.seek(0, 0)
        return data

    def read_code(self, compressed_file: BinaryIO) -> int | None:
        """Чтение кода из сжатого файла до тех пор, пока это возможно"""
        while self._buffer_length < self._archiver.current_code_length:
            byte = compressed_file.read(1)
            if not byte:
                return None
            self._buffer = (self._buffer << 8) | byte[0]
            self._buffer_length += 8

        self._buffer_length = self._buffer_length - self._archiver.current_code_length
        return (self._buffer >> self._buffer_length) & ((1 << self._archiver.current_code_length) - 1)

    def reset(self) -> None:
        self._buffer = 0
        self._buffer_length = 0

    def update_write_file(self, new_write_file: str) -> None:
        self._write_file = new_write_file
