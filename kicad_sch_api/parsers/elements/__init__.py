"""
Element-specific parsers for KiCAD schematic elements.

This module contains specialized parsers for different schematic element types,
extracted from the monolithic parser.py for better maintainability.
"""

from .graphics_parser import GraphicsParser

# Additional element parsers will be imported here as they are created
# from .wire_parser import WireParser
# from .label_parser import LabelParser
# from .text_parser import TextParser
# from .sheet_parser import SheetParser
# from .library_parser import LibraryParser
# from .symbol_parser import SymbolParser
# from .metadata_parser import MetadataParser

__all__ = [
    "GraphicsParser",
    # Will be populated as parsers are added
]
