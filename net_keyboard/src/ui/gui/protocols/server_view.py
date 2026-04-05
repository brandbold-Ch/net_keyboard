from typing import Callable, Protocol


class ServerViewProtocol(Protocol):
    def on_submit(self, handler: Callable[[str, str], None]) -> None:
        pass
