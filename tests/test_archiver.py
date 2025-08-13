import os
import unittest

from scripts.archiver.decoder import Decoder
from scripts.archiver.encoder import Encoder


class TestArchiver(unittest.TestCase):
    def test_full(self) -> None:
        test_cases = ["default_test_text", "lorem_ipsum_text", "alice29", "ascii-art"]

        for file_name in test_cases:
            origin_text: str = read_txt_file(file_name)
            with self.subTest(file_name):
                self.assertEqual(get_new_text_after_archiver_operation(file_name), origin_text)


def get_new_text_after_archiver_operation(file_name: str) -> str:
    # Encoding origin file
    encoder = Encoder(f"../src/{file_name}.txt")
    encoder.run()

    # Remove origin file
    os.remove(f"../src/{file_name}.txt")

    # Decoding origin file
    decoder = Decoder(f"../src/{file_name}.lzw")
    decoder.run()

    # Load text after decoding
    new_text: str = read_txt_file(file_name)

    # Remove origin file
    os.remove(f"../src/{file_name}.lzw")

    return new_text


def read_txt_file(file_name: str) -> str:
    with open(f"../src/{file_name}.txt") as file:
        text = file.read()
        if not text:
            raise ValueError(f"Пустой файл {file_name} или ошибка чтения!")
        return text
