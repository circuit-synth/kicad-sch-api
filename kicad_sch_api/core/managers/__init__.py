"""
Schematic management modules for separating responsibilities.

This package contains specialized managers for different aspects of schematic
manipulation, enabling clean separation of concerns and better maintainability.
"""

from .base import BaseManager
from .file_io import FileIOManager
from .format_sync import FormatSyncManager
from .graphics import GraphicsManager
from .hierarchy import HierarchyManager
from .metadata import MetadataManager
from .sheet import SheetManager
from .text_elements import TextElementManager
from .validation import ValidationManager
from .wire import WireManager

__all__ = [
    "BaseManager",
    "FileIOManager",
    "FormatSyncManager",
    "GraphicsManager",
    "HierarchyManager",
    "MetadataManager",
    "SheetManager",
    "TextElementManager",
    "ValidationManager",
    "WireManager",
]
