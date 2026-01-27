"""Server module for TCP communication."""
from typing import Optional, Union
from src.socket.base import NetworkChannel, Address
import socket


class TcpServer(NetworkChannel):
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
        self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.c_socket: Optional[socket.socket] = None

        self.open((host, port))       

    def send(self, packet: Union[str, bytes]) -> None:
        """
        Send data packet to the connected client.
        
        Args:
            packet (Union[str, bytes]): The data packet to send as a string or bytes.
            
        Raises:
            ConnectionError: If no active connection is available.
        """
        if self.c_socket is None:
            raise ConnectionError("No active connection. Cannot send packets")

        if isinstance(packet, str):
            self.c_socket.sendall(packet.encode())
        
        elif isinstance(packet, bytes):
            self.c_socket.sendall(packet)
            
        else:
            raise TypeError("Invalid data type, cannot be sent over the network")
        
    def receive(self, size: int) -> bytes:
        """
        Receive data from the connected client.
        
        Returns:
            bytes: The received data.
            
        Raises:
            ConnectionError: If no active connection is available.
        """
        if self.c_socket is None:
            self.c_socket =  self.s_socket.accept()[0]
        return self.c_socket.recv(size)

    def open(self, address: Address) -> None:
        """
        Establish the server connection and wait for client connections.
        
        Binds the server socket to the specified host and port, starts listening,
        and accepts the first incoming client connection.
        """
        self.s_socket.bind(address)
        self.s_socket.listen()

    def close(self) -> None:
        """
        Close the server socket and disconnect from clients.
        """
        self.s_socket.close()

    def start(self) -> None:
        """
        Run the server main loop.
        
        This method is intended to be implemented by subclasses to define
        the main server execution logic.
        """
        pass
