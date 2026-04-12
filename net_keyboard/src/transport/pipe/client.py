import time

import pywintypes
import win32pipe
from win32file import GENERIC_READ, OPEN_EXISTING, CloseHandle, CreateFile, ReadFile

from src.transport.base import Address, BaseConnection, Packet


class PipeClient(BaseConnection):
    def __init__(self) -> None:
        self.handle = None

    def send(self, packet: Packet):
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        if not self.handle:
            raise RuntimeError("Pipe not opened")
        return ReadFile(self.handle, size)[1]  # 👈 ojo aquí también

    def connect(self, address: Address) -> None:
        if not isinstance(address, str):
            return

        while True:
            try:
                self.handle = CreateFile(
                    address, GENERIC_READ, 0, None, OPEN_EXISTING, 0, None
                )
                break  # 🔥 conectado

            except pywintypes.error as e:
                if e.winerror == 2:
                    # 🔥 pipe no existe aún
                    time.sleep(0.3)
                    continue

                elif e.winerror == 231:
                    # ERROR_PIPE_BUSY
                    win32pipe.WaitNamedPipe(address, 5000)
                    continue

                else:
                    raise

    def close(self) -> None:
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None
