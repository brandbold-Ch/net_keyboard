from socket import AF_UNIX, SOCK_STREAM
from socket import socket as Socket
from typing import Optional

from src.transport.base import Address, NetworkChannel


class SocketUnixServer(NetworkChannel):
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
