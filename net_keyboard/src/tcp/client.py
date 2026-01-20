from typing import Any
from src.tcp.base import TCP
import socket


class BaseClient(TCP):

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
            return data.decode()
        return None

    def connect(self) -> None:
        self._client.connect((self.host, self.port))

    def disconnect(self) -> None:
        self._client.close()

    def run(self) -> None:
        pass
