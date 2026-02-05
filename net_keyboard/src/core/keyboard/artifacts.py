"""Pynput adapter module for keyboard and mouse event handling over network."""

import struct
import threading
from typing import Optional

from src.backends.base import (
    TUPLE_CODES,
    KeyboardBackend,
    KeyboardTypeEvent,
    MouseBackend,
)
from src.transport.tcp.artifacts import TcpClient, TcpServer

K_LISTENER = Optional[KeyboardBackend]
M_LISTENER = Optional[MouseBackend]


class MKVServer(TcpServer):
    """
    TCP server adapter for keyboard events using Pynput.

    This class captures keyboard and mouse events locally and sends them
    over TCP to connected clients using the Pynput library.
    """

    def __init__(
        self,
        host: str,
        port: int,
        keyboard_listener: K_LISTENER = None,
        mouse_listener: M_LISTENER = None,
    ) -> None:
        """
        Initialize the Pynput server.

        Args:
            host (str): The hostname or IP address to bind the server to.
            port (int): The port number to listen on.
        """
        super().__init__(host, port)
        self.keyboard_listener = keyboard_listener
        self.mouse_listener = mouse_listener

        if self.keyboard_listener:
            self.keyboard_listener.add_subscriber(
                self.on_press, KeyboardTypeEvent.PRESS
            )
            self.keyboard_listener.add_subscriber(
                self.on_release, KeyboardTypeEvent.RELEASE
            )

    def serialize(self, codes: TUPLE_CODES) -> bytes:
        return struct.pack("!qqq", *codes)

    def on_press(self, codes: TUPLE_CODES) -> None:
        self.send(self.serialize(codes))

    def on_release(self, codes: TUPLE_CODES) -> None:
        self.send(self.serialize(codes))

    def run(self) -> None:
        """
        Start the server and listen for keyboard events in a separate thread.
        """
        if self.keyboard_listener:
            threading.Thread(target=self.keyboard_listener.listen).start()

        if self.mouse_listener:
            threading.Thread(target=self.mouse_listener.listen).start()


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
        mouse_listener: M_LISTENER = None,
    ) -> None:
        """
        Initialize the Pynput client.

        Args:
            host (str): The hostname or IP address of the server to connect to.
            port (int): The port number of the server.
        """
        super().__init__(host, port)
        self.keyboard_listener = keyboard_listener
        self.mouse_listener = mouse_listener

    def run(self) -> None:
        while True:
            data: bytes = self.receive(1024)
            code, state, time = struct.unpack("!qqq", data)
            print(code, state, time)
