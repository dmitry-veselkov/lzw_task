import os
import unittest

from scripts.archiver.decoder import Decoder
from scripts.archiver.encoder import Encoder


class TestArchiver(unittest.TestCase):
    def test_full(self) -> None:
        """Тестирование на всех переданных файлах"""
        test_cases = ["default_test_text", "lorem_ipsum_text", "alice29", "ascii-art"]

        for file_name in test_cases:
            origin_text: str = read_txt_file(file_name)
            with self.subTest(file_name):
                self.assertEqual(get_new_text_after_archiver_operation(file_name), origin_text)


def get_new_text_after_archiver_operation(file_name: str) -> str:
    """Получаем новый текст после процедуры сжатия-разжатия"""
    # Кодируем оригинальный файл
    encoder = Encoder(f"../src/{file_name}.txt", archive_name="", password="test_password_123")
    encoder.run()
    # Удаляем оригинальный файл
    os.remove(f"../src/{file_name}.txt")

    # Декодируем файл, полученный после кодирования
    decoder = Decoder(f"../src/{file_name}.lzw", password="test_password_123")
    decoder.run()

    # Загружаем текст после декодирования
    new_text: str = read_txt_file(file_name)

    # Удаляем сжатый файл, он нам больше не нужен
    os.remove(f"../src/{file_name}.lzw")

    return new_text


def read_txt_file(file_name: str) -> str:
    """Читаем файл и возвращаем хранящуюся там информацию"""
    with open(f"../src/{file_name}.txt") as file:
        text = file.read()
        if not text:
            raise ValueError(f"Пустой файл {file_name} или ошибка чтения!")
        return text
