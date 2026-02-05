import os

from src.backends.base import KeyboardTypeEvent
from src.backends.keyboard import NtEventListener, PosixEventListener
from src.core.keyboard import MKVClient, MKVServer
from src.utils.config import e


def on_press(codes):
    print("Pressed:", codes)


def on_release(codes):
    print("Released:", codes)


OS = os.name

if OS == "posix":
    ev = PosixEventListener()
    ev.add_subscriber(on_press, kind=KeyboardTypeEvent.PRESS)
    ev.add_subscriber(on_release, kind=KeyboardTypeEvent.RELEASE)
    ev.listen()

elif OS == "nt":
    ev = NtEventListener()
    ev.add_subscriber(on_press, kind=KeyboardTypeEvent.PRESS)
    ev.add_subscriber(on_release, kind=KeyboardTypeEvent.RELEASE)
    ev.listen()


def k1() -> None:
    server = MKVServer(e.SERVER_HOST, e.SERVER_PORT, PosixEventListener())
    server.run()


def k2() -> None:
    client = MKVClient(e.CLIENT_HOST, e.CLIENT_PORT, PosixEventListener())
    client.run()


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
