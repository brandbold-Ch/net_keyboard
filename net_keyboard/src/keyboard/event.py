from typing import Callable, List
from pynput import keyboard
from pynput.keyboard import Key, KeyCode


class KeyboardEvent:

    def __init__(self) -> None:
        self.capturers: List[Callable] = []

    def _inject_in_capturers(self, key: int) -> None:
        for capturer in self.capturers:
            capturer(str(key))

    def _on_press(self, key: Key | KeyCode) -> None:
        self._inject_in_capturers(key.vk)

    def _on_release(self, key: Key | KeyCode) -> None:
        pass

    def add_capturer(self, func: Callable) -> None:
        self.capturers.append(func)

    def listen(self) -> None:
        listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        listener.start()
        listener.join()
