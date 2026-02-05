from typing import Any, Optional, Self

from win32file import GENERIC_READ, OPEN_EXISTING, CloseHandle, CreateFile, ReadFile

from src.transport.base import Address, NetworkChannel


class PyHANDLE:
    @property
    def handle(self) -> int: ...
    def Close(self) -> None: ...
    def close(self) -> None: ...
    def Detach(self) -> Self: ...


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


class PipeServer(NetworkChannel):
    def send(self, packet: str | bytes) -> None:
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        raise NotImplementedError()

    def open(self, address: Address) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()
