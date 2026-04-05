from typing import Callable, Protocol


class ClientViewProtocol(Protocol):
    def on_submit(self, handler: Callable[[str, int, bool, bool], None]) -> None:
        pass
