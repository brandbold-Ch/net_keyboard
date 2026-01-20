from typing import Optional
from src.tcp import BaseServer, BaseClient
import threading
from src.backends.base import KeyboardTypeEvent, MouseTypeEvent
from src.backends.pynput import PynputKeyboardEvent, PynputMouseEvent, PynputKey
from pynput.keyboard import Key, KeyCode


class PynputServer(BaseServer):
    
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self.keyboard_event = PynputKeyboardEvent()
        self.mouse_event = PynputMouseEvent()

        self.keyboard_event.add_callback(self.keyboard_press, KeyboardTypeEvent.PRESS)

    def keyboard_press(self, key: PynputKey) -> None:
        if isinstance(key, Key): 
            self.send(key.name)
        
        elif isinstance(key, KeyCode):
            self.send(key.char)

    def run(self) -> None:
        threading.Thread(target=self.keyboard_event.listen).start()


class PynputClient(BaseClient):

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self.keyboard_event = PynputKeyboardEvent()
        self.mouse_event = PynputMouseEvent()

    def run(self) -> None:
        while True:
            data: Optional[str] = self.receive()
            print(data)

            if data:
                self.keyboard_event.insert(data)
