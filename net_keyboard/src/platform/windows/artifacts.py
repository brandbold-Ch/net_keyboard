from typing import Optional
from src.socket.base import NetworkChannel, Address
from _win32typing import PyHANDLE
from win32file import GENERIC_READ, OPEN_EXISTING, CloseHandle, CreateFile, ReadFile


class PipeClient(NetworkChannel):
    
    def __init__(self) -> None:
        self.handle: Optional[PyHANDLE] = None
    
    def send(self, packet: str | bytes) -> None:
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        if not self.handle:
            raise RuntimeError("Pipe not opened")
        return ReadFile(self.handle.handle, size)[1]

    def open(self, address: Address) -> None:
        self.handle = CreateFile(
            address, 
            GENERIC_READ, 
            0, 
            None, 
            OPEN_EXISTING, 
            0, 
            None
        )

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
        