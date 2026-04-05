from dataclasses import dataclass

from .client import Client


@dataclass
class Server:
    host: str
    port: int
    clients: list[Client]
    pool: int
    keyboard: str
    mouse: str
    save_connection: bool
    auto_reconnect: bool
