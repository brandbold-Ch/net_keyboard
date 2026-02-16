"""Windows named pipe client utilities.

Provides a small PipeClient wrapper around Windows native API calls used to
read from named pipes. The module is Windows-specific and uses pywin32's
win32file functions.
"""

from typing import Any

from win32file import GENERIC_READ, OPEN_EXISTING, CloseHandle, CreateFile, ReadFile

from src.transport.base import Address, NetworkChannel


class PipeClient(NetworkChannel):
    """Client wrapper for reading from a Windows named pipe.

    Note: This implementation focuses on reading (GENERIC_READ). Methods
    raise NotImplementedError where write/send semantics are not provided.
    """

    def __init__(self) -> None:
        self.handle: Any = None

    def send(self, packet: str | bytes) -> None:
        """Send a packet to the server (not implemented)."""
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        """Read up to ``size`` bytes from the pipe.

        Returns the bytes read from the pipe. Raises RuntimeError when the
        pipe has not been opened yet.
        """
        if not self.handle:
            raise RuntimeError("Pipe not opened")
        return ReadFile(self.handle.handle, size)[1]

    def open(self, address: Address) -> None:
        """Open a handle to the named pipe at ``address``.

        The address is expected to be a string pipe name on Windows. The
        CreateFile call opens the pipe for reading using pywin32.
        """
        if isinstance(address, str):
            self.handle = CreateFile(
                address, GENERIC_READ, 0, None, OPEN_EXISTING, 0, None
            )

    def close(self) -> None:
        """Close the pipe handle if it was opened."""
        if self.handle:
            CloseHandle(self.handle.handle)
