"""Named pipe transport implementations for Windows.

Exports PipeClient and PipeServer stubs used on Windows platforms.
"""

from .client import PipeClient
from .server import PipeServer

__all__ = ["PipeClient", "PipeServer"]
