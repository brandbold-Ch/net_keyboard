"""Base module for TCP communication abstraction."""
from typing import Union
from abc import ABC, abstractmethod


class TCP(ABC):
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
    def receive(self) -> bytes:
        """
        Receive data from the connection.
        
        Returns:
            bytes: The received data.
        """
        pass
    
    @abstractmethod
    def connect(self) -> None:
        """
        Establish a connection.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the connection.
        """
        pass
    
    @abstractmethod
    def run(self) -> None:
        """
        Execute the main communication loop.
        """
        pass
