"""
Wire element parser for S-expression wire definitions.

Handles parsing of wire elements with points, stroke properties, and UUIDs.
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from .base import BaseElementParser

logger = logging.getLogger(__name__)


class WireParser(BaseElementParser):
    """Parser for wire S-expression elements."""

    def __init__(self):
        """Initialize wire parser."""
        super().__init__("wire")

    def parse_element(self, element: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a wire S-expression element.

        Expected format:
        (wire (pts (xy x1 y1) (xy x2 y2) ...) (stroke (width w) (type t)) (uuid "..."))

        Args:
            element: Wire S-expression element

        Returns:
            Parsed wire data with points, stroke, and UUID information
        """
        wire_data = {
            "points": [],
            "stroke_width": 0.0,
            "stroke_type": "default",
            "uuid": None,
            "wire_type": "wire",  # Default to wire (vs bus)
        }

        for elem in element[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "pts":
                self._parse_points(elem, wire_data)
            elif elem_type == "stroke":
                self._parse_stroke(elem, wire_data)
            elif elem_type == "uuid":
                wire_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        # Validate wire has sufficient points
        if len(wire_data["points"]) >= 2:
            return wire_data
        else:
            self._logger.warning(f"Wire has insufficient points: {len(wire_data['points'])}")
            return None

    def _parse_points(self, pts_element: List[Any], wire_data: Dict[str, Any]) -> None:
        """
        Parse points from pts element.

        Args:
            pts_element: (pts (xy x1 y1) (xy x2 y2) ...)
            wire_data: Wire data dictionary to update
        """
        for pt in pts_element[1:]:
            if isinstance(pt, list) and len(pt) >= 3:
                if str(pt[0]) == "xy":
                    try:
                        x, y = float(pt[1]), float(pt[2])
                        wire_data["points"].append({"x": x, "y": y})
                    except (ValueError, IndexError) as e:
                        self._logger.warning(f"Invalid point coordinates: {pt}, error: {e}")

    def _parse_stroke(self, stroke_element: List[Any], wire_data: Dict[str, Any]) -> None:
        """
        Parse stroke properties from stroke element.

        Args:
            stroke_element: (stroke (width w) (type t))
            wire_data: Wire data dictionary to update
        """
        for stroke_elem in stroke_element[1:]:
            if isinstance(stroke_elem, list) and len(stroke_elem) >= 2:
                stroke_type = str(stroke_elem[0])
                try:
                    if stroke_type == "width":
                        wire_data["stroke_width"] = float(stroke_elem[1])
                    elif stroke_type == "type":
                        wire_data["stroke_type"] = str(stroke_elem[1])
                except (ValueError, IndexError) as e:
                    self._logger.warning(f"Invalid stroke property: {stroke_elem}, error: {e}")
