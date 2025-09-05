import argparse

from archiver.archiver import Archiver
from archiver.decoder import Decoder
from archiver.encoder import Encoder


class CLI:
    """CLI-интерфейс"""
    @staticmethod
    def run() -> None:
        """Парсинг полученных аргументов и запуск архиватора в выбранном режиме: сжатие или распаковка"""
        parser = argparse.ArgumentParser(description="CLI-archiver")
        parser.add_argument('file_path', help="Absolute or relative path to input file")
        parser.add_argument('-decoding' '-d', help="Enabling decoding mode", action="store_true")
        args = parser.parse_args()

        print("Processing...")

        archiver: Archiver = Decoder(args.file_path) if args.decoding_d else Encoder(args.file_path)
        status = archiver.run()

        print(f"{status.mode.value} of the file with name '{status.file_name}' {status.progress.value}.")
