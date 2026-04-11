from typing import Callable, Protocol


class ClientViewProtocol(Protocol):
    """
    Protocol for the client view in the GUI.

    This protocol defines the expected behavior for client views, including
    the submission of data through a handler function.

    Methods:
        on_submit(handler: Callable[[str, int, bool, bool], None]) -> None:
            Registers a handler function to be called when the user submits data.
            The handler receives the following parameters:
                - str: The host address.
                - int: The port number.
                - bool: A flag indicating whether encryption is enabled.
                - bool: A flag indicating whether compression is enabled.
    """

    def on_submit(self, handler: Callable[[str, int, bool, bool], None]) -> None:
        pass
