"""
Core interfaces for KiCAD schematic API.

This module provides abstract interfaces for the main components of the system,
enabling better separation of concerns and testability.
"""

from .parser import IElementParser, ISchematicParser
from .repository import ISchematicRepository
from .resolver import ISymbolResolver

__all__ = [
    "IElementParser",
    "ISchematicParser",
    "ISchematicRepository",
    "ISymbolResolver",
]
