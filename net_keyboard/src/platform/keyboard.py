from typing import Callable, Optional, Tuple
from src.platform.base import (
    IPCStreamReader, GLOBAL_FORMAT_SPEC,
    CALLBACK_READER, safe_read
    )
from struct import unpack


CB_EVENT = Callable[[Tuple[int, int, int]], None]


class Listener(IPCStreamReader):

    def __init__(
        self, 
        on_press: Optional[CB_EVENT] = None,
        on_release: Optional[CB_EVENT] = None
    ) -> None:
        self.on_press: Optional[CB_EVENT] = on_press
        self.on_release: Optional[CB_EVENT] = on_release
        self._running: bool = True
    
    def open(self, raw: CALLBACK_READER) -> None:     
        spec = GLOBAL_FORMAT_SPEC
        
        try:
            while self._running:
                data: bytes = safe_read(raw, spec.size)
                code, state, time = unpack(spec.fmt, data)
                
                if state == 1 and self.on_press:
                    self.on_press((code, state, time))
                    
                elif state == 0 and self.on_release:
                    self.on_release((code, state, time))

        except Exception as e:
            print(f"Listener error: {e}")
        finally:
            self.close()            

    def close(self) -> None:
        pass
