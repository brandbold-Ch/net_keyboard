from .client.home import ClientHomeView
from .client.setup import ClientSetupView
from .server.home import ServerHomeView
from .server.setup import ServerSetupView
from .startup import StartupView

__all__ = [
    "ClientSetupView",
    "StartupView",
    "ServerSetupView",
    "ClientHomeView",
    "ServerHomeView",
]
