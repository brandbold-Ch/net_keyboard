from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    
    @abstractmethod
    def init(self) -> None:
        pass
