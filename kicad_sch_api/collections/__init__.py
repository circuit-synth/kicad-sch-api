"""
Modern collection architecture for KiCAD schematic elements.

This module provides a unified collection framework that eliminates code duplication
across component, wire, and junction collections while providing consistent
indexing, performance optimization, and management capabilities.
"""

from .base import IndexedCollection
from .components import ComponentCollection
from .wires import WireCollection
from .junctions import JunctionCollection
from .labels import LabelCollection

__all__ = [
    "IndexedCollection",
    "ComponentCollection",
    "WireCollection",
    "JunctionCollection",
    "LabelCollection",
]