import sys
from src.utils.config import e
import threading
from src.adapters.keyboard.pynput import PynputServer, PynputClient


"""def k1() -> None:
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
"""

def on_press(key):
    try:
        if isinstance(key, keyboard.KeyCode):
            print("KeyCode pressed: ", {
                'char': key.char,
                'vk': key.vk
            })
            
        elif isinstance(key, keyboard.Key):
            print("Key pressed: ", {
                'name': key.name,
                'value': key.value
            })
            
    except AttributeError:
        print('special key {0} pressed'.format(
            key))
        
    
from pynput import keyboard
listener = keyboard.Listener(
    on_press=on_press)
listener.start()
