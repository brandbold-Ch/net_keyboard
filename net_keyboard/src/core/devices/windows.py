import ctypes
from ctypes import wintypes
from typing import Any, Dict

from .base import InputDeviceProvider, IODevice

user32 = ctypes.windll.user32

RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2

RIDI_DEVICENAME = 0x20000007


class RAWINPUTDEVICELIST(ctypes.Structure):
    _fields_ = [
        ("hDevice", wintypes.HANDLE),
        ("dwType", wintypes.DWORD),
    ]


TYPE_MAP = {
    IODevice.KEYBOARD: RIM_TYPEKEYBOARD,
    IODevice.MOUSE: RIM_TYPEMOUSE,
    IODevice.JOYSTICK: RIM_TYPEHID,
}


class WindowsInputDevice(InputDeviceProvider):
    @classmethod
    def _device_names(cls, hDevice) -> Any:
        size = wintypes.UINT(0)
        user32.GetRawInputDeviceInfoW(
            hDevice, RIDI_DEVICENAME, None, ctypes.byref(size)
        )
        buffer = ctypes.create_unicode_buffer(size.value)
        user32.GetRawInputDeviceInfoW(
            hDevice, RIDI_DEVICENAME, buffer, ctypes.byref(size)
        )

        return buffer.value

    @classmethod
    def list_devices(cls, device: IODevice) -> Dict[str, Any]:
        size = ctypes.sizeof(RAWINPUTDEVICELIST)
        n_devices = wintypes.UINT()
        user32.GetRawInputDeviceList(None, ctypes.byref(n_devices), size)
        devices_array = (RAWINPUTDEVICELIST * n_devices.value)()
        user32.GetRawInputDeviceList(devices_array, ctypes.byref(n_devices), size)
        devices: Dict[str, Any] = {}

        for n in range(n_devices.value):
            dev = devices_array[n]
            name = cls._device_names(dev.hDevice)

            if dev.dwType != TYPE_MAP.get(device):
                continue

            devices[name] = dev.hDevice
        return devices
