"""Evdev backend module for keyboard and mouse event handling."""
from src.backends.base import (
    KeyboardBackend, KbdSubList, 
    KeyboardTypeEvent, TUPLE_CODES
    )
from src.platform.linux.klevent import LinuxKbdListener, CB_EVENT


class EvdevKeyboardEvent(KeyboardBackend):
    """
    Evdev-based keyboard event handler.
    
    This class implements keyboard event handling using the evdev library,
    providing functionality for listening to keyboard events on Linux systems.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Evdev keyboard event handler.
        """
        self.subscribers: KbdSubList = KbdSubList()

    def on_press(self, codes: TUPLE_CODES) -> None:
        """
        Handle keyboard press events.
        
        Args:
            codes (Tuple[int, int, int]): The scancode, state, and time of the key that was pressed.
        """
        self._emit_event(codes, KeyboardTypeEvent.PRESS)
        
    def on_release(self, codes: TUPLE_CODES) -> None:
        """
        Handle keyboard release events.
        
        Args:
            codes (Tuple[int, int, int]): The scancode, state, and time of the key that was released.
        """
        self._emit_event(codes, KeyboardTypeEvent.RELEASE)

    def add_subscriber(
        self, 
        sub: CB_EVENT, 
        kind: KeyboardTypeEvent
    ) -> None:
        """
        Register a callback function for keyboard events.
        
        Args:
            sub (Callable): The callback function to register.
            kind (KeyboardTypeEvent): The type of keyboard event to listen for.
        """
        match kind:
            case KeyboardTypeEvent.PRESS:
                self.subscribers.press.append(sub)

            case KeyboardTypeEvent.RELEASE:
                self.subscribers.release.append(sub)

    def _emit_event(
        self, 
        codes: TUPLE_CODES, 
        kind: KeyboardTypeEvent
    ) -> None:
        """
        Notify all registered callbacks for a keyboard event.
        
        Args:
            codes (Tuple[int, int, int]): The scancode of the key involved in the event.
            kind (KeyboardTypeEvent): The type of keyboard event.
        """
        match kind:
            case KeyboardTypeEvent.PRESS:
                for sub in self.subscribers.press:
                    sub(codes)
                    
            case KeyboardTypeEvent.RELEASE:
                for sub in self.subscribers.release:
                    sub(codes)
    
    def listen(self) -> None:
        """
        Start listening for keyboard events.
        
        Blocks until the listener thread is interrupted or terminated.
        """
        listener = LinuxKbdListener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        listener.open()
