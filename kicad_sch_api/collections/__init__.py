"""
Modern collection architecture for KiCAD schematic elements.

This module provides a unified collection framework with:
- Centralized index management via IndexRegistry
- Lazy index rebuilding for performance
- Configurable validation levels
- Auto-tracking property dictionaries
- Batch mode for bulk operations
"""

from .base import (
    BaseCollection,
    IndexRegistry,
    IndexSpec,
    PropertyDict,
    ValidationLevel,
)
from .bus_entries import BusEntryCollection
from .components import Component, ComponentCollection
from .junctions import JunctionCollection
from .labels import LabelCollection, LabelElement
from .wires import WireCollection

__all__ = [
    "BaseCollection",
    "IndexSpec",
    "IndexRegistry",
    "PropertyDict",
    "ValidationLevel",
    "BusEntryCollection",
    "Component",
    "ComponentCollection",
    "JunctionCollection",
    "LabelCollection",
    "LabelElement",
    "WireCollection",
]
