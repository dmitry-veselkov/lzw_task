from typing import BinaryIO

from .archiver import Archiver


class FileManager:
    def __init__(self, archiver: Archiver, write_file: str, read_file: str | None = None) -> None:
        self._archiver = archiver
        self._write_file = write_file
        self._read_file = read_file

        self._buffer: int = 0
        self._buffer_length: int = 0

    def write_code(self, code: int) -> None:
        self._buffer = (self._buffer << self._archiver.current_code_length) | code
        self._buffer_length += self._archiver.current_code_length

        while self._buffer_length >= 8:
            byte = self._buffer >> self._buffer_length - 8
            with open(file=self._write_file, mode="ab") as file:
                file.write(bytes([byte]))
            self._buffer_length -= 8
            self._buffer = self._buffer & ((1 << self._buffer_length) - 1)

    def write_remaining_bits(self) -> None:
        if self._buffer_length > 0:
            byte = self._buffer << 8 - self._buffer_length
            with open(self._write_file, 'ab') as file:
                file.write(bytes([byte]))

    def read_code(self, compressed_file: BinaryIO) -> int | None:
        while self._buffer_length < self._archiver.current_code_length:
            byte = compressed_file.read(1)
            if not byte:
                return None
            self._buffer = (self._buffer << 8) | byte[0]
            self._buffer_length += 8

        self._buffer_length = self._buffer_length - self._archiver.current_code_length
        return (self._buffer >> self._buffer_length) & ((1 << self._archiver.current_code_length) - 1)
