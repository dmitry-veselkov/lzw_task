import zlib


class CRC32:
    CHECKSUM_LENGTH = 32

    def __init__(self) -> None:
        self._checksum: int = 0

    def update_checksum(self, data: bytes) -> None:
        self._checksum = zlib.crc32(data, self._checksum)

    def get_checksum(self) -> int:
        return self._checksum & 0xFFFFFFFF

