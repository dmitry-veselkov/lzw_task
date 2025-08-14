from enum import Enum


class ArchiverMode(Enum):
    ENCODER = "Archiving"
    DECODER = "Unpacking"


class ArchiverProgress(Enum):
    FAULT = "failed with an error"
    SUCCESS = "was completed successfully"


class ArchiverStatus:
    def __init__(self, mode: ArchiverMode, fault: ArchiverProgress, file_name: str):
        self.mode = mode
        self.progress = fault
        self.file_name = file_name
