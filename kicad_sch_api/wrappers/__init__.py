"""
Wrapper classes for schematic elements.

Provides enhanced element access with validation, parent tracking,
and automatic change notification.
"""

from .base import ElementWrapper
from .wire import WireWrapper

__all__ = [
    "ElementWrapper",
    "WireWrapper",
]
