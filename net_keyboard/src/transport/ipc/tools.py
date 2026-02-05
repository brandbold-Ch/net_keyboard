import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from struct import calcsize, unpack
from threading import Thread
from typing import Callable, NamedTuple, Optional, Tuple, TypeAlias, Union

CB_EVENT: TypeAlias = Callable[[Tuple[int, int, int]], None]


FMT: str = "<H B Q"
SIZE: int = calcsize(FMT)


class FormatSpec(NamedTuple):
    fmt: str
    size: int


GLOBAL_FORMAT_SPEC = FormatSpec(fmt=FMT, size=SIZE)
CALLBACK_READER: TypeAlias = Callable[[int], str | bytes]


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


AgentSource: TypeAlias = Union[IPCStreamReader, str]


class IPCProcessLauncher(ABC):
    def __init__(self, client: AgentSource, server: AgentSource, shared: str) -> None:
        self.client = client
        self.server = server
        self.shared = shared

        self.base_path = Path(__file__).resolve().parent

    def start_process(self, exec: str) -> None:
        try:
            subprocess.Popen([self.base_path / exec])
        except Exception as e:
            print(f"{__file__} -> {e}")

    def posix_channel_1(self) -> None:
        from src.transport.socket import SocketServer

        u_server: SocketServer = SocketServer()
        u_server.open(self.shared)

        if isinstance(self.server, str):
            self.start_process(self.server)

        elif isinstance(self.server, IPCStreamReader):
            Thread(target=self.server.open, args=(u_server.receive,)).start()

    def posix_channel_2(self) -> None:
        from src.transport.socket import SocketClient

        u_client: SocketClient = SocketClient()
        # u_client.open(self.shared)

        if isinstance(self.client, str):
            self.start_process(self.client)

        elif isinstance(self.client, IPCStreamReader):
            Thread(target=self.client.open, args=(u_client.receive,)).start()

    def nt_channel_1(self) -> None:
        from src.transport.pipe import PipeServer

        u_server: PipeServer = PipeServer()
        # u_server.open(self.shared)

        if isinstance(self.server, str):
            self.start_process(self.server)

        elif isinstance(self.server, IPCStreamReader):
            Thread(target=self.server.open, args=(u_server.receive,)).start()

    def nt_channel_2(self) -> None:
        from src.transport.pipe import PipeClient

        u_client: PipeClient = PipeClient()
        u_client.open(self.shared)

        if isinstance(self.client, str):
            self.start_process(self.client)

        elif isinstance(self.client, IPCStreamReader):
            Thread(target=self.client.open, args=(u_client.receive,)).start()

    def launch(self) -> None:
        os_name = os.name

        if os_name == "posix":
            self.posix_channel_1()
            self.posix_channel_2()

        elif os_name == "nt":
            self.nt_channel_1()
            self.nt_channel_2()


class KeyListener(IPCStreamReader):
    def __init__(
        self, on_press: Optional[CB_EVENT] = None, on_release: Optional[CB_EVENT] = None
    ) -> None:
        self.on_press: Optional[CB_EVENT] = on_press
        self.on_release: Optional[CB_EVENT] = on_release
        self._running: bool = True

    def open(self, raw: CALLBACK_READER) -> None:
        spec = GLOBAL_FORMAT_SPEC

        try:
            while self._running:
                data: bytes = safe_read(raw, spec.size)
                code, state, time = unpack(spec.fmt, data)

                if state == 1 and self.on_press:
                    self.on_press((code, state, time))

                elif state == 0 and self.on_release:
                    self.on_release((code, state, time))

        except Exception as e:
            print(f"Listener error: {e}")
        finally:
            self.close()

    def close(self) -> None:
        pass
