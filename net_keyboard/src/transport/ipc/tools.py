"""IPC tools and helpers for launching and communicating with agents.

This module provides utilities for inter-process communication used by the
project. It includes a small format specification for serialized keyboard
events, safe read helpers, platform-aware channel factory helpers, and
classes to launch and manage helper processes that bridge local input
devices to the main application.
"""

import platform
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from struct import calcsize, unpack
from threading import Thread
from typing import (
    Callable,
    Dict,
    Generator,
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
SUFFIX = Optional[str]
PREFIX = Optional[str]

system: str = platform.system()


def safe_read(reader: CALLBACK_READER, size: int) -> bytes:
    """Read exactly ``size`` bytes from a reader callable.

    The provided ``reader`` callable is expected to accept an integer size
    and return either a bytes object or an empty value on EOF. This helper
    accumulates bytes until the requested size is reached or raises EOFError
    when the reader returns no data.

    Args:
        reader: Callable that reads up to ``n`` bytes and returns bytes or
            an empty value when the stream is closed.
        size: Number of bytes to read.

    Returns:
        A bytes object of length ``size``.

    Raises:
        EOFError: If the reader returns no data before the requested amount
            of bytes has been accumulated.
    """

    buffer = b""

    while len(buffer) < size:
        chunk = reader(size - len(buffer))
        if not chunk:
            raise EOFError("Reading Error")
        buffer += chunk

    return buffer


class Devices:
    devin: Path = Path("/dev/input")

    @staticmethod
    def _iter_path(path: Path) -> Generator[Path, None, None]:
        return path.iterdir()

    @classmethod
    def _input(cls, prefix: PREFIX = None, suffix: SUFFIX = None) -> Dict[str, Path]:
        entry: Optional[Path] = cls.find_entry()
        devices: Dict[str, Path] = {}

        if entry is None:
            raise RuntimeError("Input Devices Not Founds")

        for dir in cls._iter_path(entry):
            name = dir.name

            if prefix:
                if not name.startswith(prefix):
                    continue
            if suffix:
                if not name.endswith(suffix):
                    continue

            try:
                target = dir.resolve()
            except FileNotFoundError:
                continue

            devices[name] = target

        return devices

    @classmethod
    def _uinput(cls, prefix: PREFIX = None, suffix: SUFFIX = None) -> Dict[str, Path]:
        return {}

    @classmethod
    def find_entry(cls) -> Optional[Path]:
        for dir in cls._iter_path(cls.devin):
            if not dir.name.startswith("by"):
                continue
            return dir

    @classmethod
    def scan_devices(
        cls,
        device_type: Literal["IN", "UIN"],
        prefix: PREFIX = None,
        suffix: SUFFIX = None,
    ) -> Dict[str, Path]:
        match device_type:
            case "IN":
                return cls._input(prefix, suffix)
            case "UIN":
                return cls._uinput(prefix, suffix)


class IPCStreamReader(ABC):
    @property
    @abstractmethod
    def device(self) -> Optional[str]:
        """Return the device path this reader will read from, if any.

        Concrete implementations may return None when there is no single
        device path associated with the reader (for example when the reader
        is implemented by an external process).
        """
        pass

    @abstractmethod
    def open(self, raw: CALLBACK_READER) -> None:
        """Start reading from the provided raw callback reader.

        Implementations should call ``raw(n)`` repeatedly to obtain bytes
        from the underlying transport and process them accordingly. This
        method is typically run inside a dedicated thread.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Request the reader to stop and clean up resources."""
        pass


AGENT_SOURCE: TypeAlias = Union[IPCStreamReader, str]


class ChannelFactory:
    @classmethod
    def create(cls, role: CHANNEL_ROLE) -> NetworkChannel:
        """Create a platform-specific NetworkChannel for the given role.

        Args:
            role: Either "client" or "server" indicating the desired
                channel role.

        Returns:
            An instance of ``NetworkChannel`` appropriate for the running
            operating system and role.

        Raises:
            RuntimeError: When the current OS or role is unsupported.
        """

        match system:
            case "Linux":
                return cls._linux_channel(role)

            case "Windows":
                return cls._windows_channel(role)

            case _:
                raise RuntimeError(f"Unsupported OS: {system}")

    @staticmethod
    def _linux_channel(role: str) -> NetworkChannel:
        """Build a Linux-specific NetworkChannel implementation.

        This currently maps to Unix domain sockets for both client and
        server roles.
        """

        if role == "client":
            from src.transport.socket_unix import SocketUnixClient

            return SocketUnixClient()

        elif role == "server":
            from src.transport.socket_unix import SocketUnixServer

            return SocketUnixServer()

        else:
            raise TypeError(f"(Posix) Unsupported Role: {role}")

    @staticmethod
    def _windows_channel(role: str) -> NetworkChannel:
        """Build a Windows-specific NetworkChannel implementation.

        On Windows this maps to named pipe based implementations.
        """

        if role == "client":
            from src.transport.pipe import PipeClient

            return PipeClient()

        elif role == "server":
            from src.transport.pipe import PipeServer

            return PipeServer()

        else:
            raise TypeError(f"(Nt) Unsupported Role: {role}")


class IPCProcessLauncher(ABC):
    def __init__(self, client: AGENT_SOURCE, server: AGENT_SOURCE, shared: str) -> None:
        self.client = client
        self.server = server
        self.shared = shared

        if getattr(sys, "frozen", False):
            # Ejecutándose en PyInstaller
            self.base_path = Path(getattr(sys, "_MEIPASS"))
        else:
            # Desarrollo normal
            self.base_path = Path(__file__).resolve().parents[2]

    def _cleanup(self, address: str) -> None:
        """Remove any pre-existing address file (Unix domain socket).

        This is a small helper to avoid "address already in use" errors when
        re-creating a Unix domain socket file on POSIX systems.
        """

        path = Path(address)
        if path.exists():
            path.unlink()

    def _set_filesync(self) -> None:
        """Prepare helper files in the project's bin directory.

        Writes a small ``shared.txt`` containing the address used for IPC and
        optionally writes a ``device.txt`` file when a device path is known.
        These files are intended to be consumed by helper native binaries or
        manual inspection during debugging.
        """

        def get_device(agent: AGENT_SOURCE) -> Optional[str]:
            return (
                getattr(agent, "device") if isinstance(agent, IPCStreamReader) else None
            )

        bin_path = self.base_path / "bin"
        d_path = bin_path / "device.txt"
        device = get_device(self.client) or get_device(self.server)

        (bin_path / "shared.txt").write_text(self.shared, encoding="utf-8")

        if device:
            d_path.write_text(device, encoding="utf-8")

    def _launch_process(self, exec: str) -> None:
        """Start an external helper process from the project's bin folder.

        Any exceptions are caught and printed to aid debugging.
        """

        try:
            subprocess.Popen([self.base_path / exec])
        except Exception as e:
            print(f"{__file__} -> {e}")

    def _launch_channel(self, role: CHANNEL_ROLE, agent: AGENT_SOURCE) -> None:
        """Launch either an in-process IPCStreamReader or an external agent.

        If ``agent`` implements ``IPCStreamReader`` it will be wired to a
        platform channel created by ChannelFactory and run in a background
        thread. If ``agent`` is a string it's assumed to be an executable name
        under the project's ``bin`` directory and will be launched as a
        separate process.
        """

        if isinstance(agent, IPCStreamReader):
            channel: NetworkChannel = ChannelFactory.create(role)
            channel.open(self.shared)

            Thread(target=agent.open, args=(channel.receive,)).start()

        elif isinstance(agent, str):
            self._launch_process(agent)

    def launch(self) -> None:
        """Launch both server and client agents and prepare shared artifacts.

        On POSIX systems the shared address file is removed before launching
        to avoid bind errors. The method then prepares helper files and
        starts the server and client agents according to provided sources.
        """

        if system == "Linux":
            self._cleanup(self.shared)

        self._set_filesync()

        self._launch_channel("server", self.server)
        self._launch_channel("client", self.client)


class KeyListener(IPCStreamReader):
    def __init__(
        self,
        on_press: Optional[CB_EVENT] = None,
        on_release: Optional[CB_EVENT] = None,
        device: Optional[str] = None,
    ) -> None:
        self.on_press = on_press
        self.on_release = on_release
        self._device = device
        self._running: bool = True

    @property
    def device(self) -> Optional[str]:
        """Return the device path associated with this KeyListener.

        May be None when the listener is not tied to a single device.
        """

        return self._device

    def open(self, raw: CALLBACK_READER) -> None:
        """Start reading events from the provided raw reader.

        This method runs a loop that reads fixed-size event packets using
        GLOBAL_FORMAT and dispatches them to the configured on_press and
        on_release callbacks. The loop terminates when ``close`` is called
        or when an exception occurs.
        """

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
        """Stop the reader loop and release resources.

        Setting the internal running flag to False will cause the read loop
        in ``open`` to exit gracefully on the next iteration.
        """

        self._running = False
