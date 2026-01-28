import os
import subprocess
from abc import ABC, abstractmethod
from struct import calcsize
from threading import Thread
from typing import Callable, NamedTuple, Union

from src.socket.base import NetworkChannel

FMT: str = "<H B Q"
SIZE: int = calcsize(FMT)


class FormatSpec(NamedTuple):
    fmt: str
    size: int


GLOBAL_FORMAT_SPEC = FormatSpec(fmt=FMT, size=SIZE)
CALLBACK_READER = Callable[[int], str | bytes]


def safe_read(reader: CALLBACK_READER, size: int) -> bytes:
    buffer = b""

    while len(buffer) < size:
        chunk = reader(size - len(buffer))
        if not chunk:
            raise EOFError("IPC Channel closed")
        buffer += chunk

    return buffer


class IPCStreamReader(ABC):
    @abstractmethod
    def open(self, raw: CALLBACK_READER) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


EnforcementAgent = Union[IPCStreamReader, str]


class IPCProcessLauncher(ABC):
    def __init__(
        self, client: EnforcementAgent, server: EnforcementAgent, shared: str
    ) -> None:
        self.client = client
        self.server = server
        self.shared = shared

    def start_process(self, path: str) -> None:
        try:
            subprocess.Popen([path], cwd=os.getcwd())
        except Exception as e:
            print(f"{__file__} -> {e}")

    def linux_channel_1(self) -> None:
        from .linux.artifacts import SocketServer

        u_server: NetworkChannel = SocketServer()
        u_server.open(self.shared)

        if isinstance(self.server, str):
            self.start_process(self.server)

        elif isinstance(self.server, IPCStreamReader):
            Thread(target=self.server.open, args=(u_server.receive,)).start()

    def linux_channel_2(self) -> None:
        from .linux.artifacts import SocketClient

        u_client: NetworkChannel = SocketClient()
        # u_client.open(self.shared)

        if isinstance(self.client, str):
            self.start_process(self.client)

        elif isinstance(self.client, IPCStreamReader):
            Thread(target=self.client.open, args=(u_client.receive,)).start()

    def windows_channel_1(self) -> None:
        from .windows.artifacts import PipeServer

        u_server: NetworkChannel = PipeServer()
        # u_server.open(self.shared)

        if isinstance(self.server, str):
            self.start_process(self.server)

        elif isinstance(self.server, IPCStreamReader):
            Thread(target=self.server.open, args=(u_server.receive,)).start()

    def windows_channel_2(self) -> None:
        from .windows.artifacts import PipeClient

        u_client: PipeClient = PipeClient()
        u_client.open(self.shared)

        if isinstance(self.client, str):
            self.start_process(self.client)

        elif isinstance(self.client, IPCStreamReader):
            Thread(target=self.client.open, args=(u_client.receive,)).start()

    def launch(self) -> None:
        os_name = os.name.lower()
        if os_name == "posix":
            self.linux_channel_1()
            self.linux_channel_2()

        elif os_name == "nt":
            self.windows_channel_1()
            self.windows_channel_2()
