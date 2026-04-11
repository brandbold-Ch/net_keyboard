"""Base module for keyboard and mouse backend abstraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, List, Tuple, TypeAlias

EventList: TypeAlias = List[Callable[..., None]]
TUPLE_CODES: TypeAlias = Tuple[int, int, int]


class MouseTypeEvent(Enum):
    """
    Enumeration of mouse event types.

    This class defines the types of events that can be triggered by a mouse,
    such as scrolling, moving, or clicking.
    """

    SCROLL = auto()
    MOVE = auto()
    CLICK = auto()


class KeyboardTypeEvent(Enum):
    """
    Enumeration of keyboard event types.

    This class defines the types of events that can be triggered by a keyboard,
    such as pressing or releasing a key.
    """

    PRESS = auto()
    RELEASE = auto()


@dataclass
class KeyboardSubscribers:
    """
    Container for keyboard event callbacks.

    This class holds lists of callback functions that are triggered
    when specific keyboard events occur, such as key presses or releases.

    Attributes:
        press (EventList): List of callbacks for key press events.
        release (EventList): List of callbacks for key release events.
    """

    press: EventList = field(default_factory=list)
    release: EventList = field(default_factory=list)


class KeyboardBackend(ABC):
    """
    Abstract base class for keyboard backend implementations.

    This class serves as a blueprint for all keyboard backend implementations,
    ensuring they provide methods to handle keyboard events such as key presses
    and releases.
    """

    @abstractmethod
    def on_press(self, event: TUPLE_CODES) -> None:
        """
        Handle keyboard press events.

        Args:
            codes (Tuple[int, int, int]): The scancode, state, and time of the key that was pressed.
        """
        pass

    @abstractmethod
    def on_release(self, event: TUPLE_CODES) -> None:
        """
        Handle keyboard release events.

        Args:
            codes (Tuple[int, int, int]): The scancode, state, and time of the key that was released.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def listen(self) -> None:
        """
        Start listening for keyboard events.
        """
        pass
