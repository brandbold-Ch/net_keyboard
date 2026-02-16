"""Keyboard backend implementations.

Provides concrete keyboard backend classes that integrate with platform
specific input readers and the IPC launcher.
"""

from .listener import EventListener

__all__ = ["EventListener"]
