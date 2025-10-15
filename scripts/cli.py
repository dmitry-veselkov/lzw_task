import click

from archiver.archiver import Archiver
from archiver.decoder import Decoder
from archiver.encoder import Encoder


class CLI:
    """
    CLI-интерфейс
    """

    @staticmethod
    @click.command()
    @click.option("-files_path", prompt=True, help="Path to the source file or directory")
    @click.option('-archive_name', default="", help="Archive name")
    @click.option('--decoding', '-d', is_flag=True, help="Enabling deconding mode")
    def run(files_path: str, archive_name: str, decoding: bool) -> None:
        """
        Парсинг аргументов командной строки и запуск архиватора
        в выбранном режиме: сжатие или распаковка.
        """
        print("Processing...")
        archiver: Archiver = Decoder(files_path) if decoding else Encoder(files_path, archive_name)
        status = archiver.run()
        if status.error is None:
            print(f"{status.mode.value} was completed successfully.")
        else:
            print(f"{status.mode.value} failed with an error:")
            raise status.error
