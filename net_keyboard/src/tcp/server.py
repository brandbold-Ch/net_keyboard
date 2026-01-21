"""Server module for TCP communication."""
from typing import Optional, Union
from src.tcp.base import TCP
import socket


class BaseServer(TCP):
    """
    Base TCP server class for handling network connections.
    
    This class extends the TCP base class and provides server-side functionality
    for accepting and managing client connections over TCP.
    """

    def __init__(self, host: str, port: int) -> None:
        """
        Initialize the TCP server.
        
        Args:
            host (str): The hostname or IP address to bind the server to.
            port (int): The port number to listen on.
        """
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host: str = host
        self.port: int = port
        self.connection: Optional[socket.socket] = None
        self.address: Optional[str] = None

        self.connect()       

    def send(self, packet: Union[str, bytes]) -> None:
        """
        Send data packet to the connected client.
        
        Args:
            packet (Union[str, bytes]): The data packet to send as a string or bytes.
            
        Raises:
            ConnectionError: If no active connection is available.
        """
        if self.connection is None:
            raise ConnectionError("No active connection. Cannot send packets")

        if isinstance(packet, str):
            self.connection.sendall(packet.encode())
        
        elif isinstance(packet, bytes):
            self.connection.sendall(packet)
            
        else:
            raise TypeError("Invalid data type, cannot be sent over the network")
        
    def receive(self) -> bytes:
        """
        Receive data from the connected client.
        
        Returns:
            bytes: The received data.
            
        Raises:
            ConnectionError: If no active connection is available.
        """
        if self.connection is None:
            raise ConnectionError("No active connection. Cannot receive packets")
        
        return self.connection.recv(1024)

    def connect(self) -> None:
        """
        Establish the server connection and wait for client connections.
        
        Binds the server socket to the specified host and port, starts listening,
        and accepts the first incoming client connection.
        """
        self._server.bind((self.host, self.port))
        self._server.listen()
        self.connection, self.address = self._server.accept()

    def disconnect(self) -> None:
        """
        Close the server socket and disconnect from clients.
        """
        self._server.close()

    def run(self) -> None:
        """
        Run the server main loop.
        
        This method is intended to be implemented by subclasses to define
        the main server execution logic.
        """
        pass
