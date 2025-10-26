"""
Modular S-expression parsers for KiCAD elements.

This package provides specialized parsers for different types of KiCAD
S-expression elements, organized by responsibility and testable in isolation.
"""

from .base import BaseElementParser
from .registry import ElementParserRegistry

__all__ = [
    "ElementParserRegistry",
    "BaseElementParser",
]
