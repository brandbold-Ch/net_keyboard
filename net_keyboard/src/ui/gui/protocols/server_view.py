from typing import Callable, Protocol


class ServerViewProtocol(Protocol):
    """
    Protocol for server view interactions.

    This protocol defines the interface for handling server-related
    events in the GUI. It ensures that any class implementing this
    protocol provides a method to handle form submissions.

    Methods:
        on_submit(handler: Callable[[str, str], None]): Registers a callback
            to handle server setup submissions. The callback receives two
            string arguments representing the server's address and port.
    """

    def on_submit(self, handler: Callable[[str, str], None]) -> None:
        """
        Register a callback for server setup submissions.

        Args:
            handler (Callable[[str, str], None]): A function that takes two
                string arguments (server address and port) and performs
                the necessary actions upon form submission.
        """
        pass
