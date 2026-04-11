"""TCP server adapter for transmitting keyboard events over the network.

This module provides the MKVServer class which adapts a local keyboard
backend into a TCP server. It serializes keyboard event codes using the
project's global format and forwards them to connected TCP clients.
"""

import struct
import threading
from typing import Optional

from src.backends.base import (
    TUPLE_CODES,
    KeyboardBackend,
    KeyboardTypeEvent,
)
from src.transport.ipc.tools import GLOBAL_FORMAT
from src.transport.socket_tcp import TCPServer

K_LISTENER = Optional[KeyboardBackend]


class NetKeyboardServer(TCPServer):
    """Server adapter that forwards local keyboard events to TCP clients.

    MKVServer extends the generic TcpServer to listen for keyboard events
    provided by a KeyboardBackend implementation. When events are received
    they are serialized with the project's GLOBAL_FORMAT and sent to all
    connected clients.

    Attributes:
        keyboard_listener (Optional[KeyboardBackend]): Optional backend that
            provides keyboard events. If provided, its press/release
            callbacks are subscribed to the server's send methods.
    """

    def __init__(
        self, host: str, port: int, keyboard_listener: K_LISTENER = None
    ) -> None:
        """Initialize the server and optionally attach a keyboard listener.

        Args:
            host: Hostname or IP address to bind the TCP server.
            port: Port number to listen on.
            keyboard_listener: Optional backend that emits keyboard events.
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
        """Serialize a tuple of keyboard codes into bytes.

        Args:
            codes: A tuple of three integers matching GLOBAL_FORMAT.

        Returns:
            A bytes object ready to be sent over the network.
        """
        return struct.pack(GLOBAL_FORMAT.fmt, *codes)

    def on_press(self, codes: TUPLE_CODES) -> None:
        """Callback invoked for key press events; sends serialized packet."""
        self.send(self.serialize(codes))

    def on_release(self, codes: TUPLE_CODES) -> None:
        """Callback invoked for key release events; sends serialized packet."""
        self.send(self.serialize(codes))

    def start(self) -> None:
        """
        Start the server and listen for keyboard events in a separate thread.
        """
        if self.keyboard_listener:
            threading.Thread(target=self.keyboard_listener.listen).start()
