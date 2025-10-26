"""
Symbol element parser for S-expression symbol definitions.

Handles parsing of symbol elements with properties, positions, and library references.
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from .base import BaseElementParser

logger = logging.getLogger(__name__)


class SymbolParser(BaseElementParser):
    """Parser for symbol S-expression elements."""

    def __init__(self):
        """Initialize symbol parser."""
        super().__init__("symbol")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a symbol S-expression element.

        Expected format:
        (symbol (lib_id "Device:R") (at x y angle) (property "Reference" "R1" ...)...)

        Args:
            element: Symbol S-expression element

        Returns:
            Parsed symbol data with library ID, position, and properties
        """
        symbol_data = {
            "lib_id": "",
            "position": {"x": 0, "y": 0, "angle": 0},
            "mirror": "",
            "unit": 1,
            "in_bom": True,
            "on_board": True,
            "fields_autoplaced": False,
            "uuid": None,
            "properties": [],
            "instances": [],
        }

        for elem in element[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "lib_id":
                symbol_data["lib_id"] = str(elem[1]) if len(elem) > 1 else ""
            elif elem_type == "at":
                self._parse_position(elem, symbol_data)
            elif elem_type == "mirror":
                symbol_data["mirror"] = str(elem[1]) if len(elem) > 1 else ""
            elif elem_type == "unit":
                symbol_data["unit"] = int(elem[1]) if len(elem) > 1 else 1
            elif elem_type == "in_bom":
                symbol_data["in_bom"] = self._parse_boolean(elem[1]) if len(elem) > 1 else True
            elif elem_type == "on_board":
                symbol_data["on_board"] = self._parse_boolean(elem[1]) if len(elem) > 1 else True
            elif elem_type == "fields_autoplaced":
                symbol_data["fields_autoplaced"] = True
            elif elem_type == "uuid":
                symbol_data["uuid"] = str(elem[1]) if len(elem) > 1 else None
            elif elem_type == "property":
                prop = self._parse_property(elem)
                if prop:
                    symbol_data["properties"].append(prop)
            elif elem_type == "instances":
                symbol_data["instances"] = self._parse_instances(elem)

        return symbol_data

    def _parse_position(self, at_element: List[Any], symbol_data: Dict[str, Any]) -> None:
        """
        Parse position from at element.

        Args:
            at_element: (at x y [angle])
            symbol_data: Symbol data dictionary to update
        """
        try:
            if len(at_element) >= 3:
                symbol_data["position"]["x"] = float(at_element[1])
                symbol_data["position"]["y"] = float(at_element[2])
            if len(at_element) >= 4:
                symbol_data["position"]["angle"] = float(at_element[3])
        except (ValueError, IndexError) as e:
            self._logger.warning(f"Invalid position coordinates: {at_element}, error: {e}")

    def _parse_property(self, prop_element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a property element.

        Args:
            prop_element: (property "name" "value" (at x y angle) ...)

        Returns:
            Parsed property data or None if invalid
        """
        if len(prop_element) < 3:
            return None

        prop_data = {
            "name": str(prop_element[1]),
            "value": str(prop_element[2]),
            "position": {"x": 0, "y": 0, "angle": 0},
            "effects": {},
        }

        # Parse additional property elements
        for elem in prop_element[3:]:
            if isinstance(elem, list) and len(elem) > 0:
                elem_type = str(elem[0])
                if elem_type == "at":
                    self._parse_property_position(elem, prop_data)
                elif elem_type == "effects":
                    prop_data["effects"] = self._parse_effects(elem)

        return prop_data

    def _parse_property_position(self, at_element: List[Any], prop_data: Dict[str, Any]) -> None:
        """Parse property position from at element."""
        try:
            if len(at_element) >= 3:
                prop_data["position"]["x"] = float(at_element[1])
                prop_data["position"]["y"] = float(at_element[2])
            if len(at_element) >= 4:
                prop_data["position"]["angle"] = float(at_element[3])
        except (ValueError, IndexError) as e:
            self._logger.warning(f"Invalid property position: {at_element}, error: {e}")

    def _parse_effects(self, effects_element: List[Any]) -> Dict[str, Any]:
        """Parse effects element for text formatting."""
        effects = {
            "font_size": 1.27,
            "font_thickness": 0.15,
            "bold": False,
            "italic": False,
            "hide": False,
            "justify": [],
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

    def _parse_instances(self, instances_element: List[Any]) -> List[Dict[str, Any]]:
        """Parse instances element for symbol instances."""
        instances = []
        for elem in instances_element[1:]:
            if isinstance(elem, list) and len(elem) > 0 and str(elem[0]) == "instance":
                instance = self._parse_instance(elem)
                if instance:
                    instances.append(instance)
        return instances

    def _parse_instance(self, instance_element: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a single instance element."""
        instance = {"project": "", "path": "", "reference": "", "unit": 1}

        for elem in instance_element[1:]:
            if isinstance(elem, list) and len(elem) >= 2:
                elem_type = str(elem[0])
                if elem_type == "project":
                    instance["project"] = str(elem[1])
                elif elem_type == "path":
                    instance["path"] = str(elem[1])
                elif elem_type == "reference":
                    instance["reference"] = str(elem[1])
                elif elem_type == "unit":
                    try:
                        instance["unit"] = int(elem[1])
                    except (ValueError, IndexError):
                        pass

        return instance if instance["reference"] else None

    def _parse_boolean(self, value: Any) -> bool:
        """Parse boolean value from S-expression."""
        if isinstance(value, str):
            return value.lower() in ("yes", "true", "1")
        elif isinstance(value, sexpdata.Symbol):
            return str(value).lower() in ("yes", "true", "1")
        else:
            return bool(value)
