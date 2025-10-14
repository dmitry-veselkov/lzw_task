from enum import Enum


class ArchiverMode(Enum):
    """Режимы работы архиватора: кодировщик и декодировщик"""
    ENCODER = "Archiving"
    DECODER = "Unpacking"


class ArchiverProgress(Enum):
    """Результат работы архиватора: успех или ошибка"""
    FAULT = "failed with an error"
    SUCCESS = "was completed successfully"


class ArchiverStatus:
    """Возращаемое пользователю состояние архиватора по завершении его работы"""
    def __init__(self, mode: ArchiverMode, fault: ArchiverProgress):
        self.mode = mode
        self.progress = fault
