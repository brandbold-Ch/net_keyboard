"""Pynput adapter module for keyboard and mouse event handling over network."""

import struct
from typing import Optional

from src.backends.base import KeyboardBackend
from src.transport.ipc.tools import GLOBAL_FORMAT, safe_read
from src.transport.socket_tcp import TcpClient

K_LISTENER = Optional[KeyboardBackend]


class MKVClient(TcpClient):
    """
    TCP client adapter for simulating keyboard and mouse events using Pynput.

    This class connects to a TCP server, receives keyboard and mouse events,
    and simulates them locally using the Pynput library.
    """

    def __init__(
        self,
        host: str,
        port: int,
        keyboard_listener: K_LISTENER = None,
    ) -> None:
        """
        Initialize the Pynput client.

        Args:
            host (str): The hostname or IP address of the server to connect to.
            port (int): The port number of the server.
        """
        super().__init__(host, port)
        self.keyboard_listener = keyboard_listener

    def start(self) -> None:
        spec = GLOBAL_FORMAT

        while True:
            data: bytes = safe_read(self.receive, spec.size)
            code, state, time = struct.unpack(spec.fmt, data)
            print(code, state, time)
