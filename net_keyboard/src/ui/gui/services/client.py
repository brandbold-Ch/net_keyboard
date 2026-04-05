from src.utils.context import context


class ClientService:
    def set_host(self, host: str) -> None:
        context.client.host = host

    def set_port(self, port: int) -> None:
        context.client.port = port

    def set_save_connection(self, status: bool) -> None:
        context.client.save_connection = status

    def set_auto_reconnect(self, status: bool) -> None:
        context.client.auto_reconnect = status
