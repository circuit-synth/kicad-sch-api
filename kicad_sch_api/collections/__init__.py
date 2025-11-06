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
from .components import Component, ComponentCollection

# Other collections to be implemented
# from .junctions import JunctionCollection
# from .labels import LabelCollection
# from .wires import WireCollection

__all__ = [
    "BaseCollection",
    "IndexSpec",
    "IndexRegistry",
    "PropertyDict",
    "ValidationLevel",
    "Component",
    "ComponentCollection",
    # "WireCollection",
    # "JunctionCollection",
    # "LabelCollection",
]
