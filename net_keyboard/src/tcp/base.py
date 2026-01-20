from typing import Any
from abc import ABC, abstractmethod


class TCP(ABC):
    
    @abstractmethod
    def send(self, packet: str) -> None:
        pass
    
    @abstractmethod
    def receive(self) -> Any:
        pass
    
    @abstractmethod
    def connect(self) -> None:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def run(self) -> None:
        pass
