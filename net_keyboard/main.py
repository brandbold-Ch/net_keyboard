import sys
from src.utils.config import e
import threading
from src.adapters.keyboard.pynput import PynputServer, PynputClient


def k1() -> None:
    server = PynputServer(e.SERVER_HOST, e.SERVER_PORT)
    server.run()

def k2() -> None:
    client = PynputClient(e.CLIENT_HOST, e.CLIENT_PORT)
    client.run()


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

