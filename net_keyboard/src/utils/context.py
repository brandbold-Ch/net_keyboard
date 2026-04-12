"""Configuration management module for network keyboard application."""

import json
from dataclasses import asdict
from typing import Dict, Any

from src.ui.gui.models.client import Client
from src.ui.gui.models.server import Server

properties = "properties.json"


class AppContext:
    """
    Configuration class for managing server, client, and connection settings.

    This class handles loading and saving configuration data from/to a JSON file,
    providing default values and managing network connection parameters.
    """

    first_run: bool
    os: str
    client: Client
    server: Server
    kbds: Dict[str, Any]
    mice: Dict[str, Any]

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
        with open(properties, "r") as raw:
            data: Dict = json.load(raw)
            client_data = data["client"]
            server_data = data["server"]

        server_data["clients"] = list(
            map(lambda client: Client(**client), server_data["clients"])
        )

        self.first_run = data["first_run"]
        self.os = data["os"]
        self.client = Client(**client_data)
        self.server = Server(**server_data)

    def dump_config(self) -> None:
        """
        Save current configuration data to the JSON configuration file.

        Writes the current server, client, and connection settings to
        the config.json file with proper formatting.
        """
        with open(properties, "w") as raw:
            json.dump(
                {
                    "first_run": self.first_run,
                    "os": self.os,
                    "client": asdict(self.client),
                    "server": asdict(self.server),
                },
                fp=raw,
                indent=4,
            )


def get_context() -> AppContext:
    """
    Create and return a new configuration instance.

    Returns:
        AppContext: A new configuration instance with loaded settings.
    """
    return AppContext()


context = get_context()
