from typing import Any, Callable
import evdev
from src.backends.base import KeyboardBackend, MouseBackend
from evdev import InputDevice, categorize, ecodes


EvdevKey = object
EvdevButton = object


class EvdevKeyboardEvent(KeyboardBackend[EvdevKey]):
    
    def __init__(self) -> None:
        pass

    def on_press(self, key: EvdevKey) -> None:
        pass

    def on_release(self, key: EvdevKey) -> None:
        pass
    
    def add_callback(self, cb: Callable[..., None]) -> None:
        pass
    
    def notify_callbacks(self, key: EvdevKey) -> None:
        pass

    def listen(self) -> None:
        pass


class EvdevMouseEvent(MouseBackend[EvdevButton]):
    
    def __init__(self) -> None:
        pass

    def on_move(
        self,
        mouse_position_x: int, 
        mouse_position_y: int
    ) -> None:
        pass
    
    def on_click(
        self, 
        mouse_position_x: int, 
        mouse_position_y: int, 
        button: EvdevButton, 
        pressed: bool
    ) -> None:
        pass
    
    def on_scroll(
        self,
        mouse_position_x: int, 
        mouse_position_y: int, 
        scroll_change_x: int, 
        scroll_change_y: int
    ) -> None:
        pass

    def add_callback(self, cb: Callable[..., None]) -> None:
        pass
    
    def notify_callbacks(self, **kwargs: object) -> None:
        pass

    def listen(self) -> None:
        pass
