from abc import ABC, abstractmethod
from typing import Any, Tuple, TypeAlias, Union

Address: TypeAlias = Tuple[Any, ...] | str
Packet: TypeAlias = Union[str, bytes]


class BaseConnection(ABC):
    """
    Abstract base class for TCP communication.

    This class defines the interface for TCP communication that must be implemented
    by both client and server classes.
    """

    @abstractmethod
    def send(self, packet: Packet) -> None:
        """
        Send a data packet.

        Args:
            packet (Union[str, bytes]): The data packet to send as a string or bytes.
        """
        pass

    @abstractmethod
    def receive(self, size: int) -> Packet:
        """
        Receive data from the connection.

        Args:
            size (int): The number of bytes to receive.
        Returns:
            str | bytes: The received data.
        """
        pass

    @abstractmethod
    def connect(self, address: Address) -> None:
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
