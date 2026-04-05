from dataclasses import dataclass


@dataclass
class Client:
    host: str
    port: int
    save_connection: bool
    auto_reconnect: bool
