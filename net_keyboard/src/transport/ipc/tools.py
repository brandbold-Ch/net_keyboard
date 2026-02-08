import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from struct import calcsize, unpack
from threading import Thread
from typing import (
    Callable,
    Dict,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    TypeAlias,
    Union,
)

from src.transport.base import NetworkChannel

FMT: str = "<H B Q"
SIZE: int = calcsize(FMT)


class FormatSpec(NamedTuple):
    fmt: str
    size: int


CB_EVENT: TypeAlias = Callable[[Tuple[int, int, int]], None]
CALLBACK_READER: TypeAlias = Callable[[int], str | bytes]
GLOBAL_FORMAT = FormatSpec(fmt=FMT, size=SIZE)
CHANNEL_ROLE = Literal["client", "server"]


def safe_read(reader: CALLBACK_READER, size: int) -> bytes:
    buffer = b""

    while len(buffer) < size:
        chunk = reader(size - len(buffer))
        if not chunk:
            raise EOFError("IPC Channel closed")
        buffer += chunk

    return buffer


def scan_keyboard() -> Dict[str, Path]:
    by_id = Path("/dev/input/by-id")
    keyboards: Dict[str, Path] = {}

    if not by_id.exists():
        return keyboards

    for dir in by_id.iterdir():
        if not dir.is_symlink():
            continue

        name = dir.name
        if not name.endswith("kbd"):
            continue

        try:
            target = dir.resolve()
        except FileNotFoundError:
            continue

        keyboards[name] = target

    return keyboards


class IPCStreamReader(ABC):
    @abstractmethod
    def device(self) -> Optional[str]:
        pass

    @abstractmethod
    def open(self, raw: CALLBACK_READER) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


AGENT_SOURCE: TypeAlias = Union[IPCStreamReader, str]


class ChannelFactory:
    @staticmethod
    def create(role: CHANNEL_ROLE) -> NetworkChannel:
        platform: str = os.name

        match platform:
            case "posix":
                if role == "client":
                    from src.transport.socket_unix import SocketUnixClient

                    return SocketUnixClient()

                elif role == "server":
                    from src.transport.socket_unix import SocketUnixServer

                    return SocketUnixServer()

            case "nt":
                if role == "client":
                    from src.transport.pipe import PipeClient

                    return PipeClient()

                elif role == "server":
                    from src.transport.pipe import PipeServer

                    return PipeServer()

            case _:
                raise RuntimeError(f"Unsupported OS: {platform}")


class IPCProcessLauncher(ABC):
    def __init__(self, client: AGENT_SOURCE, server: AGENT_SOURCE, shared: str) -> None:
        self.client = client
        self.server = server
        self.shared = shared

        self.base_path = Path(__file__).resolve().parents[2]

    def _cleanup(self, address: str) -> None:
        path = Path(address)
        if path.exists():
            path.unlink()

    def _set_readables(self) -> None:
        build_dir = self.base_path / "bin"
        build_dir.mkdir(parents=True, exist_ok=True)

        device_txt = build_dir / "device.txt"
        shared_txt = build_dir / "shared.txt"

        shared_txt.write_text(self.shared, encoding="utf-8")

        if isinstance(self.client, IPCStreamReader):
            device_txt.write_text(str(self.client.device()), encoding="utf-8")

        if isinstance(self.server, IPCStreamReader):
            device_txt.write_text(str(self.server.device()), encoding="utf-8")

    def _launch_process(self, exec: str) -> None:
        try:
            subprocess.Popen([self.base_path / exec])
        except Exception as e:
            print(f"{__file__} -> {e}")

    def _launch_channel(self, role: CHANNEL_ROLE, agent: AGENT_SOURCE) -> None:
        if isinstance(agent, str):
            self._launch_process(agent)

        elif isinstance(agent, IPCStreamReader):
            channel: NetworkChannel = ChannelFactory.create(role)
            channel.open(self.shared)

            Thread(target=agent.open, args=(channel.receive,)).start()

    def launch(self) -> None:
        if os.name == "posix":
            self._cleanup(self.shared)

        self._set_readables()

        self._launch_channel("server", self.server)
        self._launch_channel("client", self.client)


class KeyListener(IPCStreamReader):
    def __init__(
        self,
        on_press: Optional[CB_EVENT] = None,
        on_release: Optional[CB_EVENT] = None,
        device: Optional[str] = None,
    ) -> None:
        self._device = device
        self.on_press = on_press
        self.on_release = on_release
        self._running: bool = True

    def device(self) -> Optional[str]:
        return self._device

    def open(self, raw: CALLBACK_READER) -> None:
        spec = GLOBAL_FORMAT

        try:
            while self._running:
                data: bytes = safe_read(raw, spec.size)
                code, state, time = unpack(spec.fmt, data)

                if state == 1 and self.on_press:
                    self.on_press((code, state, time))

                elif state == 0 and self.on_release:
                    self.on_release((code, state, time))

        except Exception as e:
            print(f"KeyListener error: {e}")
        finally:
            self.close()

    def close(self) -> None:
        self._running = False
