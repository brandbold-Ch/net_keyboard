"""Pynput backend module for keyboard and mouse event handling."""
from typing import Callable
from src.backends.base import KeyboardBackend, KeyboardTypeEvent,\
    KbdSubList, TUPLE_CODES
from src.platform.keyboard import Listener
from src.platform.base import IPCProcessLauncher


class LinuxKeyboardEventListener(KeyboardBackend):
    """
    Pynput-based keyboard event handler.
    
    This class implements keyboard event handling using the pynput library,
    providing functionality to listen to keyboard events and manage callbacks.
    """

    def __init__(self, os_name: str) -> None:
        """
        Initialize the Pynput keyboard event handler.
        
        Sets up the keyboard controller and initializes the callback list.
        """
        self.os_name = os_name
        self.callbacks: KbdSubList = KbdSubList()

    def on_press(self, codes: TUPLE_CODES) -> None:
        """
        Handle keyboard press events.
        
        Args:
            code (int): The scancode of the key that was pressed.
            state (int): The state of the key.
            time (int): The time of the event.
        """
        self._emit_event(codes, KeyboardTypeEvent.PRESS) 

    def on_release(self, codes: TUPLE_CODES) -> None:
        """
        Handle keyboard release events.
        
        Args:
            code (int): The scancode of the key that was released.
            state (int): The state of the key.
            time (int): The time of the event.
        """
        self._emit_event(codes, KeyboardTypeEvent.RELEASE)
    
    def press(self, code: int) -> None:
        """
        Simulate pressing a key.
        
        Args:
            code (int): The scancode of the key to press.
        """
        pass
        
    def add_subscriber(
        self, 
        cb: Callable[[TUPLE_CODES], None], 
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
                
            case _:
                raise ValueError(f"Unsupported keyboard event type: {kind}")

    def _emit_event(
        self, 
        codes: TUPLE_CODES,
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
                    cb(codes)
                    
            case KeyboardTypeEvent.RELEASE:
                for cb in self.callbacks.release:
                    cb(codes)
            
            case _:
                raise ValueError(f"Unsupported keyboard event type: {kind}")

    def listen(self) -> None:
        """
        Start listening for keyboard events.
        
        Blocks until the listener thread is interrupted or terminated.
        """
        launcher = IPCProcessLauncher(
            client="src/platform/linux/klevent" if self.os_name == "posix" else
                "src/platform/windows/kwevent",
            server=Listener(
                on_press=self.on_press,
                on_release=self.on_release
            ),
            shared="/tmp/keyboard_ipc.sock" if self.os_name == "posix" else
                r"\\.\pipe\keyboard_ipc"
        )
        launcher.launch()
