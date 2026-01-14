from typing import Any, Optional
import socket
from abc import ABC, abstractmethod


class InputEndpoint(ABC):
    
    @abstractmethod
    def send(self, packet: str) -> None:
        pass
    
    @abstractmethod
    def receive(self) -> Any:
        pass
    
    @abstractmethod
    def connect(self) -> None:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def run(self) -> None:
        pass


class BaseServer(InputEndpoint):

    def __init__(self, host: str, port: int) -> None:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host: str = host
        self.port: int = port
        self.connection: Optional[socket.socket] = None
        self.address: Optional[str] = None

        self.connect()

    def send(self, packet: str) -> None:
        self.connection.sendall(packet.encode())

    def receive(self) -> Any:
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


class BaseClient(InputEndpoint):

    def __init__(self, host: str, port: int) -> None:
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host: str = host
        self.port: int = port

        self.connect()

    def send(self, packet: str) -> None:
        self._client.sendall(packet.encode())

    def receive(self) -> Any:
        data = self._client.recv(1024)
        if data:
            return data
        return None

    def connect(self) -> None:
        self._client.connect((self.host, self.port))

    def disconnect(self) -> None:
        self._client.close()

    def run(self) -> None:
        pass
