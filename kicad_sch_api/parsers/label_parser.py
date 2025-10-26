"""
Label element parser for S-expression label definitions.

Handles parsing of text labels, hierarchical labels, and other text elements.
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from .base import BaseElementParser

logger = logging.getLogger(__name__)


class LabelParser(BaseElementParser):
    """Parser for label S-expression elements."""

    def __init__(self):
        """Initialize label parser."""
        super().__init__("label")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a label S-expression element.

        Expected format:
        (label "text" (at x y angle) (effects (font (size s s))))

        Args:
            element: Label S-expression element

        Returns:
            Parsed label data with text, position, and formatting
        """
        if len(element) < 2:
            return None

        label_data = {
            "text": str(element[1]),
            "position": {"x": 0, "y": 0, "angle": 0},
            "effects": {
                "font_size": 1.27,
                "font_thickness": 0.15,
                "bold": False,
                "italic": False,
                "hide": False,
                "justify": []
            },
            "uuid": None
        }

        for elem in element[2:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                self._parse_position(elem, label_data)
            elif elem_type == "effects":
                label_data["effects"] = self._parse_effects(elem)
            elif elem_type == "uuid":
                label_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return label_data

    def _parse_position(self, at_element: List[Any], label_data: Dict[str, Any]) -> None:
        """
        Parse position from at element.

        Args:
            at_element: (at x y [angle])
            label_data: Label data dictionary to update
        """
        try:
            if len(at_element) >= 3:
                label_data["position"]["x"] = float(at_element[1])
                label_data["position"]["y"] = float(at_element[2])
            if len(at_element) >= 4:
                label_data["position"]["angle"] = float(at_element[3])
        except (ValueError, IndexError) as e:
            self._logger.warning(f"Invalid position coordinates: {at_element}, error: {e}")

    def _parse_effects(self, effects_element: List[Any]) -> Dict[str, Any]:
        """
        Parse effects element for text formatting.

        Args:
            effects_element: (effects (font ...) (justify ...) ...)

        Returns:
            Parsed effects data
        """
        effects = {
            "font_size": 1.27,
            "font_thickness": 0.15,
            "bold": False,
            "italic": False,
            "hide": False,
            "justify": []
        }

        for elem in effects_element[1:]:
            if isinstance(elem, list) and len(elem) > 0:
                elem_type = str(elem[0])
                if elem_type == "font":
                    self._parse_font(elem, effects)
                elif elem_type == "justify":
                    effects["justify"] = [str(j) for j in elem[1:]]
                elif elem_type == "hide":
                    effects["hide"] = True

        return effects

    def _parse_font(self, font_element: List[Any], effects: Dict[str, Any]) -> None:
        """
        Parse font element within effects.

        Args:
            font_element: (font (size w h) (thickness t) ...)
            effects: Effects dictionary to update
        """
        for elem in font_element[1:]:
            if isinstance(elem, list) and len(elem) > 0:
                elem_type = str(elem[0])
                if elem_type == "size":
                    try:
                        if len(elem) >= 3:
                            # Usually (size width height), use width for font_size
                            effects["font_size"] = float(elem[1])
                    except (ValueError, IndexError):
                        pass
                elif elem_type == "thickness":
                    try:
                        effects["font_thickness"] = float(elem[1])
                    except (ValueError, IndexError):
                        pass
                elif elem_type == "bold":
                    effects["bold"] = True
                elif elem_type == "italic":
                    effects["italic"] = True


class HierarchicalLabelParser(BaseElementParser):
    """Parser for hierarchical label S-expression elements."""

    def __init__(self):
        """Initialize hierarchical label parser."""
        super().__init__("hierarchical_label")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a hierarchical label S-expression element.

        Expected format:
        (hierarchical_label "text" (shape input) (at x y angle) ...)

        Args:
            element: Hierarchical label S-expression element

        Returns:
            Parsed hierarchical label data
        """
        if len(element) < 2:
            return None

        label_data = {
            "text": str(element[1]),
            "shape": "input",  # Default shape
            "position": {"x": 0, "y": 0, "angle": 0},
            "effects": {
                "font_size": 1.27,
                "font_thickness": 0.15,
                "bold": False,
                "italic": False,
                "hide": False,
                "justify": []
            },
            "uuid": None
        }

        for elem in element[2:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "shape":
                label_data["shape"] = str(elem[1]) if len(elem) > 1 else "input"
            elif elem_type == "at":
                self._parse_position(elem, label_data)
            elif elem_type == "effects":
                label_data["effects"] = self._parse_effects(elem)
            elif elem_type == "uuid":
                label_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return label_data

    def _parse_position(self, at_element: List[Any], label_data: Dict[str, Any]) -> None:
        """Parse position from at element."""
        try:
            if len(at_element) >= 3:
                label_data["position"]["x"] = float(at_element[1])
                label_data["position"]["y"] = float(at_element[2])
            if len(at_element) >= 4:
                label_data["position"]["angle"] = float(at_element[3])
        except (ValueError, IndexError) as e:
            self._logger.warning(f"Invalid position coordinates: {at_element}, error: {e}")

    def _parse_effects(self, effects_element: List[Any]) -> Dict[str, Any]:
        """Parse effects element for text formatting."""
        effects = {
            "font_size": 1.27,
            "font_thickness": 0.15,
            "bold": False,
            "italic": False,
            "hide": False,
            "justify": []
        }

        for elem in effects_element[1:]:
            if isinstance(elem, list) and len(elem) > 0:
                elem_type = str(elem[0])
                if elem_type == "font":
                    self._parse_font(elem, effects)
                elif elem_type == "justify":
                    effects["justify"] = [str(j) for j in elem[1:]]
                elif elem_type == "hide":
                    effects["hide"] = True

        return effects

    def _parse_font(self, font_element: List[Any], effects: Dict[str, Any]) -> None:
        """Parse font element within effects."""
        for elem in font_element[1:]:
            if isinstance(elem, list) and len(elem) > 0:
                elem_type = str(elem[0])
                if elem_type == "size":
                    try:
                        if len(elem) >= 3:
                            effects["font_size"] = float(elem[1])
                    except (ValueError, IndexError):
                        pass
                elif elem_type == "thickness":
                    try:
                        effects["font_thickness"] = float(elem[1])
                    except (ValueError, IndexError):
                        pass
                elif elem_type == "bold":
                    effects["bold"] = True
                elif elem_type == "italic":
                    effects["italic"] = True