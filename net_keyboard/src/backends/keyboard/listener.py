"""Pynput backend module for keyboard and mouse event handling."""

from typing import Callable

from src.backends.base import (
    TUPLE_CODES,
    KeyboardBackend,
    KeyboardSubscribers,
    KeyboardTypeEvent,
)
from src.transport.ipc.tools import IPCProcessLauncher


class EventListener(KeyboardBackend):
    """
    Pynput-based keyboard event handler.

    This class implements keyboard event handling using the pynput library,
    providing functionality to listen to keyboard events and manage callbacks.
    """

    def __init__(self, launcher_factory: Callable[[], IPCProcessLauncher]) -> None:
        """
        Initialize the Pynput keyboard event handler.

        Sets up the keyboard controller and initializes the callback list.
        """
        self._subscribers: KeyboardSubscribers = KeyboardSubscribers()
        self._launcher_factory = launcher_factory

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
        self, cb: Callable[[TUPLE_CODES], None], kind: KeyboardTypeEvent
    ) -> None:
        """
        Register a callback function for keyboard events.

        Args:
            cb (Callable): The callback function to register.
            kind (KeyboardTypeEvent): The type of keyboard event to listen for.
        """
        match kind:
            case KeyboardTypeEvent.PRESS:
                self._subscribers.press.append(cb)

            case KeyboardTypeEvent.RELEASE:
                self._subscribers.release.append(cb)

            case _:
                raise ValueError(f"Unsupported keyboard event type: {kind}")

    def _emit_event(self, codes: TUPLE_CODES, kind: KeyboardTypeEvent) -> None:
        """
        Notify all registered callbacks for a keyboard event.

        Args:
            key (PynputKey): The key involved in the event.
            kind (KeyboardTypeEvent): The type of keyboard event.
        """
        match kind:
            case KeyboardTypeEvent.PRESS:
                for cb in self._subscribers.press:
                    cb(codes)

            case KeyboardTypeEvent.RELEASE:
                for cb in self._subscribers.release:
                    cb(codes)

            case _:
                raise ValueError(f"Unsupported keyboard event type: {kind}")

    def listen(self) -> None:
        """
        Start listening for keyboard events.

        Blocks until the listener thread is interrupted or terminated.
        """
        launcher = self._launcher_factory()
        launcher.launch()
