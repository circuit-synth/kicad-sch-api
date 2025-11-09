"""
Wire and connection element parsers for KiCAD schematics.

Handles parsing and serialization of connection elements:
- Wire
- Junction
- No-connect
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from ...core.config import config
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class WireParser(BaseElementParser):
    """Parser for wire and connection elements."""

    def __init__(self):
        """Initialize wire parser."""
        super().__init__("wire")

    def _parse_wire(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a wire definition."""
        wire_data = {
            "points": [],
            "stroke_width": 0.0,
            "stroke_type": config.defaults.stroke_type,
            "uuid": None,
            "wire_type": "wire",  # Default to wire (vs bus)
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "pts":
                # Parse points: (pts (xy x1 y1) (xy x2 y2) ...)
                for pt in elem[1:]:
                    if isinstance(pt, list) and len(pt) >= 3:
                        if str(pt[0]) == "xy":
                            x, y = float(pt[1]), float(pt[2])
                            wire_data["points"].append({"x": x, "y": y})

            elif elem_type == "stroke":
                # Parse stroke: (stroke (width 0) (type default))
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list) and len(stroke_elem) >= 2:
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width":
                            wire_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type":
                            wire_data["stroke_type"] = str(stroke_elem[1])

            elif elem_type == "uuid":
                wire_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        # Only return wire if it has at least 2 points
        if len(wire_data["points"]) >= 2:
            return wire_data
        else:
            logger.warning(f"Wire has insufficient points: {len(wire_data['points'])}")
            return None

    def _parse_junction(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a junction definition."""
        junction_data = {
            "position": {"x": 0, "y": 0},
            "diameter": 0,
            "color": (0, 0, 0, 0),
            "uuid": None,
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                # Parse position: (at x y)
                if len(elem) >= 3:
                    junction_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}

            elif elem_type == "diameter":
                # Parse diameter: (diameter value)
                if len(elem) >= 2:
                    junction_data["diameter"] = float(elem[1])

            elif elem_type == "color":
                # Parse color: (color r g b a)
                if len(elem) >= 5:
                    junction_data["color"] = (
                        int(elem[1]),
                        int(elem[2]),
                        int(elem[3]),
                        int(elem[4]),
                    )

            elif elem_type == "uuid":
                junction_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return junction_data

    def _parse_no_connect(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a no_connect symbol."""
        # Format: (no_connect (at x y) (uuid ...))
        no_connect_data = {"position": {"x": 0, "y": 0}, "uuid": None}

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                if len(elem) >= 3:
                    no_connect_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "uuid":
                no_connect_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return no_connect_data

    def _wire_to_sexp(self, wire_data: Dict[str, Any]) -> List[Any]:
        """Convert wire to S-expression."""
        sexp = [sexpdata.Symbol("wire")]

        # Add points (pts section)
        points = wire_data.get("points", [])
        if len(points) >= 2:
            pts_sexp = [sexpdata.Symbol("pts")]
            for point in points:
                if isinstance(point, dict):
                    x, y = point["x"], point["y"]
                elif isinstance(point, (list, tuple)) and len(point) >= 2:
                    x, y = point[0], point[1]
                else:
                    # Assume it's a Point object
                    x, y = point.x, point.y

                # Format coordinates properly (avoid unnecessary .0 for integers)
                if isinstance(x, float) and x.is_integer():
                    x = int(x)
                if isinstance(y, float) and y.is_integer():
                    y = int(y)

                pts_sexp.append([sexpdata.Symbol("xy"), x, y])
            sexp.append(pts_sexp)

        # Add stroke information
        stroke_width = wire_data.get("stroke_width", config.defaults.stroke_width)
        stroke_type = wire_data.get("stroke_type", config.defaults.stroke_type)
        stroke_sexp = [sexpdata.Symbol("stroke")]

        # Format stroke width (use int for 0, preserve float for others)
        if isinstance(stroke_width, float) and stroke_width == 0.0:
            stroke_width = 0

        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add UUID
        if "uuid" in wire_data:
            sexp.append([sexpdata.Symbol("uuid"), wire_data["uuid"]])

        return sexp

    def _junction_to_sexp(self, junction_data: Dict[str, Any]) -> List[Any]:
        """Convert junction to S-expression."""
        sexp = [sexpdata.Symbol("junction")]

        # Add position
        pos = junction_data["position"]
        if isinstance(pos, dict):
            x, y = pos["x"], pos["y"]
        elif isinstance(pos, (list, tuple)) and len(pos) >= 2:
            x, y = pos[0], pos[1]
        else:
            # Assume it's a Point object
            x, y = pos.x, pos.y

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y])

        # Add diameter
        diameter = junction_data.get("diameter", 0)
        sexp.append([sexpdata.Symbol("diameter"), diameter])

        # Add color (RGBA)
        color = junction_data.get("color", (0, 0, 0, 0))
        if isinstance(color, (list, tuple)) and len(color) >= 4:
            sexp.append([sexpdata.Symbol("color"), color[0], color[1], color[2], color[3]])
        else:
            sexp.append([sexpdata.Symbol("color"), 0, 0, 0, 0])

        # Add UUID
        if "uuid" in junction_data:
            sexp.append([sexpdata.Symbol("uuid"), junction_data["uuid"]])

        return sexp

    def _no_connect_to_sexp(self, no_connect_data: Dict[str, Any]) -> List[Any]:
        """Convert no_connect to S-expression."""
        sexp = [sexpdata.Symbol("no_connect")]

        # Add position
        pos = no_connect_data["position"]
        x, y = pos["x"], pos["y"]

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y])

        # Add UUID
        if "uuid" in no_connect_data:
            sexp.append([sexpdata.Symbol("uuid"), no_connect_data["uuid"]])

        return sexp
