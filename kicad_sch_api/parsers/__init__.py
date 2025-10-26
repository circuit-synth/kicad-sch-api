"""
Modular S-expression parsers for KiCAD elements.

This package provides specialized parsers for different types of KiCAD
S-expression elements, organized by responsibility and testable in isolation.
"""

from .registry import ElementParserRegistry
from .base import BaseElementParser

__all__ = [
    "ElementParserRegistry",
    "BaseElementParser",
]