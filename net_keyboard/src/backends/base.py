"""Base module for keyboard and mouse backend abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Tuple, TypeAlias

EventList: TypeAlias = List[Callable[..., None]]
TUPLE_CODES: TypeAlias = Tuple[int, int, int]


class MouseTypeEvent(Enum):
    """Enumeration of mouse event types."""

    SCROLL = "scroll"
    MOVE = "move"
    CLICK = "click"


class KeyboardTypeEvent(Enum):
    """Enumeration of keyboard event types."""

    PRESS = "press"
    RELEASE = "release"


@dataclass
class KeyboardSubscribers:
    """
    Container for keyboard event callbacks.

    Attributes:
        press (Subscribers): List of callbacks for key press events.
        release (Subscribers): List of callbacks for key release events.
    """

    press: EventList = field(default_factory=list)
    release: EventList = field(default_factory=list)


class KeyboardBackend(ABC):
    """
    Abstract base class for keyboard backend implementations.

    This class defines the interface that all keyboard backend implementations
    must follow for handling keyboard events.
    """

    @abstractmethod
    def on_press(self, codes: TUPLE_CODES) -> None:
        """
        Handle keyboard press events.

        Args:
            codes (Tuple[int, int, int]): The scancode, state, and time of the key that was pressed.
        """
        pass

    @abstractmethod
    def on_release(self, codes: TUPLE_CODES) -> None:
        """
        Handle keyboard release events.

        Args:
            codes (Tuple[int, int, int]): The scancode, state, and time of the key that was released.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def listen(self) -> None:
        """
        Start listening for keyboard events.
        """
        pass
