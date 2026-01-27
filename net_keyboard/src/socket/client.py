"""Client module for TCP communication."""
from typing import Union
from src.socket.base import NetworkChannel, Address
import socket


class TcpClient(NetworkChannel):
    """
    Base TCP client class for establishing network connections.
    
    This class extends the TCP base class and provides client-side functionality
    for connecting to and communicating with TCP servers.
    """

    def __init__(self, host: str, port: int) -> None:
        """
        Initialize the TCP client and connect to the server.
        
        Args:
            host (str): The hostname or IP address of the server to connect to.
            port (int): The port number of the server.
        """
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.open((host, port))

    def send(self, packet: Union[str, bytes]) -> None:
        """
        Send data packet to the connected server.
        
        Args:
            packet (Union[str, bytes]): The data packet to send as a string or bytes.
        """
        if isinstance(packet, str):
            self._client.sendall(packet.encode())
        
        elif isinstance(packet, bytes):
            self._client.sendall(packet)
            
        else:
            raise TypeError("Invalid data type, cannot be sent over the network")

    def receive(self, size: int) -> bytes:
        """
        Receive data from the connected server.
        
        Returns:
            bytes: The received data.
        """
        return self._client.recv(size)
        
    def open(self, address: Address) -> None:
        """
        Connect to the TCP server using the configured host and port.
        """
        self._client.connect(address)

    def close(self) -> None:
        """
        Close the client socket and disconnect from the server.
        """
        self._client.close()

    def start(self) -> None:
        """
        Run the client main loop.
        
        This method is intended to be implemented by subclasses to define
        the main client execution logic.
        """
        pass
