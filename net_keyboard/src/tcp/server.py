from typing import Any, Optional
from src.tcp.base import TCP
import socket


class BaseServer(TCP):

    def __init__(self, host: str, port: int) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host: str = host
        self.port: int = port
        self.connection: Optional[socket.socket] = None
        self.address: Optional[str] = None

        self.connect()       

    def send(self, packet: str) -> None:
        if self.connection is None:
            raise ConnectionError("No active connection. Cannot send packets")

        self.connection.sendall(packet.encode())

    def receive(self) -> Any:
        if self.connection is None:
            raise ConnectionError("No active connection. Cannot receive packets")
        
        data = self.connection.recv(1024)
        if data:
            return data.decode()
        return None

    def connect(self) -> None:
        self._server.bind((self.host, self.port))
        self._server.listen()
        self.connection, self.address = self._server.accept()

    def disconnect(self) -> None:
        self._server.close()

    def run(self) -> None:
        pass
