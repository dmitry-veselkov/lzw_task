from .archiver import Archiver
from .archiver_status import ArchiverMode, ArchiverProgress, ArchiverStatus
from .constants import DEFAULT_DICT_LENGTH
from .file_manager import FileManager
from .crc import CRC32


class Decoder(Archiver):
    """
    Режим декодирования (раскаковки)

    Ход работы декодировищка:
    1. Достать из конца файла 32 бита контрольной суммы и 16 бит с размером мета-информации
    2. Получить из мета-информации: название всех файлов и их размер в сжатом виде
    3. Начать запись в файлы, начиная с первого до момента, пока не закончится его размер
    4. Проверить контрольную сумму
    """

    def __init__(self, file_path: str, dictionary: dict[int, str] | None = None) -> None:
        """Инициализация начального словаря и сохранение информации об исходном файле"""
        super().__init__(file_path)  # TODO тут какая-то параша получается с базовым классом

        self._compressed_file_path: str = file_path

        (self._checksum, self._meta_info) = FileManager.load_footer(file_path)
        self._files = [files for files, sizes in self._meta_info.items()]

        self._file_manager = FileManager(self, self._files[0], self._compressed_file_path)
        self._crc = CRC32()

        self._dictionary: dict[int, str] = dictionary or {i: chr(i) for i in range(DEFAULT_DICT_LENGTH)}
        self._previous_str: str = ""

    def run(self) -> ArchiverStatus:
        """Запуск режима разархивации (распаковки)"""
        with open(file=self._compressed_file_path, mode="rb") as compressed_file:
            for file_path, compressed_size in self._meta_info.items():
                with open(file=file_path, mode="w", encoding="utf-8") as origin_file:
                    bits_counter = 0

                    while bits_counter < compressed_size:
                        code: int | None = self._file_manager.read_code(compressed_file)
                        if code is None:
                            break

                        bits_counter += self.current_code_length

                        current_str: str = self._get_current_str(code)
                        origin_file.write(current_str)
                        self._crc.update_checksum(current_str.encode())

                        new_str = self._previous_str + current_str[0]
                        if new_str not in self._dictionary.values():
                            self._dictionary[len(self._dictionary)] = new_str
                            self._try_update_code_length()

                        self._previous_str = current_str

                self._previous_str = ""
                self._file_manager.reset()

        print(self._checksum, self._crc.get_checksum())
        return ArchiverStatus(ArchiverMode.DECODER, ArchiverProgress.SUCCESS)

    def _get_current_str(self, code: int) -> str:
        """По переданному коду возвращает соответсвующую ему строку"""
        if code in self._dictionary:
            return self._dictionary[code]
        return self._previous_str + self._previous_str[0]

    def _try_update_code_length(self) -> None:
        """Попытка обновить длину кода по правилам декодировщика"""
        if len(self._dictionary) >= self._max_code:
            self.current_code_length += 1
            self._max_code = self._update_max_code()
