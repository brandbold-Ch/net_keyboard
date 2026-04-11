"""Named pipe server interface for Windows platforms.

This module provides a PipeServer stub implementing the NetworkChannel
interface. Methods are left as NotImplementedError since platform-specific
implementations are required for Windows named pipes.
"""

from src.transport.base import Address, BaseConnection


class PipeServer(BaseConnection):
    """Server-side pipe channel placeholder for Windows named pipes."""

    def send(self, packet: str | bytes) -> None:
        """Send a packet to the connected client."""
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        """Receive up to ``size`` bytes from the client."""
        raise NotImplementedError()

    def connect(self, address: Address) -> None:
        """Open or bind the server to the given address."""
        raise NotImplementedError()

    def close(self) -> None:
        """Close the server and free resources."""
        raise NotImplementedError()
