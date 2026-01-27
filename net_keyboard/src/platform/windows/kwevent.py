from src.platform.base import IPCStreamReader, FormatSpec, GLOBAL_FORMAT_SPEC, safe_read, CALLBACK_READER
from struct import unpack


class WindowsKbdListener(IPCStreamReader):
    
    def __init__(self) -> None:
        self._running: bool = True
    
    def open(self, raw: CALLBACK_READER) -> None:
        spec: FormatSpec = GLOBAL_FORMAT_SPEC
        
        try:
            while self._running:
                data: bytes = safe_read(raw, spec.size)
                code, state, time = unpack(spec.fmt, data)
                print(code, state, time)

        except EOFError:
            pass
        finally:
            self.close()

    def close(self) -> None:
        pass
