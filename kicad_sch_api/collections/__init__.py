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
    IndexSpec,
    IndexRegistry,
    PropertyDict,
    ValidationLevel,
)
from .junctions import JunctionCollection
from .labels import LabelCollection, LabelElement
from .wires import WireCollection

# Component collection from components worktree (when merged)
# from .components import Component, ComponentCollection

__all__ = [
    "BaseCollection",
    "IndexSpec",
    "IndexRegistry",
    "PropertyDict",
    "ValidationLevel",
    "JunctionCollection",
    "LabelCollection",
    "LabelElement",
    "WireCollection",
    # "Component",
    # "ComponentCollection",
]
