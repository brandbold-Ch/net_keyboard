"""Client module for TCP communication."""

from abc import ABC, abstractmethod
from typing import Any, TypeAlias, Union

Address: TypeAlias = tuple[Any, ...] | str


class NetworkChannel(ABC):
    """
    Abstract base class for TCP communication.

    This class defines the interface for TCP communication that must be implemented
    by both client and server classes.
    """

    @abstractmethod
    def send(self, packet: Union[str, bytes]) -> None:
        """
        Send a data packet.

        Args:
            packet (Union[str, bytes]): The data packet to send as a string or bytes.
        """
        pass

    @abstractmethod
    def receive(self, size: int) -> str | bytes:
        """
        Receive data from the connection.

        Args:
            size (int): The number of bytes to receive.
        Returns:
            str | bytes: The received data.
        """
        pass

    @abstractmethod
    def open(self, address: Address) -> None:
        """
        Establish a connection.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection.
        """
        pass
