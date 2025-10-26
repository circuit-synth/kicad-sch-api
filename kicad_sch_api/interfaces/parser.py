"""
Parser interfaces for S-expression elements.

These interfaces define the contract for parsing different types of KiCAD
S-expression elements, enabling modular and testable parsing.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union


class IElementParser(Protocol):
    """Interface for parsing individual S-expression elements."""

    def can_parse(self, element: List[Any]) -> bool:
        """
        Check if this parser can handle the given S-expression element.

        Args:
            element: S-expression element (list with type as first item)

        Returns:
            True if this parser can handle the element type
        """
        ...

    def parse(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse an S-expression element into a dictionary representation.

        Args:
            element: S-expression element to parse

        Returns:
            Parsed element as dictionary, or None if parsing failed

        Raises:
            ParseError: If element is malformed or cannot be parsed
        """
        ...


class ISchematicParser(Protocol):
    """Interface for high-level schematic parsing operations."""

    def parse_file(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a complete KiCAD schematic file.

        Args:
            filepath: Path to the .kicad_sch file

        Returns:
            Complete schematic data structure

        Raises:
            FileNotFoundError: If file doesn't exist
            ParseError: If file format is invalid
        """
        ...

    def parse_string(self, content: str) -> Dict[str, Any]:
        """
        Parse schematic content from a string.

        Args:
            content: S-expression content as string

        Returns:
            Complete schematic data structure

        Raises:
            ParseError: If content format is invalid
        """
        ...
