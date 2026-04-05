from src.ui.gui.protocols import ServerViewProtocol
from src.ui.gui.services import ServerService


class ServerController:
    def __init__(self, view: ServerViewProtocol) -> None:
        self.view = view
        self.service = ServerService()

        self._connect()

    def _connect(self) -> None:
        self.view.on_submit(self.handle_submit)

    def handle_submit(self, keyboard: str, mouse: str) -> None:
        self.service.set_keyboard(keyboard)
        self.service.set_mouse(mouse)
        self.service.start_server()
