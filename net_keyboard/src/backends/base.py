from typing import Generic, TypeVar, List, Callable
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field


K = TypeVar("K")
B = TypeVar("B")
CallList = List[Callable[..., None]]


class MouseTypeEvent(Enum):
    SCROLL = "scroll"
    MOVE = "move"
    CLICK = "click"


class KeyboardTypeEvent(Enum):
    PRESS = "press"
    RELEASE = "release"


@dataclass
class KeyboardCallList:
    press: CallList = field(default_factory=list)
    release: CallList = field(default_factory=list) 


@dataclass
class MouseCallList:
    move: CallList = field(default_factory=list)
    click: CallList = field(default_factory=list) 
    scroll: CallList = field(default_factory=list) 


class KeyboardBackend(Generic[K], ABC):
    
    @abstractmethod
    def on_press(self, key: K) -> None:
        pass
    
    @abstractmethod
    def on_release(self, key: K) -> None:
        pass
    
    @abstractmethod
    def insert(self, key: str) -> None:
        pass
    
    @abstractmethod
    def listen(self) -> None:
        pass


class MouseBackend(Generic[B], ABC):
    
    @abstractmethod
    def on_move(
        self,
        mouse_position_x: int, 
        mouse_position_y: int
    ) -> None:
        pass
    
    @abstractmethod
    def on_click(
        self, 
        mouse_position_x: int, 
        mouse_position_y: int, 
        button: B, 
        pressed: bool
    ) -> None:
        pass
    
    @abstractmethod
    def on_scroll(
        self,
        mouse_position_x: int, 
        mouse_position_y: int, 
        scroll_change_x: int, 
        scroll_change_y: int
    ) -> None:
        pass

    @abstractmethod
    def listen(self) -> None:
        pass
