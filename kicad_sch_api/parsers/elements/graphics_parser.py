"""
Graphics element parsers for KiCAD schematics.

Handles parsing and serialization of graphical elements:
- Polyline
- Arc
- Circle
- Bezier curves
- Rectangle
- Image
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from ...core.config import config
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class GraphicsParser(BaseElementParser):
    """Parser for graphical schematic elements."""

    def __init__(self):
        """Initialize graphics parser."""
        super().__init__("graphics")

    def _parse_polyline(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a polyline graphical element."""
        # Format: (polyline (pts (xy x1 y1) (xy x2 y2) ...) (stroke ...) (uuid ...))
        polyline_data = {
            "points": [],
            "stroke_width": config.defaults.stroke_width,
            "stroke_type": config.defaults.stroke_type,
            "uuid": None,
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "pts":
                for pt in elem[1:]:
                    if isinstance(pt, list) and len(pt) >= 3 and str(pt[0]) == "xy":
                        polyline_data["points"].append({"x": float(pt[1]), "y": float(pt[2])})
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            polyline_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            polyline_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "uuid":
                polyline_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return polyline_data if polyline_data["points"] else None

    def _parse_arc(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse an arc graphical element."""
        # Format: (arc (start x y) (mid x y) (end x y) (stroke ...) (fill ...) (uuid ...))
        arc_data = {
            "start": {"x": 0, "y": 0},
            "mid": {"x": 0, "y": 0},
            "end": {"x": 0, "y": 0},
            "stroke_width": config.defaults.stroke_width,
            "stroke_type": config.defaults.stroke_type,
            "fill_type": config.defaults.fill_type,
            "uuid": None,
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "start" and len(elem) >= 3:
                arc_data["start"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "mid" and len(elem) >= 3:
                arc_data["mid"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "end" and len(elem) >= 3:
                arc_data["end"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            arc_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            arc_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        arc_data["fill_type"] = str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
            elif elem_type == "uuid":
                arc_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return arc_data

    def _parse_circle(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a circle graphical element."""
        # Format: (circle (center x y) (radius r) (stroke ...) (fill ...) (uuid ...))
        circle_data = {
            "center": {"x": 0, "y": 0},
            "radius": 0,
            "stroke_width": config.defaults.stroke_width,
            "stroke_type": config.defaults.stroke_type,
            "fill_type": config.defaults.fill_type,
            "uuid": None,
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "center" and len(elem) >= 3:
                circle_data["center"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "radius" and len(elem) >= 2:
                circle_data["radius"] = float(elem[1])
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            circle_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            circle_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        circle_data["fill_type"] = (
                            str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
                        )
            elif elem_type == "uuid":
                circle_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return circle_data

    def _parse_bezier(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a bezier curve graphical element."""
        # Format: (bezier (pts (xy x1 y1) (xy x2 y2) ...) (stroke ...) (fill ...) (uuid ...))
        bezier_data = {
            "points": [],
            "stroke_width": config.defaults.stroke_width,
            "stroke_type": config.defaults.stroke_type,
            "fill_type": config.defaults.fill_type,
            "uuid": None,
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "pts":
                for pt in elem[1:]:
                    if isinstance(pt, list) and len(pt) >= 3 and str(pt[0]) == "xy":
                        bezier_data["points"].append({"x": float(pt[1]), "y": float(pt[2])})
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            bezier_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            bezier_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        bezier_data["fill_type"] = (
                            str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
                        )
            elif elem_type == "uuid":
                bezier_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return bezier_data if bezier_data["points"] else None

    def _parse_rectangle(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a rectangle graphical element."""
        rectangle = {}

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0])

            if elem_type == "start" and len(elem) >= 3:
                rectangle["start"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "end" and len(elem) >= 3:
                rectangle["end"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            rectangle["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            rectangle["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        rectangle["fill_type"] = (
                            str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
                        )
            elif elem_type == "uuid" and len(elem) >= 2:
                rectangle["uuid"] = str(elem[1])

        return rectangle if rectangle else None

    def _parse_image(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse an image element."""
        # Format: (image (at x y) (uuid "...") (data "base64..."))
        image = {"position": {"x": 0, "y": 0}, "data": "", "scale": 1.0, "uuid": None}

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at" and len(elem) >= 3:
                image["position"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "scale" and len(elem) >= 2:
                image["scale"] = float(elem[1])
            elif elem_type == "data" and len(elem) >= 2:
                # The data can be spread across multiple string elements
                data_parts = []
                for data_elem in elem[1:]:
                    data_parts.append(str(data_elem).strip('"'))
                image["data"] = "".join(data_parts)
            elif elem_type == "uuid" and len(elem) >= 2:
                image["uuid"] = str(elem[1]).strip('"')

        return image if image.get("uuid") and image.get("data") else None

    def _polyline_to_sexp(self, polyline_data: Dict[str, Any]) -> List[Any]:
        """Convert polyline to S-expression."""
        sexp = [sexpdata.Symbol("polyline")]

        # Add points
        points = polyline_data.get("points", [])
        if points:
            pts_sexp = [sexpdata.Symbol("pts")]
            for point in points:
                x, y = point["x"], point["y"]
                # Format coordinates properly
                if isinstance(x, float) and x.is_integer():
                    x = int(x)
                if isinstance(y, float) and y.is_integer():
                    y = int(y)
                pts_sexp.append([sexpdata.Symbol("xy"), x, y])
            sexp.append(pts_sexp)

        # Add stroke
        stroke_width = polyline_data.get("stroke_width", config.defaults.stroke_width)
        stroke_type = polyline_data.get("stroke_type", config.defaults.stroke_type)
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add UUID
        if "uuid" in polyline_data:
            sexp.append([sexpdata.Symbol("uuid"), polyline_data["uuid"]])

        return sexp

    def _arc_to_sexp(self, arc_data: Dict[str, Any]) -> List[Any]:
        """Convert arc to S-expression."""
        sexp = [sexpdata.Symbol("arc")]

        # Add start, mid, end points
        for point_name in ["start", "mid", "end"]:
            point = arc_data.get(point_name, {"x": 0, "y": 0})
            x, y = point["x"], point["y"]
            # Format coordinates properly
            if isinstance(x, float) and x.is_integer():
                x = int(x)
            if isinstance(y, float) and y.is_integer():
                y = int(y)
            sexp.append([sexpdata.Symbol(point_name), x, y])

        # Add stroke
        stroke_width = arc_data.get("stroke_width", config.defaults.stroke_width)
        stroke_type = arc_data.get("stroke_type", config.defaults.stroke_type)
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = arc_data.get("fill_type", config.defaults.fill_type)
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in arc_data:
            sexp.append([sexpdata.Symbol("uuid"), arc_data["uuid"]])

        return sexp

    def _circle_to_sexp(self, circle_data: Dict[str, Any]) -> List[Any]:
        """Convert circle to S-expression."""
        sexp = [sexpdata.Symbol("circle")]

        # Add center
        center = circle_data.get("center", {"x": 0, "y": 0})
        x, y = center["x"], center["y"]
        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)
        sexp.append([sexpdata.Symbol("center"), x, y])

        # Add radius
        radius = circle_data.get("radius", 0)
        sexp.append([sexpdata.Symbol("radius"), radius])

        # Add stroke
        stroke_width = circle_data.get("stroke_width", config.defaults.stroke_width)
        stroke_type = circle_data.get("stroke_type", config.defaults.stroke_type)
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = circle_data.get("fill_type", config.defaults.fill_type)
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in circle_data:
            sexp.append([sexpdata.Symbol("uuid"), circle_data["uuid"]])

        return sexp

    def _bezier_to_sexp(self, bezier_data: Dict[str, Any]) -> List[Any]:
        """Convert bezier curve to S-expression."""
        sexp = [sexpdata.Symbol("bezier")]

        # Add points
        points = bezier_data.get("points", [])
        if points:
            pts_sexp = [sexpdata.Symbol("pts")]
            for point in points:
                x, y = point["x"], point["y"]
                # Format coordinates properly
                if isinstance(x, float) and x.is_integer():
                    x = int(x)
                if isinstance(y, float) and y.is_integer():
                    y = int(y)
                pts_sexp.append([sexpdata.Symbol("xy"), x, y])
            sexp.append(pts_sexp)

        # Add stroke
        stroke_width = bezier_data.get("stroke_width", config.defaults.stroke_width)
        stroke_type = bezier_data.get("stroke_type", config.defaults.stroke_type)
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = bezier_data.get("fill_type", config.defaults.fill_type)
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in bezier_data:
            sexp.append([sexpdata.Symbol("uuid"), bezier_data["uuid"]])

        return sexp

    def _rectangle_to_sexp(self, rectangle_data: Dict[str, Any]) -> List[Any]:
        """Convert rectangle element to S-expression."""
        sexp = [sexpdata.Symbol("rectangle")]

        # Add start point
        start = rectangle_data["start"]
        start_x, start_y = start["x"], start["y"]
        sexp.append([sexpdata.Symbol("start"), start_x, start_y])

        # Add end point
        end = rectangle_data["end"]
        end_x, end_y = end["x"], end["y"]
        sexp.append([sexpdata.Symbol("end"), end_x, end_y])

        # Add stroke
        stroke_width = rectangle_data.get("stroke_width", config.defaults.stroke_width)
        stroke_type = rectangle_data.get("stroke_type", config.defaults.stroke_type)
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        # Add stroke color if present
        if "stroke_color" in rectangle_data:
            r, g, b, a = rectangle_data["stroke_color"]
            stroke_sexp.append([sexpdata.Symbol("color"), r, g, b, a])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = rectangle_data.get("fill_type", config.defaults.fill_type)
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        # Add fill color if present
        if "fill_color" in rectangle_data:
            r, g, b, a = rectangle_data["fill_color"]
            fill_sexp.append([sexpdata.Symbol("color"), r, g, b, a])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in rectangle_data:
            sexp.append([sexpdata.Symbol("uuid"), rectangle_data["uuid"]])

        return sexp

    def _image_to_sexp(self, image_data: Dict[str, Any]) -> List[Any]:
        """Convert image element to S-expression."""
        sexp = [sexpdata.Symbol("image")]

        # Add position
        position = image_data.get("position", {"x": 0, "y": 0})
        pos_x, pos_y = position["x"], position["y"]
        sexp.append([sexpdata.Symbol("at"), pos_x, pos_y])

        # Add UUID
        if "uuid" in image_data:
            sexp.append([sexpdata.Symbol("uuid"), image_data["uuid"]])

        # Add scale if not default
        scale = image_data.get("scale", 1.0)
        if scale != 1.0:
            sexp.append([sexpdata.Symbol("scale"), scale])

        # Add image data
        # KiCad splits base64 data into multiple lines for readability
        # Each line is roughly 76 characters (standard base64 line length)
        data = image_data.get("data", "")
        if data:
            data_sexp = [sexpdata.Symbol("data")]
            # Split the data into 76-character chunks
            chunk_size = 76
            for i in range(0, len(data), chunk_size):
                data_sexp.append(data[i : i + chunk_size])
            sexp.append(data_sexp)

        return sexp

    def _graphic_to_sexp(self, graphic_data: Dict[str, Any]) -> List[Any]:
        """Convert graphics (rectangles, etc.) to S-expression."""
        # For now, we only support rectangles - this is the main graphics element we create
        sexp = [sexpdata.Symbol("rectangle")]

        # Add start position
        start = graphic_data.get("start", {})
        start_x = start.get("x", 0)
        start_y = start.get("y", 0)

        # Format coordinates properly (avoid unnecessary .0 for integers)
        if isinstance(start_x, float) and start_x.is_integer():
            start_x = int(start_x)
        if isinstance(start_y, float) and start_y.is_integer():
            start_y = int(start_y)

        sexp.append([sexpdata.Symbol("start"), start_x, start_y])

        # Add end position
        end = graphic_data.get("end", {})
        end_x = end.get("x", 0)
        end_y = end.get("y", 0)

        # Format coordinates properly (avoid unnecessary .0 for integers)
        if isinstance(end_x, float) and end_x.is_integer():
            end_x = int(end_x)
        if isinstance(end_y, float) and end_y.is_integer():
            end_y = int(end_y)

        sexp.append([sexpdata.Symbol("end"), end_x, end_y])

        # Add stroke information (KiCAD format: width, type, and optionally color)
        stroke = graphic_data.get("stroke", {})
        stroke_sexp = [sexpdata.Symbol("stroke")]

        # Stroke width - default to 0 to match KiCAD behavior
        stroke_width = stroke.get("width", 0)
        if isinstance(stroke_width, float) and stroke_width == 0.0:
            stroke_width = 0
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])

        # Stroke type - normalize to KiCAD format and validate
        stroke_type = stroke.get("type", "default")

        # KiCAD only supports these exact stroke types
        valid_kicad_types = {"solid", "dash", "dash_dot", "dash_dot_dot", "dot", "default"}

        # Map common variations to KiCAD format
        stroke_type_map = {
            "dashdot": "dash_dot",
            "dash-dot": "dash_dot",
            "dashdotdot": "dash_dot_dot",
            "dash-dot-dot": "dash_dot_dot",
            "solid": "solid",
            "dash": "dash",
            "dot": "dot",
            "default": "default",
        }

        # Normalize and validate
        normalized_stroke_type = stroke_type_map.get(stroke_type.lower(), stroke_type)
        if normalized_stroke_type not in valid_kicad_types:
            normalized_stroke_type = "default"  # Fallback to default for invalid types

        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(normalized_stroke_type)])

        # Stroke color (if specified) - KiCAD format uses RGB 0-255 values plus alpha
        stroke_color = stroke.get("color")
        if stroke_color:
            if isinstance(stroke_color, str):
                # Convert string color names to RGB 0-255 values
                color_rgb = self._color_to_rgb255(stroke_color)
                stroke_sexp.append([sexpdata.Symbol("color")] + color_rgb + [1])  # Add alpha=1
            elif isinstance(stroke_color, (list, tuple)) and len(stroke_color) >= 3:
                # Use provided RGB values directly
                stroke_sexp.append([sexpdata.Symbol("color")] + list(stroke_color))

        sexp.append(stroke_sexp)

        # Add fill information
        fill = graphic_data.get("fill", {"type": "none"})
        fill_type = fill.get("type", "none")
        fill_sexp = [sexpdata.Symbol("fill"), [sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)]]
        sexp.append(fill_sexp)

        # Add UUID (no quotes around UUID in KiCAD format)
        if "uuid" in graphic_data:
            uuid_str = graphic_data["uuid"]
            # Remove quotes and convert to Symbol to match KiCAD format
            uuid_clean = uuid_str.replace('"', "")
            sexp.append([sexpdata.Symbol("uuid"), sexpdata.Symbol(uuid_clean)])

        return sexp
