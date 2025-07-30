class Archiver:
    @staticmethod
    def encode(file_path: str) -> None:
        compressed_data: list[int] = Archiver._get_compressed_data(file_path, dict_length=256)
        lzw_file_path = file_path.rsplit(".", 1)[0] + ".lzw"
        Archiver._write_lzw_file(compressed_data, lzw_file_path)

    @staticmethod
    def decode(file_path: str) -> None:
        print(f"decode file {file_path}")

    @staticmethod
    def _get_compressed_data(file_path: str, dict_length: int) -> list[int]:
        dictionary: dict[str, int] = {chr(i): i for i in range(dict_length)}
        # dictionary[""] = dict_length
        next_code: int = dict_length + 1
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
                    # print(current_str)
                    result.append(dictionary[current_str])
                    dictionary[new_str] = next_code
                    next_code += 1
                    current_str = symbol
            if current_str:
                result.append(dictionary[current_str])

        return result

    @staticmethod
    def _write_lzw_file(compressed_data: list[int], lwz_file_path: str) -> None:
        with open(lwz_file_path, mode="wb") as file:
            for code in compressed_data:
                file.write(code.to_bytes(length=2, byteorder='big'))
