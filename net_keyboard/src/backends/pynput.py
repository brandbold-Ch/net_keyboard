from typing import Callable, Any, Union
from src.backends.base import KeyboardBackend, MouseBackend, MouseTypeEvent,\
    KeyboardTypeEvent, KeyboardCallList, MouseCallList
from pynput import keyboard
from pynput import mouse
from pynput.keyboard import Key, KeyCode, Controller
from pynput.mouse import Button


PynputKey = Union[Key, KeyCode, None]
PynputButton = Button


class PynputKeyboardEvent(KeyboardBackend[PynputKey]):

    def __init__(self) -> None:
        self.callbacks: KeyboardCallList = KeyboardCallList()
        self.controller = Controller()

    def on_press(self, key: PynputKey) -> None:
        self.notify_callbacks(key, KeyboardTypeEvent.PRESS) 

    def on_release(self, key: PynputKey) -> None:
        self.notify_callbacks(key, KeyboardTypeEvent.RELEASE)
    
    def insert(self, key: str) -> None:
        if hasattr(Key, key):
            self.controller.press(getattr(Key, key))
        else:
            self.controller.press(key)
    
    def add_callback(
        self, 
        cb: Callable[..., None], 
        kind: KeyboardTypeEvent
    ) -> None:
        match kind:
            case KeyboardTypeEvent.PRESS:
                self.callbacks.press.append(cb)

            case KeyboardTypeEvent.RELEASE:
                self.callbacks.release.append(cb)

    def notify_callbacks(
        self, 
        key: PynputKey, 
        kind: KeyboardTypeEvent
    ) -> None:
        match kind:
            case KeyboardTypeEvent.PRESS:
                for cb in self.callbacks.press:
                    cb(key)
                    
            case KeyboardTypeEvent.RELEASE:
                for cb in self.callbacks.release:
                    cb(key)

    def listen(self) -> None:
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        listener.start()
        listener.join()


class PynputMouseEvent(MouseBackend[PynputButton]):

    def __init__(self) -> None:
        self.callbacks: MouseCallList = MouseCallList()

    def on_move(
        self,
        mouse_position_x: int, 
        mouse_position_y: int
    ) -> None:
        self.notify_callbacks(
            MouseTypeEvent.MOVE, 
            **{
                "mouse_position_x": mouse_position_x,
                "mouse_position_y": mouse_position_y
            }
        )
    
    def on_click(
        self, 
        mouse_position_x: int, 
        mouse_position_y: int, 
        button: PynputButton, 
        pressed: bool
    ) -> None:
        self.notify_callbacks(
            MouseTypeEvent.CLICK, 
            **{
                "mouse_position_x": mouse_position_x,
                "mouse_position_y": mouse_position_y,
                "button": button,
                "pressed": pressed
            }
        )
    
    def on_scroll(
        self,
        mouse_position_x: int, 
        mouse_position_y: int, 
        scroll_change_x: int, 
        scroll_change_y: int
    ) -> None:
        self.notify_callbacks(
            MouseTypeEvent.SCROLL, 
            **{
                "mouse_position_x": mouse_position_x,
                "mouse_position_y": mouse_position_y,
                "scroll_change_x": scroll_change_x,
                "scroll_change_y": scroll_change_y
            }
        )
    
    def add_callback(
        self, 
        cb: Callable[..., Any], 
        kind: MouseTypeEvent
    ) -> None:
        match kind:
            case MouseTypeEvent.CLICK:
                self.callbacks.click.append(cb)
            
            case MouseTypeEvent.MOVE:
                self.callbacks.move.append(cb)
            
            case MouseTypeEvent.SCROLL:
                self.callbacks.scroll.append(cb)
    
    def notify_callbacks(
        self, 
        kind: MouseTypeEvent, 
        **kwargs: object
    ) -> None:
            match kind:
                case MouseTypeEvent.CLICK:
                    for cb in self.callbacks.click:
                        cb(**kwargs)                
                        
                case MouseTypeEvent.MOVE:
                    for cb in self.callbacks.move:
                        cb(**kwargs)
                
                case MouseTypeEvent.SCROLL:
                    for cb in self.callbacks.scroll:
                        cb(**kwargs)                        

    def listen(self) -> None:
        listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
            on_scroll=self.on_scroll
        )
        listener.start()
        listener.join()
