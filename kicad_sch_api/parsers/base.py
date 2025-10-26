"""
Base parser implementation for S-expression elements.

Provides common functionality and utilities for all element parsers.
"""

import logging
from typing import Any, Dict, List, Optional

from ..interfaces.parser import IElementParser

logger = logging.getLogger(__name__)


class BaseElementParser(IElementParser):
    """Base implementation for S-expression element parsers."""

    def __init__(self, element_type: str):
        """
        Initialize base parser.

        Args:
            element_type: The S-expression element type this parser handles
        """
        self.element_type = element_type
        self._logger = logger.getChild(self.__class__.__name__)

    def can_parse(self, element: List[Any]) -> bool:
        """Check if this parser can handle the given element type."""
        if not element or not isinstance(element, list):
            return False

        element_type = element[0] if element else None
        # Convert sexpdata.Symbol to string for comparison
        element_type_str = str(element_type) if element_type else None
        return element_type_str == self.element_type

    def parse(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse an S-expression element with error handling.

        This method provides common error handling and validation,
        then delegates to the specific parse_element implementation.
        """
        if not self.can_parse(element):
            return None

        try:
            result = self.parse_element(element)
            if result is not None:
                self._logger.debug(f"Successfully parsed {self.element_type} element")
            return result
        except Exception as e:
            self._logger.error(f"Failed to parse {self.element_type} element: {e}")
            return None

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse the specific element type.

        This method should be implemented by subclasses to handle
        the specific parsing logic for their element type.

        Args:
            element: S-expression element to parse

        Returns:
            Parsed element data or None if parsing failed

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"parse_element not implemented for {self.element_type}")

    def _extract_position(self, element: List[Any]) -> Optional[Dict[str, float]]:
        """
        Extract position information from common S-expression formats.

        Many KiCAD elements have position info in formats like:
        (at x y [angle])

        Args:
            element: S-expression sub-element containing position

        Returns:
            Dictionary with x, y, and optionally angle, or None if not found
        """
        if not isinstance(element, list) or len(element) < 3:
            return None

        if element[0] != "at":
            return None

        try:
            result = {"x": float(element[1]), "y": float(element[2])}

            # Optional angle parameter
            if len(element) > 3:
                result["angle"] = float(element[3])

            return result
        except (ValueError, IndexError):
            return None

    def _extract_property_list(
        self, elements: List[Any], property_name: str
    ) -> List[Dict[str, Any]]:
        """
        Extract all instances of a property from a list of elements.

        Args:
            elements: List of S-expression elements
            property_name: Name of property to extract

        Returns:
            List of parsed property dictionaries
        """
        properties = []
        for element in elements:
            if isinstance(element, list) and len(element) > 0 and element[0] == property_name:
                prop = self._parse_property_element(element)
                if prop:
                    properties.append(prop)
        return properties

    def _parse_property_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a generic property element.

        Override this method in subclasses for property-specific parsing.

        Args:
            element: S-expression property element

        Returns:
            Parsed property data or None
        """
        if len(element) < 2:
            return None

        return {
            "type": element[0],
            "value": element[1] if len(element) > 1 else None,
            "raw": element,
        }
