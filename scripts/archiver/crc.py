import zlib


class CRC32:
    """
    Обертка над классов zlib для удобного вычисления
    контрольной суммы во время работы архтиватора.
    """

    def __init__(self) -> None:
        self._checksum: int = 0

    def update_checksum(self, data: bytes) -> None:
        """
        Обновление текущего значения контрольной суммы по полученнной порции данных.
        """
        self._checksum = zlib.crc32(data, self._checksum)

    def get_checksum(self) -> int:
        """
        Возвращение контрольной суммы, обрезанной до 4 байт.
        :return:
        """
        return self._checksum & 0xFFFFFFFF
