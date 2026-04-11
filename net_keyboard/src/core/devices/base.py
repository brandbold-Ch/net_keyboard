from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict


class IODevice(Enum):
    KEYBOARD = "kbd"
    MOUSE = "mouse"
    JOYSTICK = "js"


class DeviceProvider(ABC):
    @classmethod
    @abstractmethod
    def list_devices(cls, device: IODevice) -> Dict[str, Any]:
        pass


class InputDeviceProvider(DeviceProvider):
    pass


class OutputDeviceProvider(DeviceProvider):
    pass
