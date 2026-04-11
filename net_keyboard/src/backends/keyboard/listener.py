"""Keyboard backend that receives input events via an IPC launcher.

This module provides an EventListener implementation of the
``KeyboardBackend`` interface that integrates with the project's IPC
launcher. Instead of using pynput directly, this listener launches a
helper process (via ``IPCProcessLauncher``) which reads device events and
forwards them to the EventListener through the IPC channel.
"""

from typing import Callable

from src.backends.base import (
    TUPLE_CODES,
    KeyboardBackend,
    KeyboardSubscribers,
    KeyboardTypeEvent,
)
from src.transport.ipc.tools import IPCProcessLauncher


class EventListener(KeyboardBackend):
    """IPC-backed keyboard event handler.

    The EventListener implements the project-wide ``KeyboardBackend``
    interface. It stores subscribers for press/release events and uses an
    ``IPCProcessLauncher`` factory to start a helper process that reads
    low-level device events and dispatches them through the IPC channel.

    The helper process is expected to send tuples of integers matching the
    project's GLOBAL_FORMAT (code, state, time). EventListener decodes
    those tuples and forwards them to registered callbacks.
    """

    def __init__(self, launcher_factory: Callable[[], IPCProcessLauncher]) -> None:
        """
        Initialize the keyboard listener with an IPC launcher factory.

        The ``launcher_factory`` callable should return an instance of
        ``IPCProcessLauncher`` configured to launch the helper process that
        reads device events and exposes them through the IPC channel.
        The returned launcher will be used by ``listen`` to start the
        event source.
        """
        self._subscribers: KeyboardSubscribers = KeyboardSubscribers()
        self._launcher_factory = launcher_factory

    def on_press(self, event: TUPLE_CODES) -> None:
        """
        Handle keyboard press events and dispatch to subscribers.

        Args:
            codes: A tuple of three integers (code, state, time) representing
                the low-level event received from the IPC helper.
        """
        self._emit_event(event, KeyboardTypeEvent.PRESS)

    def on_release(self, event: TUPLE_CODES) -> None:
        """
        Handle keyboard release events and dispatch to subscribers.

        Args:
            codes: A tuple of three integers (code, state, time) representing
                the low-level event received from the IPC helper.
        """
        self._emit_event(event, KeyboardTypeEvent.RELEASE)

    def press(self, event: TUPLE_CODES) -> None:
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

    def _emit_event(self, event: TUPLE_CODES, kind: KeyboardTypeEvent) -> None:
        """
        Notify all registered callbacks for a keyboard event.

        Args:
            codes: A tuple (code, state, time) describing the event.
            kind: The type of keyboard event (PRESS or RELEASE).
        """
        match kind:
            case KeyboardTypeEvent.PRESS:
                for cb in self._subscribers.press:
                    cb(event)

            case KeyboardTypeEvent.RELEASE:
                for cb in self._subscribers.release:
                    cb(event)

    def listen(self) -> None:
        """
        Start listening for keyboard events.

        Blocks until the listener thread is interrupted or terminated.
        """
        launcher = self._launcher_factory()
        launcher.launch()
