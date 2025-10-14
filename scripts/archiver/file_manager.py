from typing import BinaryIO
import struct
import pickle
import pathlib


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
    def write_footer(file_path: pathlib.Path, checksum: int, meta_info: dict[str, int]) -> None:
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
    def load_footer(file_path: str) -> tuple[int, dict[str, int]]:
        """
        Чтение футера из сжатого файла:
        - целочисленная контрольная сумма;
        - словарь с мета-информацией о файлах.
        """
        with open(file_path, mode="rb+") as file:
            checksum = int.from_bytes(FileManager._load_end_data(file, bytes_num=4))
            meta_length = int.from_bytes(FileManager._load_end_data(file, bytes_num=2))
            meta_info = pickle.loads(FileManager._load_end_data(file, bytes_num=meta_length))
            file.seek(0, 0)
            return checksum, meta_info

    @staticmethod
    def get_files_with_dir(path: str) -> tuple[list[pathlib.Path], pathlib.Path]:
        """
        Возвращает список файлов и директорию, в которой они лежат.
        Если передано имя файла, вернет список с одним этим файлом и его директорию.
        Не поддерживает глубокое чтение: вложенные директории опускаются.
        """
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

    @staticmethod
    def _load_end_data(file: BinaryIO, bytes_num: int) -> bytes:
        """
        Служебный метод для получения информации определенной длины битов
        из конца бинарного файла с последующим удалением этой информации из файла.
        """
        file.seek(-bytes_num, 2)
        data = file.read(bytes_num)
        file.seek(-bytes_num, 2)
        file.truncate()
        return data
