"""Unix domain socket client stub implementation.

This module exposes a minimal client implementation placeholder for Unix
domain sockets. The methods are intentionally left as NotImplemented to be
filled by platform-specific code if needed.
"""

from src.transport.base import Address, BaseConnection, Packet


class SocketLinuxClient(BaseConnection):
    """Client side channel for Unix domain sockets.

    The current code provides method signatures matching NetworkChannel but
    raises NotImplementedError. This file documents the expected behavior for
    future implementations.
    """

    def send(self, packet: Packet) -> None:
        """Send a packet to the connected server."""
        raise NotImplementedError()

    def receive(self, size: int) -> Packet:
        """Receive up to ``size`` bytes from the server."""
        raise NotImplementedError()

    def connect(self, address: Address) -> None:
        """Open a connection to the given address."""
        raise NotImplementedError()

    def close(self) -> None:
        """Close the connection and release resources."""
        raise NotImplementedError()
