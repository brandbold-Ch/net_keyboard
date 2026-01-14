from src.keyboard.event import KeyboardEvent
from src.tcp.base import BaseServer, BaseClient
from src.utils.config import e
import  threading


class KeyboardServer(BaseServer):

    def __init__(self) -> None:
        super().__init__(e.SERVER_HOST, e.SERVER_PORT)
        self.keyboard_event = KeyboardEvent()

        threading.Thread(target=self.keyboard_event.listen).start()


class KeyboardClient(BaseClient):

    def __init__(self) -> None:
        super().__init__(e.CLIENT_HOST, e.CLIENT_PORT)


"""def k1():
    k = KeyboardServer()
    k.keyboard_event.add_capturer(k.send)


def k2():
    k = KeyboardClient()
    while True:
        print("\nKeyboard Event: ", k.receive())

"""
"""t1 = threading.Thread(target=k1)
t1.start()

time.sleep(0.5)

t2 = threading.Thread(target=k2)
t2.start()
"""