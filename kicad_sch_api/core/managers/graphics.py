"""
Graphics Manager for KiCAD schematic graphic elements.

Handles geometric shapes, drawing elements, and visual annotations including
rectangles, circles, polylines, arcs, and images while managing styling
and positioning.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from ..types import Point
from .base import BaseManager

logger = logging.getLogger(__name__)


class GraphicsManager(BaseManager):
    """
    Manages graphic elements and drawing shapes in KiCAD schematics.

    Responsible for:
    - Geometric shape creation (rectangles, circles, arcs)
    - Polyline and path management
    - Image placement and scaling
    - Stroke and fill styling
    - Layer management for graphics
    """

    def __init__(self, schematic_data: Dict[str, Any]):
        """
        Initialize GraphicsManager.

        Args:
            schematic_data: Reference to schematic data
        """
        super().__init__(schematic_data)

    def add_rectangle(
        self,
        start: Union[Point, Tuple[float, float]],
        end: Union[Point, Tuple[float, float]],
        stroke: Optional[Dict[str, Any]] = None,
        fill: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add a rectangle to the schematic.

        Args:
            start: Top-left corner position
            end: Bottom-right corner position
            stroke: Stroke properties (width, type, color)
            fill: Fill properties (color, type)
            uuid_str: Optional UUID

        Returns:
            UUID of created rectangle
        """
        if isinstance(start, tuple):
            start = Point(start[0], start[1])
        if isinstance(end, tuple):
            end = Point(end[0], end[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if stroke is None:
            stroke = self._get_default_stroke()

        # Convert to parser format (flat keys, dict positions)
        rectangle_data = {
            "uuid": uuid_str,
            "start": {"x": start.x, "y": start.y},
            "end": {"x": end.x, "y": end.y},
            "stroke_width": stroke.get("width", 0.127),
            "stroke_type": stroke.get("type", "solid"),
        }

        # Add stroke color if provided
        if "color" in stroke:
            rectangle_data["stroke_color"] = stroke["color"]

        # Add fill type if provided
        if fill is not None:
            rectangle_data["fill_type"] = fill.get("type", "none")
            # Add fill color if provided
            if "color" in fill:
                rectangle_data["fill_color"] = fill["color"]
        else:
            rectangle_data["fill_type"] = "none"

        # Add to schematic data
        if "rectangles" not in self._data:
            self._data["rectangles"] = []
        self._data["rectangles"].append(rectangle_data)

        logger.debug(f"Added rectangle from {start} to {end}")
        return uuid_str

    def add_circle(
        self,
        center: Union[Point, Tuple[float, float]],
        radius: float,
        stroke: Optional[Dict[str, Any]] = None,
        fill: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add a circle to the schematic.

        Args:
            center: Center position
            radius: Circle radius
            stroke: Stroke properties
            fill: Fill properties
            uuid_str: Optional UUID

        Returns:
            UUID of created circle
        """
        if isinstance(center, tuple):
            center = Point(center[0], center[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if stroke is None:
            stroke = self._get_default_stroke()

        circle_data = {
            "uuid": uuid_str,
            "center": [center.x, center.y],
            "radius": radius,
            "stroke": stroke,
        }

        if fill is not None:
            circle_data["fill"] = fill

        # Add to schematic data
        if "circle" not in self._data:
            self._data["circle"] = []
        self._data["circle"].append(circle_data)

        logger.debug(f"Added circle at {center} with radius {radius}")
        return uuid_str

    def add_arc(
        self,
        start: Union[Point, Tuple[float, float]],
        mid: Union[Point, Tuple[float, float]],
        end: Union[Point, Tuple[float, float]],
        stroke: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add an arc to the schematic (defined by three points).

        Args:
            start: Arc start point
            mid: Arc midpoint
            end: Arc end point
            stroke: Stroke properties
            uuid_str: Optional UUID

        Returns:
            UUID of created arc
        """
        if isinstance(start, tuple):
            start = Point(start[0], start[1])
        if isinstance(mid, tuple):
            mid = Point(mid[0], mid[1])
        if isinstance(end, tuple):
            end = Point(end[0], end[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if stroke is None:
            stroke = self._get_default_stroke()

        arc_data = {
            "uuid": uuid_str,
            "start": [start.x, start.y],
            "mid": [mid.x, mid.y],
            "end": [end.x, end.y],
            "stroke": stroke,
        }

        # Add to schematic data
        if "arc" not in self._data:
            self._data["arc"] = []
        self._data["arc"].append(arc_data)

        logger.debug(f"Added arc from {start} through {mid} to {end}")
        return uuid_str

    def add_polyline(
        self,
        points: List[Union[Point, Tuple[float, float]]],
        stroke: Optional[Dict[str, Any]] = None,
        fill: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add a polyline (multi-segment line) to the schematic.

        Args:
            points: List of points defining the polyline
            stroke: Stroke properties
            fill: Fill properties (for closed polylines)
            uuid_str: Optional UUID

        Returns:
            UUID of created polyline
        """
        if len(points) < 2:
            raise ValueError("Polyline must have at least 2 points")

        # Convert tuples to Points
        converted_points = []
        for point in points:
            if isinstance(point, tuple):
                converted_points.append(Point(point[0], point[1]))
            else:
                converted_points.append(point)

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if stroke is None:
            stroke = self._get_default_stroke()

        polyline_data = {
            "uuid": uuid_str,
            "pts": [[pt.x, pt.y] for pt in converted_points],
            "stroke": stroke,
        }

        if fill is not None:
            polyline_data["fill"] = fill

        # Add to schematic data
        if "polyline" not in self._data:
            self._data["polyline"] = []
        self._data["polyline"].append(polyline_data)

        logger.debug(f"Added polyline with {len(points)} points")
        return uuid_str

    def add_image(
        self,
        position: Union[Point, Tuple[float, float]],
        scale: float = 1.0,
        image_data: Optional[str] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add an image to the schematic.

        Args:
            position: Image position
            scale: Image scale factor
            image_data: Base64 encoded image data (optional)
            uuid_str: Optional UUID

        Returns:
            UUID of created image
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        # Store in parser format (position as dict)
        image_element = {
            "uuid": uuid_str,
            "position": {"x": position.x, "y": position.y},
            "scale": scale,
        }

        if image_data is not None:
            image_element["data"] = image_data

        # Add to schematic data
        if "images" not in self._data:
            self._data["images"] = []
        self._data["images"].append(image_element)

        logger.debug(f"Added image at {position} with scale {scale}")
        return uuid_str

    def remove_rectangle(self, uuid_str: str) -> bool:
        """
        Remove a rectangle by UUID.

        Args:
            uuid_str: UUID of rectangle to remove

        Returns:
            True if removed, False if not found
        """
        return self._remove_graphic_element("rectangle", uuid_str)

    def remove_circle(self, uuid_str: str) -> bool:
        """
        Remove a circle by UUID.

        Args:
            uuid_str: UUID of circle to remove

        Returns:
            True if removed, False if not found
        """
        return self._remove_graphic_element("circle", uuid_str)

    def remove_arc(self, uuid_str: str) -> bool:
        """
        Remove an arc by UUID.

        Args:
            uuid_str: UUID of arc to remove

        Returns:
            True if removed, False if not found
        """
        return self._remove_graphic_element("arc", uuid_str)

    def remove_polyline(self, uuid_str: str) -> bool:
        """
        Remove a polyline by UUID.

        Args:
            uuid_str: UUID of polyline to remove

        Returns:
            True if removed, False if not found
        """
        return self._remove_graphic_element("polyline", uuid_str)

    def remove_image(self, uuid_str: str) -> bool:
        """
        Remove an image by UUID.

        Args:
            uuid_str: UUID of image to remove

        Returns:
            True if removed, False if not found
        """
        return self._remove_graphic_element("image", uuid_str)

    def update_stroke(self, uuid_str: str, stroke: Dict[str, Any]) -> bool:
        """
        Update stroke properties for a graphic element.

        Args:
            uuid_str: UUID of element
            stroke: New stroke properties

        Returns:
            True if updated, False if not found
        """
        for element_type in ["rectangle", "circle", "arc", "polyline"]:
            elements = self._data.get(element_type, [])
            for element in elements:
                if element.get("uuid") == uuid_str:
                    element["stroke"] = stroke
                    logger.debug(f"Updated stroke for {element_type} {uuid_str}")
                    return True

        logger.warning(f"Graphic element not found for stroke update: {uuid_str}")
        return False

    def update_fill(self, uuid_str: str, fill: Dict[str, Any]) -> bool:
        """
        Update fill properties for a graphic element.

        Args:
            uuid_str: UUID of element
            fill: New fill properties

        Returns:
            True if updated, False if not found
        """
        for element_type in ["rectangle", "circle", "polyline"]:
            elements = self._data.get(element_type, [])
            for element in elements:
                if element.get("uuid") == uuid_str:
                    element["fill"] = fill
                    logger.debug(f"Updated fill for {element_type} {uuid_str}")
                    return True

        logger.warning(f"Graphic element not found for fill update: {uuid_str}")
        return False

    def get_graphics_in_area(
        self,
        area_start: Union[Point, Tuple[float, float]],
        area_end: Union[Point, Tuple[float, float]],
    ) -> List[Dict[str, Any]]:
        """
        Get all graphic elements within a specified area.

        Args:
            area_start: Area top-left corner
            area_end: Area bottom-right corner

        Returns:
            List of graphic elements in the area
        """
        if isinstance(area_start, tuple):
            area_start = Point(area_start[0], area_start[1])
        if isinstance(area_end, tuple):
            area_end = Point(area_end[0], area_end[1])

        result = []

        # Check rectangles
        rectangles = self._data.get("rectangle", [])
        for rect in rectangles:
            rect_start = Point(rect["start"][0], rect["start"][1])
            rect_end = Point(rect["end"][0], rect["end"][1])
            if self._rectangles_overlap(area_start, area_end, rect_start, rect_end):
                result.append({"type": "rectangle", "data": rect})

        # Check circles
        circles = self._data.get("circle", [])
        for circle in circles:
            center = Point(circle["center"][0], circle["center"][1])
            radius = circle["radius"]
            if self._circle_in_area(center, radius, area_start, area_end):
                result.append({"type": "circle", "data": circle})

        # Check polylines
        polylines = self._data.get("polyline", [])
        for polyline in polylines:
            if self._polyline_in_area(polyline["pts"], area_start, area_end):
                result.append({"type": "polyline", "data": polyline})

        # Check arcs
        arcs = self._data.get("arc", [])
        for arc in arcs:
            arc_start = Point(arc["start"][0], arc["start"][1])
            arc_end = Point(arc["end"][0], arc["end"][1])
            if self._point_in_area(arc_start, area_start, area_end) or self._point_in_area(
                arc_end, area_start, area_end
            ):
                result.append({"type": "arc", "data": arc})

        # Check images
        images = self._data.get("image", [])
        for image in images:
            pos = Point(image["at"][0], image["at"][1])
            if self._point_in_area(pos, area_start, area_end):
                result.append({"type": "image", "data": image})

        return result

    def list_all_graphics(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all graphic elements in the schematic.

        Returns:
            Dictionary with graphic element types and their data
        """
        result = {}
        for element_type in ["rectangle", "circle", "arc", "polyline", "image"]:
            elements = self._data.get(element_type, [])
            result[element_type] = [{"uuid": elem.get("uuid"), "data": elem} for elem in elements]

        return result

    def get_graphics_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about graphic elements.

        Returns:
            Dictionary with graphics statistics
        """
        stats = {}
        total_elements = 0

        for element_type in ["rectangle", "circle", "arc", "polyline", "image"]:
            count = len(self._data.get(element_type, []))
            stats[element_type] = count
            total_elements += count

        stats["total_graphics"] = total_elements
        return stats

    def _remove_graphic_element(self, element_type: str, uuid_str: str) -> bool:
        """Remove graphic element by UUID from specified type."""
        elements = self._data.get(element_type, [])
        for i, element in enumerate(elements):
            if element.get("uuid") == uuid_str:
                del elements[i]
                logger.debug(f"Removed {element_type}: {uuid_str}")
                return True
        return False

    def _get_default_stroke(self) -> Dict[str, Any]:
        """Get default stroke properties."""
        return {"width": 0.254, "type": "default"}

    def _rectangles_overlap(
        self, area_start: Point, area_end: Point, rect_start: Point, rect_end: Point
    ) -> bool:
        """Check if two rectangles overlap."""
        return not (
            area_end.x < rect_start.x
            or area_start.x > rect_end.x
            or area_end.y < rect_start.y
            or area_start.y > rect_end.y
        )

    def _circle_in_area(
        self, center: Point, radius: float, area_start: Point, area_end: Point
    ) -> bool:
        """Check if circle intersects with area."""
        # Check if circle center is in area or if circle overlaps area bounds
        if self._point_in_area(center, area_start, area_end):
            return True

        # Check if circle intersects with area edges
        closest_x = max(area_start.x, min(center.x, area_end.x))
        closest_y = max(area_start.y, min(center.y, area_end.y))
        distance = Point(closest_x, closest_y).distance_to(center)

        return distance <= radius

    def _polyline_in_area(
        self, points: List[List[float]], area_start: Point, area_end: Point
    ) -> bool:
        """Check if any part of polyline is in area."""
        for point_coords in points:
            point = Point(point_coords[0], point_coords[1])
            if self._point_in_area(point, area_start, area_end):
                return True
        return False

    def _point_in_area(self, point: Point, area_start: Point, area_end: Point) -> bool:
        """Check if point is within area."""
        return area_start.x <= point.x <= area_end.x and area_start.y <= point.y <= area_end.y

    def validate_graphics(self) -> List[str]:
        """
        Validate graphic elements for consistency and correctness.

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check rectangles
        rectangles = self._data.get("rectangle", [])
        for rect in rectangles:
            start = Point(rect["start"][0], rect["start"][1])
            end = Point(rect["end"][0], rect["end"][1])
            if start.x >= end.x or start.y >= end.y:
                warnings.append(f"Rectangle {rect.get('uuid')} has invalid dimensions")

        # Check circles
        circles = self._data.get("circle", [])
        for circle in circles:
            radius = circle.get("radius", 0)
            if radius <= 0:
                warnings.append(f"Circle {circle.get('uuid')} has invalid radius: {radius}")

        # Check polylines
        polylines = self._data.get("polyline", [])
        for polyline in polylines:
            points = polyline.get("pts", [])
            if len(points) < 2:
                warnings.append(f"Polyline {polyline.get('uuid')} has too few points")

        return warnings
