import zlib


class CRC32:
    # TODO: Дописать документацию ко всем файлам, прогнать через линтеры и запланировать время для реализации пароля
    def __init__(self) -> None:
        self._checksum: int = 0

    def update_checksum(self, data: bytes) -> None:
        self._checksum = zlib.crc32(data, self._checksum)

    def get_checksum(self) -> int:
        return self._checksum & 0xFFFFFFFF

