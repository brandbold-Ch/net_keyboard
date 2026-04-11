from pathlib import Path
from typing import Any, Dict, Generator, Optional

from .base import InputDeviceProvider, IODevice


class LinuxInputDevice(InputDeviceProvider):
    devin: Path = Path("/dev/input")

    @classmethod
    def list_devices(cls, device: IODevice) -> Dict[str, Any]:
        entry: Optional[Path] = cls._entrypoint()
        devices: Dict[str, Path] = {}

        if entry is None:
            raise RuntimeError("Input Devices Not Founds")

        for dir in cls._iter_path(entry):
            name = dir.name

            if not name.endswith(device.value):
                continue

            try:
                target = dir.resolve()
            except FileNotFoundError:
                continue

            devices[name] = target
        return devices

    @staticmethod
    def _iter_path(path: Path) -> Generator[Path, None, None]:
        return path.iterdir()

    @classmethod
    def _entrypoint(cls) -> Optional[Path]:
        for path in cls._iter_path(cls.devin):
            if path.name.startswith("by"):
                return path
        return None
