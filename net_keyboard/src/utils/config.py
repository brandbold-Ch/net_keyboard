"""Configuration management module for network keyboard application."""
import json
from typing import Dict, List


k1 = "server"
k2 = "client"
file = "config.json"


class Confing:
    """
    Configuration class for managing server, client, and connection settings.
    
    This class handles loading and saving configuration data from/to a JSON file,
    providing default values and managing network connection parameters.
    """

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5000

    CLIENT_HOST: str = "127.0.0.1"
    CLIENT_PORT: int = 5000

    CONNECTIONS: List[Dict[str, int]] = []

    def __init__(self) -> None:
        """
        Initialize the configuration manager and load settings from file.
        """
        self.load_config()

    def load_config(self) -> None:
        """
        Load configuration data from the JSON configuration file.
        
        Reads the config.json file and updates the instance attributes
        with server, client, and connection settings from the file.
        """
        with open(file, "r") as raw:
            data: Dict = json.load(raw)

        self.SERVER_HOST = data[k1]["host"]
        self.SERVER_PORT = data[k1]["port"]

        self.CLIENT_HOST = data[k2]["host"]
        self.CLIENT_PORT = data[k2]["port"]

        self.CONNECTIONS = data["connections"]

    def dump_config(self) -> None:
        """
        Save current configuration data to the JSON configuration file.
        
        Writes the current server, client, and connection settings to
        the config.json file with proper formatting.
        """
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
    """
    Create and return a new configuration instance.
    
    Returns:
        Confing: A new configuration instance with loaded settings.
    """
    return Confing()


e = config()
