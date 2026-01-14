import json
from typing import Dict, List, Optional


k1 = "server"
k2 = "client"
file = "config.json"


class Confing:

    SERVER_HOST: Optional[str] = None
    SERVER_PORT: Optional[int] = None

    CLIENT_HOST: Optional[str] = None
    CLIENT_PORT: Optional[int] = None

    CONNECTIONS: List[Dict[str, int]] = None

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
                "server": {
                    "host": self.SERVER_HOST,
                    "port": self.SERVER_PORT
                },
                "client": {
                    "host": self.CLIENT_HOST,
                    "port": self.CLIENT_PORT
                },
                "connections": self.CONNECTIONS
            }, fp=raw, indent=2)


def config() -> Confing:
    return Confing()


e = config()
