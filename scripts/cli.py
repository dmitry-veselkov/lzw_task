import click

from archiver.archiver import Archiver
from archiver.decoder import Decoder
from archiver.encoder import Encoder


class CLI:
    """CLI-интерфейс"""

    @staticmethod
    @click.command()
    @click.option("-files_path", prompt=True)
    @click.option('--decoding', '-d', is_flag=True)
    def run(files_path: str, decoding: bool) -> None:
        """Парсинг полученных аргументов и запуск архиватора в выбранном режиме: сжатие или распаковка"""
        print("Processing...")
        archiver: Archiver = Decoder(files_path) if decoding else Encoder(files_path)
        status = archiver.run()
        print(f"{status.mode.value} {status.progress.value}.")
