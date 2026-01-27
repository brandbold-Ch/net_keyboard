"""Base module for keyboard and mouse backend abstraction."""
from typing import Generic, TypeVar, List, Callable, Tuple
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field


B = TypeVar("B")
Subscribers = List[Callable[..., None]]
TUPLE_CODES = Tuple[int, int, int]


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
class KbdSubList:
    """
    Container for keyboard event callbacks.
    
    Attributes:
        press (Subscribers): List of callbacks for key press events.
        release (Subscribers): List of callbacks for key release events.
    """
    press: Subscribers = field(default_factory=list)
    release: Subscribers = field(default_factory=list) 


@dataclass
class MouseCallList:
    """
    Container for mouse event callbacks.
    
    Attributes:
        move (CallList): List of callbacks for mouse movement events.
        click (CallList): List of callbacks for mouse click events.
        scroll (CallList): List of callbacks for mouse scroll events.
    """
    move: Subscribers = field(default_factory=list)
    click: Subscribers = field(default_factory=list) 
    scroll: Subscribers = field(default_factory=list) 


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
    
    @abstractmethod
    def listen(self) -> None:
        """
        Start listening for keyboard events.
        """
        pass


class MouseBackend(Generic[B], ABC):
    """
    Abstract base class for mouse backend implementations.
    
    This class defines the interface that all mouse backend implementations
    must follow for handling mouse events.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def on_click(
        self, 
        mouse_position_x: int, 
        mouse_position_y: int, 
        button: B, 
        pressed: bool
    ) -> None:
        """
        Handle mouse click events.
        
        Args:
            mouse_position_x (int): The X coordinate of the click position.
            mouse_position_y (int): The Y coordinate of the click position.
            button (B): The mouse button that was clicked.
            pressed (bool): True if button was pressed, False if released.
        """
        pass
    
    @abstractmethod
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
        pass

    @abstractmethod
    def listen(self) -> None:
        """
        Start listening for mouse events.
        """
        pass
