"""Unix domain socket server implementation for local IPC.

This module provides a minimal server channel implementation using
AF_UNIX / SOCK_STREAM sockets. It is intended for local communication on
POSIX systems and mirrors part of the NetworkChannel interface required by
the IPC utilities.
"""

from socket import AF_UNIX, SOCK_STREAM
from socket import socket as Socket
from typing import Optional

from src.transport.base import Address, NetworkChannel, Packet


class SocketUnixServer(NetworkChannel):
    """Server channel backed by a Unix domain socket.

    The server binds to a filesystem path and accepts a single client
    connection. The implementation is intentionally small and synchronous.
    """

    def __init__(self) -> None:
        self.s_socket: Socket = Socket(AF_UNIX, SOCK_STREAM)
        self.c_socket: Optional[Socket] = None

    def send(self, packet: Packet) -> None:
        """Send bytes to the connected client.

        Raises NotImplementedError because this simple implementation writes
        directly to the accepted client socket via other code paths.
        """
        raise NotImplementedError()

    def receive(self, size: int) -> Packet:
        """Receive up to ``size`` bytes from the accepted client connection.

        If no client has connected yet the method blocks until accept() returns
        a connected socket.
        """
        while not self.c_socket:
            self.c_socket = self.s_socket.accept()[0]
        return self.c_socket.recv(size)

    def open(self, address: Address) -> None:
        """Bind the server socket to the provided filesystem path and listen."""
        self.s_socket.bind(address)
        self.s_socket.listen(1)

    def close(self) -> None:
        """Close the server socket and the accepted client socket if present."""
        self.s_socket.close()
        if self.c_socket:
            self.c_socket.close()
