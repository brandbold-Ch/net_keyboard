from src.ui.gui.protocols import ClientViewProtocol
from src.ui.gui.services import ClientService


class ClientController:
    def __init__(self, view: ClientViewProtocol) -> None:
        self.view = view
        self.service = ClientService()

        self._connect()

    def _connect(self) -> None:
        self.view.on_submit(self.handle_submit)

    def handle_submit(self, host: str, port: int, save: bool, reconnect: bool) -> None:
        self.service.set_host(host)
        self.service.set_port(port)
        self.service.set_save_connection(save)
        self.service.set_auto_reconnect(reconnect)
