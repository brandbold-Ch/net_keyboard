"""Pynput backend module for keyboard and mouse event handling."""
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
    """
    Pynput-based keyboard event handler.
    
    This class implements keyboard event handling using the pynput library,
    providing functionality to listen to keyboard events and manage callbacks.
    """

    def __init__(self) -> None:
        """
        Initialize the Pynput keyboard event handler.
        
        Sets up the keyboard controller and initializes the callback list.
        """
        self.callbacks: KeyboardCallList = KeyboardCallList()
        self.controller = Controller()

    def on_press(self, key: PynputKey) -> None:
        """
        Handle keyboard press events.
        
        Args:
            key (PynputKey): The key that was pressed.
        """
        self.notify_callbacks(key, KeyboardTypeEvent.PRESS) 

    def on_release(self, key: PynputKey) -> None:
        """
        Handle keyboard release events.
        
        Args:
            key (PynputKey): The key that was released.
        """
        self.notify_callbacks(key, KeyboardTypeEvent.RELEASE)
    
    def insert(self, key: str) -> None:
        """
        Simulate pressing a key.
        
        Args:
            key (str): The key to press. Can be a special key name or character.
        """
        if hasattr(Key, key):
            self.controller.press(getattr(Key, key))
        else:
            self.controller.press(key)
    
    def add_callback(
        self, 
        cb: Callable[..., None], 
        kind: KeyboardTypeEvent
    ) -> None:
        """
        Register a callback function for keyboard events.
        
        Args:
            cb (Callable): The callback function to register.
            kind (KeyboardTypeEvent): The type of keyboard event to listen for.
        """
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
        """
        Notify all registered callbacks for a keyboard event.
        
        Args:
            key (PynputKey): The key involved in the event.
            kind (KeyboardTypeEvent): The type of keyboard event.
        """
        match kind:
            case KeyboardTypeEvent.PRESS:
                for cb in self.callbacks.press:
                    cb(key)
                    
            case KeyboardTypeEvent.RELEASE:
                for cb in self.callbacks.release:
                    cb(key)

    def listen(self) -> None:
        """
        Start listening for keyboard events.
        
        Blocks until the listener thread is interrupted or terminated.
        """
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        listener.start()
        listener.join()


class PynputMouseEvent(MouseBackend[PynputButton]):
    """
    Pynput-based mouse event handler.
    
    This class implements mouse event handling using the pynput library,
    providing functionality to listen to mouse events and manage callbacks.
    """

    def __init__(self) -> None:
        """
        Initialize the Pynput mouse event handler.
        
        Sets up the callback list for mouse events.
        """
        self.callbacks: MouseCallList = MouseCallList()

    def on_move(
        self,
        mouse_position_x: int, 
        mouse_position_y: int
    ) -> None:
        """
        Handle mouse movement events.
        
        Args:
            mouse_position_x (int): The X coordinate of the mouse position.
            mouse_position_y (int): The Y coordinate of the mouse position.
        """
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
        """
        Handle mouse click events.
        
        Args:
            mouse_position_x (int): The X coordinate of the click position.
            mouse_position_y (int): The Y coordinate of the click position.
            button (PynputButton): The mouse button that was clicked.
            pressed (bool): True if button was pressed, False if released.
        """
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
        """
        Handle mouse scroll events.
        
        Args:
            mouse_position_x (int): The X coordinate of the scroll position.
            mouse_position_y (int): The Y coordinate of the scroll position.
            scroll_change_x (int): The horizontal scroll change amount.
            scroll_change_y (int): The vertical scroll change amount.
        """
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
        """
        Register a callback function for mouse events.
        
        Args:
            cb (Callable): The callback function to register.
            kind (MouseTypeEvent): The type of mouse event to listen for.
        """
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
        """
        Notify all registered callbacks for a mouse event.
        
        Args:
            kind (MouseTypeEvent): The type of mouse event.
            **kwargs: Additional event-specific arguments to pass to callbacks.
        """
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
        """
        Start listening for mouse events.
        
        Blocks until the listener thread is interrupted or terminated.
        """
        listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
            on_scroll=self.on_scroll
        )
        listener.start()
        listener.join()
