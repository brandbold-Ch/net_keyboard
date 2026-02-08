from src.transport.base import Address, NetworkChannel


class PipeServer(NetworkChannel):
    def send(self, packet: str | bytes) -> None:
        raise NotImplementedError()

    def receive(self, size: int) -> str | bytes:
        raise NotImplementedError()

    def open(self, address: Address) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()
