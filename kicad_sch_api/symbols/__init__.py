"""
Symbol resolution and caching architecture for KiCAD schematic API.

This module provides a unified symbol resolution system that separates concerns
between caching, inheritance resolution, and validation while maintaining
high performance and exact format preservation.
"""

from .cache import ISymbolCache, SymbolCache
from .resolver import SymbolResolver
from .validators import SymbolValidator

__all__ = [
    "ISymbolCache",
    "SymbolCache",
    "SymbolResolver",
    "SymbolValidator",
]
