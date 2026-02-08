import os

from src.backends.base import KeyboardTypeEvent
from src.backends.keyboard import EventListener
from src.transport.ipc.tools import IPCProcessLauncher, KeyListener, scan_keyboard
from src.utils.config import e


def on_press(codes):
    print("Pressed:", codes)


def on_release(codes):
    print("Released:", codes)


listener: EventListener
OS = os.name


def launcher_factory() -> IPCProcessLauncher:
    kbds = scan_keyboard() # usb-1bcf_08a0-event-kbd usb-BY_Tech_Gaming_Keyboard-event-kbd

    return (
        IPCProcessLauncher(
            client="bin/socket_unix/klevent"
            if OS == "posix"
            else "bin/pipe/kwevent.exe",
            server=KeyListener(
                on_press=listener.on_press,
                on_release=listener.on_release,
                device=str(kbds["usb-BY_Tech_Gaming_Keyboard-event-kbd"]),
            ),
            shared="/tmp/keyboard_ipc.sock"
            if OS == "posix"
            else r"\\.\pipe\keyboard_ipc",
        )
        if OS == "posix"
        else IPCProcessLauncher(
            server="bin/socket_unix/klevent"
            if OS == "posix"
            else "bin/pipe/kwevent.exe",
            client=KeyListener(
                on_press=listener.on_press, on_release=listener.on_release
            ),
            shared="/tmp/keyboard_ipc.sock"
            if OS == "posix"
            else r"\\.\pipe\keyboard_ipc",
        )
    )


listener = EventListener(launcher_factory)
listener.add_subscriber(on_press, kind=KeyboardTypeEvent.PRESS)
listener.add_subscriber(on_release, kind=KeyboardTypeEvent.RELEASE)
listener.listen()


"""def k1() -> None:
    server = MKVServer(e.SERVER_HOST, e.SERVER_PORT, PosixEventListener())
    server.run()


def k2() -> None:
    client = MKVClient(e.CLIENT_HOST, e.CLIENT_PORT, PosixEventListener())
    client.run()
"""

"""
def main() -> None:
    args = sys.argv[1:]

    if args[0] == "server":
        e.SERVER_HOST = args[1]
        e.SERVER_PORT = int(args[2])
        e.dump_config()

        threading.Thread(target=k1).start()

    elif args[0] == "client":
        e.CLIENT_HOST = args[1]
        e.CLIENT_PORT = int(args[2])
        e.dump_config()

        threading.Thread(target=k2).start()


if __name__ == "__main__":
    main()
"""
# w = sys.argv

"""sleep(5)

if w[1] == "0":
    k1()

elif w[1] == "1":
    k2()
"""
