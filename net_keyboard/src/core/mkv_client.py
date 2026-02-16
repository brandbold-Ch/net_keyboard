"""TCP client adapter for receiving and simulating keyboard events.

This module contains MKVClient which connects to a TCP server that emits
serialized keyboard events. MKVClient deserializes incoming packets using
the project's GLOBAL_FORMAT and forwards events to a local keyboard
backend for simulation.
"""

import struct
from typing import Optional

from src.backends.base import KeyboardBackend
from src.transport.ipc.tools import GLOBAL_FORMAT, safe_read
from src.transport.socket_tcp import TcpClient

K_LISTENER = Optional[KeyboardBackend]


class MKVClient(TcpClient):
    """Client adapter that receives serialized keyboard events from server.

    MKVClient connects to a remote TcpServer and continuously reads fixed
    size packets according to GLOBAL_FORMAT. Decoded events can be passed
    to a local KeyboardBackend instance for local simulation.

    Attributes:
        keyboard_listener (Optional[KeyboardBackend]): Optional backend used
            to simulate or dispatch received keyboard events locally.
    """

    def __init__(
        self,
        host: str,
        port: int,
        keyboard_listener: K_LISTENER = None,
    ) -> None:
        """Initialize the TCP client and optionally set a keyboard backend.

        Args:
            host: Hostname or IP address of the server to connect to.
            port: Port number of the server.
            keyboard_listener: Optional backend to receive simulated events.
        """
        super().__init__(host, port)
        self.keyboard_listener = keyboard_listener

    def start(self) -> None:
        """Run the client's receive loop and dispatch incoming events.

        This method blocks and reads exactly GLOBAL_FORMAT.size bytes from the
        socket, unpacks the tuple and (currently) prints the values. In a
        full implementation the decoded event should be forwarded to the
        configured keyboard backend.
        """
        spec = GLOBAL_FORMAT

        while True:
            data: bytes = safe_read(self.receive, spec.size)
            code, state, time = struct.unpack(spec.fmt, data)
            print(code, state, time)
