from scripts.archiver import Archiver
from scripts.constants import DEFAULT_DICT_LENGTH
from scripts.file_manager import FileManager


class Decoder(Archiver):
    def __init__(self, file_path: str, dictionary: dict[int, str] | None = None) -> None:
        super().__init__()

        self._compressed_file_path: str = file_path
        self._origin_file_path: str = file_path.rsplit('.', 1)[0] + ".txt"
        self._file_manager = FileManager(
            archiver=self, write_file=self._origin_file_path, read_file=self._compressed_file_path
        )

        self._dictionary: dict[int, str] = dictionary or {i: chr(i) for i in range(DEFAULT_DICT_LENGTH)}
        self._previous_str: str = ""

    def run(self) -> None:
        with (
            open(file=self._origin_file_path, mode="w", encoding="utf-8") as origin_file,
            open(file=self._compressed_file_path, mode="rb") as compressed_file,
        ):
            while True:
                code: int | None = self._file_manager.read_code(compressed_file)
                if code is None:
                    break

                if code in self._dictionary:
                    current_str = self._dictionary[code]
                else:
                    current_str = self._previous_str + self._previous_str[0]

                origin_file.write(current_str)

                new_str = self._previous_str + current_str[0]
                if new_str not in self._dictionary.values():
                    self._dictionary[len(self._dictionary)] = new_str
                    self._try_update_code_length_2()

                self._previous_str = current_str

    def _try_update_code_length_2(self) -> None:
        if len(self._dictionary) >= self._max_code:
            self.current_code_length += 1
            self._max_code = self._update_max_code()
