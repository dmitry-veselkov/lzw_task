class Archiver:
    _DEFAULT_DICT_LENGTH = 256

    @staticmethod
    def encode(file_path: str) -> None:
        compressed_data: list[int] = Archiver._get_compressed_data(file_path, Archiver._initialize_encode_dict())
        lzw_file_path: str = file_path.rsplit(".", 1)[0] + ".lzw"
        Archiver._write_lzw_file(compressed_data, lzw_file_path)

    @staticmethod
    def decode(file_path: str) -> None:
        codes: list[int] = Archiver._parse_compressed_file()
        original_data: list[str] = Archiver._get_original_data(codes, Archiver._initialize_decode_dict())
        decoded_file_path: str = file_path.rsplit(".", 1)[0] + ".txt"
        Archiver._write_decoded_file(original_data, decoded_file_path)

    @staticmethod
    def _get_compressed_data(file_path: str, dictionary: dict[str, int]) -> list[int]:
        current_str: str = ""
        result: list[int] = []

        with open(file=file_path, mode="r") as file:
            while True:
                symbol = file.read(1)
                if not symbol:
                    break
                new_str = current_str + symbol
                if new_str in dictionary:
                    current_str = new_str
                else:
                    result.append(dictionary[current_str])
                    dictionary[new_str] = len(dictionary)
                    current_str = symbol
            if current_str:
                result.append(dictionary[current_str])

        return result

    @staticmethod
    def _get_original_data(codes: list[int], dictionary: dict[int, str]) -> list[str]:
        previous_str: str = ""
        result: list[str] = []

        for code in codes:
            current_str = dictionary[code] if code in dictionary else previous_str + previous_str[0]
            result.append(current_str)

            new_str = previous_str + current_str[0]
            if new_str not in dictionary.values():
                dictionary[len(dictionary)] = new_str

            previous_str = current_str

        return result

    @staticmethod
    def _write_lzw_file(compressed_data: list[int], lwz_file_path: str) -> None:
        pass

    @staticmethod
    def _write_decoded_file(original_data: list[str], decoded_file_path: str) -> None:
        pass

    @staticmethod
    def _parse_compressed_file() -> list[int]:
        pass

    @staticmethod
    def _initialize_encode_dict() -> dict[str, int]:
        return {chr(i): i for i in range(Archiver._DEFAULT_DICT_LENGTH)}

    @staticmethod
    def _initialize_decode_dict() -> dict[int, str]:
        return {i: chr(i) for i in range(Archiver._DEFAULT_DICT_LENGTH)}
