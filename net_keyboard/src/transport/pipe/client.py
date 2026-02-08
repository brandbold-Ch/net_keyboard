from typing import Any

from win32file import GENERIC_READ, OPEN_EXISTING, CloseHandle, CreateFile, ReadFile

from src.transport.base import Address, NetworkChannel


class PipeClient(NetworkChannel):
    def __init__(self) -> None:
        self.handle: Any = None

    def send(self, packet: str | bytes) -> None:
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        if not self.handle:
            raise RuntimeError("Pipe not opened")
        return ReadFile(self.handle.handle, size)[1]

    def open(self, address: Address) -> None:
        if isinstance(address, str)
            self.handle = CreateFile(address, GENERIC_READ, 0, None, OPEN_EXISTING, 0, None)

    def close(self) -> None:
        if self.handle:
            CloseHandle(self.handle.handle)
