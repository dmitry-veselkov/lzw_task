from enum import Enum


class ArchiverMode(Enum):
    """Режимы работы архиватора: кодировщик и декодировщик"""
    ENCODER = "Archiving"
    DECODER = "Unpacking"


class ArchiverStatus:
    """Возращаемое пользователю состояние архиватора по завершении его работы"""
    def __init__(self, mode: ArchiverMode, error: Exception = None) -> None:
        self.mode = mode
        self.error = error
