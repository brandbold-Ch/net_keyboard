import platform
from typing import Any, Dict

from .base import IODevice


class DeviceResolver:
    @staticmethod
    def scan_devices(device: IODevice) -> Dict[str, Any]:
        match platform.system():
            case "Linux":
                from .linux import LinuxInputDevice

                return LinuxInputDevice.list_devices(device)

            case "Windows":
                from .windows import WindowsInputDevice

                return WindowsInputDevice.list_devices(device)

            case _:
                return {}
