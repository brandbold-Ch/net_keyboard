import sys
from src.utils.config import e
from src.keyboard.main import KeyboardServer, KeyboardClient
import threading


def k1() -> None:
    k = KeyboardServer()
    k.keyboard_event.add_capturer(k.send)


def k2() -> None:
    k = KeyboardClient()
    while True:
        print("\nKeyboard Event: ", k.receive())


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
