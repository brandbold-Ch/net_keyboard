import ctypes
from ctypes import wintypes

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


def obtener_nombre_dispositivo(hDevice):
    size = wintypes.UINT(0)

    # Obtener tamaño necesario
    user32.GetRawInputDeviceInfoW(hDevice, RIDI_DEVICENAME, None, ctypes.byref(size))

    buffer = ctypes.create_unicode_buffer(size.value)

    # Obtener nombre
    user32.GetRawInputDeviceInfoW(hDevice, RIDI_DEVICENAME, buffer, ctypes.byref(size))

    return buffer.value


def listar_dispositivos_dict():
    size = ctypes.sizeof(RAWINPUTDEVICELIST)
    num_devices = wintypes.UINT()

    # Obtener número de dispositivos
    user32.GetRawInputDeviceList(None, ctypes.byref(num_devices), size)

    devices_array = (RAWINPUTDEVICELIST * num_devices.value)()

    user32.GetRawInputDeviceList(devices_array, ctypes.byref(num_devices), size)

    dispositivos = {}

    for i in range(num_devices.value):
        dev = devices_array[i]

        if dev.dwType == RIM_TYPEMOUSE:
            tipo = "mouse"
        elif dev.dwType == RIM_TYPEKEYBOARD:
            tipo = "keyboard"
        else:
            tipo = "hid"

        nombre = obtener_nombre_dispositivo(dev.hDevice)

        # Simulación tipo Linux
        key = f"event{i}"

        dispositivos[key] = {"tipo": tipo, "ruta": nombre, "handle": int(dev.hDevice)}

    return dispositivos


if __name__ == "__main__":
    dispositivos = listar_dispositivos_dict()

    for k, v in dispositivos.items():
        print(f"{k}:")
        print(f"  tipo: {v['tipo']}")
        print(f"  ruta: {v['ruta']}")
        print(f"  handle: {v['handle']}")
        print()
