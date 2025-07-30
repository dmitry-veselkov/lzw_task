import argparse
from archiver import Archiver


class CLI:
    @staticmethod
    def run() -> None:
        parser = argparse.ArgumentParser(description="Пока тут написано пупупу")
        parser.add_argument('file_path', help="Absolute path to input file")
        parser.add_argument('-decoding' '-d', help="Decoding mode", action="store_true")
        args = parser.parse_args()

        if args.decoding_d:
            Archiver.decode(args.file_path)
        else:
            Archiver.encode(args.file_path)
