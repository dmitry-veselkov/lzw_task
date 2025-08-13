import argparse

from scripts.archiver import Archiver
from scripts.decoder import Decoder
from scripts.encoder import Encoder


class CLI:
    @staticmethod
    def run() -> None:
        parser = argparse.ArgumentParser(description="Пока тут написано пупупу")
        parser.add_argument('file_path', help="Absolute path to input file")
        parser.add_argument('-decoding' '-d', help="Decoding mode", action="store_true")
        args = parser.parse_args()

        archiver: Archiver = Decoder(args.file_path) if args.decoding_d else Encoder(args.file_path)
        archiver.run()
