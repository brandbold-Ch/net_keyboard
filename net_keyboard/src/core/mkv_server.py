"""Pynput adapter module for keyboard and mouse event handling over network."""

import struct
import threading
from typing import Optional

from src.backends.base import (
    TUPLE_CODES,
    KeyboardBackend,
    KeyboardTypeEvent,
)
from src.transport.ipc.tools import GLOBAL_FORMAT
from src.transport.socket_tcp import TcpServer

K_LISTENER = Optional[KeyboardBackend]


class MKVServer(TcpServer):
    """
    TCP server adapter for keyboard events using Pynput.

    This class captures keyboard and mouse events locally and sends them
    over TCP to connected clients using the Pynput library.
    """

    def __init__(
        self, host: str, port: int, keyboard_listener: K_LISTENER = None
    ) -> None:
        """
        Initialize the Pynput server.

        Args:
            host (str): The hostname or IP address to bind the server to.
            port (int): The port number to listen on.
        """
        super().__init__(host, port)
        self.keyboard_listener = keyboard_listener

        if self.keyboard_listener:
            self.keyboard_listener.add_subscriber(
                self.on_press, KeyboardTypeEvent.PRESS
            )
            self.keyboard_listener.add_subscriber(
                self.on_release, KeyboardTypeEvent.RELEASE
            )

    def serialize(self, codes: TUPLE_CODES) -> bytes:
        return struct.pack(GLOBAL_FORMAT.fmt, *codes)

    def on_press(self, codes: TUPLE_CODES) -> None:
        self.send(self.serialize(codes))

    def on_release(self, codes: TUPLE_CODES) -> None:
        self.send(self.serialize(codes))

    def start(self) -> None:
        """
        Start the server and listen for keyboard events in a separate thread.
        """
        if self.keyboard_listener:
            threading.Thread(target=self.keyboard_listener.listen).start()
