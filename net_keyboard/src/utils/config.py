import json
from typing import Dict, List


k1 = "server"
k2 = "client"
file = "config.json"


class Confing:

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5000

    CLIENT_HOST: str = "127.0.0.1"
    CLIENT_PORT: int = 5000

    CONNECTIONS: List[Dict[str, int]] = []

    def __init__(self) -> None:
        self.load_config()

    def load_config(self) -> None:
        with open(file, "r") as raw:
            data: Dict = json.load(raw)

        self.SERVER_HOST = data[k1]["host"]
        self.SERVER_PORT = data[k1]["port"]

        self.CLIENT_HOST = data[k2]["host"]
        self.CLIENT_PORT = data[k2]["port"]

        self.CONNECTIONS = data["connections"]

    def dump_config(self) -> None:
        with open(file, "w") as raw:
            json.dump({
                k1: {
                    "host": self.SERVER_HOST,
                    "port": self.SERVER_PORT
                },
                k2: {
                    "host": self.CLIENT_HOST,
                    "port": self.CLIENT_PORT
                },
                "connections": self.CONNECTIONS
            }, 
            fp=raw, 
            indent=2
        )


def config() -> Confing:
    return Confing()


e = config()
