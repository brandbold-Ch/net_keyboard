from abc import ABC, abstractmethod
from typing import NamedTuple, Union, Optional, cast
from struct import calcsize
from socket import AF_UNIX, SOCK_STREAM, socket as Socket
from typing import Callable

try:
    from _win32typing import PyHANDLE
    from win32file import (
        CreateFile, ReadFile, CloseHandle,
        GENERIC_READ, OPEN_EXISTING
    )
except ModuleNotFoundError:
    pass

from src.socket.base import NetworkChannel, Address
import subprocess
from threading import Thread
import os


FMT: str = "<H B Q"
SIZE: int = calcsize(FMT)


class FormatSpec(NamedTuple):
    fmt: str
    size: int


GLOBAL_FORMAT_SPEC = FormatSpec(fmt=FMT, size=SIZE)
CALLBACK_READER = Callable[[int], str | bytes]


def safe_read(
    reader: CALLBACK_READER, 
    size: int
) -> bytes:
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


class SocketClient(NetworkChannel):
    
    def send(self, packet: str | bytes) -> None:
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        raise NotImplementedError()

    def open(self, address: Address) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()


class SocketServer(NetworkChannel):
    
    def __init__(self) -> None:
        self.s_socket: Socket = Socket(AF_UNIX, SOCK_STREAM)
        self.c_socket: Optional[Socket] = None
        
    def send(self, packet: str | bytes) -> None:
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        while not self.c_socket:
            self.c_socket = self.s_socket.accept()[0]
        return self.c_socket.recv(size)

    def open(self, address: Address) -> None:
        self.s_socket.bind(address)
        self.s_socket.listen(1)

    def close(self) -> None:
        self.s_socket.close()
        if self.c_socket:
            self.c_socket.close()


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
            cast(str, address), 
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
    

EnforcementAgent = Union[IPCStreamReader, str]


class IPCProcessLauncher(ABC):

    def __init__(
        self, 
        client: EnforcementAgent, 
        server: EnforcementAgent,
        shared: str
    ) -> None:
        self.client = client
        self.server = server
        self.shared = shared
        
    def start_process(self, path: str) -> None:
        try:
            subprocess.Popen(
                [path],
                cwd=os.getcwd()
            )
        except Exception as e:
            print(f"{__file__} -> {e}")
            
    def linux_channel_1(self) -> None:
        u_server: NetworkChannel = SocketServer()
        u_server.open(self.shared)

        if isinstance(self.server, str):
            self.start_process(self.server)

        elif isinstance(self.server, IPCStreamReader):
            Thread(target=self.server.open, args=(u_server.receive,)).start()

    def linux_channel_2(self) -> None:
        u_client: NetworkChannel = SocketClient()
        #u_client.open(self.shared)

        if isinstance(self.client, str):
            self.start_process(self.client)
            
        elif isinstance(self.client, IPCStreamReader):
            Thread(target=self.client.open, args=(u_client.receive,)).start()
    
    def windows_channel_1(self) -> None:
        u_server: NetworkChannel = PipeServer()
        #u_server.open(self.shared)
        
        if isinstance(self.server, str):
            self.start_process(self.server)
        
        elif isinstance(self.server, IPCStreamReader):
            Thread(target=self.server.open, args=(u_server.receive,)).start()

    def windows_channel_2(self) -> None:
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
