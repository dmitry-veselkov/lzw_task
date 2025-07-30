from scripts.archiver import Archiver


def test_encoding():
    expected_result = []
    result_1 = Archiver._get_compressed_data("../src/text2.txt", {"a": 0, "b": 1, "c": 2, "d": 3})
    result_2 = Archiver._get_compressed_data("../src/text2.txt", Archiver._initialize_encode_dict())

    print(f"Expected: {expected_result}")
    print(f"Result_1: {result_1}")
    print(f"Result_2: {result_2}")


def test_decoding():
    codes_1 = [0, 1, 3, 4, 2, 2, 7, 6, 1]
    result_1 = Archiver._get_original_data(codes_1, {0: "a", 1: "b", 2: "c", 3: "d"})

    codes_2 = [97, 98, 100, 256, 99, 99, 259, 258, 98]
    result_2 = Archiver._get_original_data(codes_2, Archiver._initialize_decode_dict())

    print(f"Result_1: {result_1}")
    print(f"Result_2: {result_2}")


def test_save_text():
    compressed_data = Archiver._get_compressed_data("../src/text.txt", Archiver._initialize_encode_dict())
    original_text = Archiver._get_original_data(compressed_data, Archiver._initialize_decode_dict())
    print(''.join(original_text))


if __name__ == "__main__":
    # test_encoding()
    # test_decoding()
    test_save_text()