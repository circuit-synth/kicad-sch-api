"""
Component bounding box calculations for Manhattan routing.

Adapted from circuit-synth's proven symbol geometry logic for accurate
KiCAD component bounds calculation and collision detection.
"""

import logging
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..library.cache import get_symbol_cache
from .types import Point, SchematicSymbol

logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Axis-aligned bounding box (adapted from circuit-synth BBox)."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        """Get bounding box width."""
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        """Get bounding box height."""
        return self.max_y - self.min_y

    @property
    def center(self) -> Point:
        """Get bounding box center point."""
        return Point((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)

    def contains_point(self, point: Point) -> bool:
        """Check if point is inside this bounding box."""
        return self.min_x <= point.x <= self.max_x and self.min_y <= point.y <= self.max_y

    def overlaps(self, other: "BoundingBox") -> bool:
        """Check if this bounding box overlaps with another."""
        return not (
            self.max_x < other.min_x  # this right < other left
            or self.min_x > other.max_x  # this left > other right
            or self.max_y < other.min_y  # this bottom < other top
            or self.min_y > other.max_y
        )  # this top > other bottom

    def expand(self, margin: float) -> "BoundingBox":
        """Return expanded bounding box with margin."""
        return BoundingBox(
            self.min_x - margin, self.min_y - margin, self.max_x + margin, self.max_y + margin
        )

    def __repr__(self) -> str:
        return f"BoundingBox(min_x={self.min_x:.2f}, min_y={self.min_y:.2f}, max_x={self.max_x:.2f}, max_y={self.max_y:.2f})"


class SymbolBoundingBoxCalculator:
    """
    Calculate accurate bounding boxes for KiCAD symbols.

    Adapted from circuit-synth SymbolBoundingBoxCalculator for compatibility
    with kicad-sch-api's symbol cache system.
    """

    # KiCAD default dimensions (from circuit-synth)
    DEFAULT_TEXT_HEIGHT = 2.54  # 100 mils
    DEFAULT_PIN_LENGTH = 2.54  # 100 mils
    DEFAULT_PIN_NAME_OFFSET = 0.508  # 20 mils
    DEFAULT_PIN_NUMBER_SIZE = 1.27  # 50 mils
    DEFAULT_PIN_TEXT_WIDTH_RATIO = 2.0  # Width to height ratio for pin text

    @classmethod
    def calculate_bounding_box(cls, symbol, include_properties: bool = True) -> BoundingBox:
        """
        Calculate accurate bounding box from SymbolDefinition.

        Args:
            symbol: SymbolDefinition from symbol cache
            include_properties: Whether to include space for Reference/Value labels

        Returns:
            BoundingBox with accurate dimensions
        """
        if not symbol:
            logger.warning("Symbol is None, using default bounding box")
            return BoundingBox(-2.54, -2.54, 2.54, 2.54)

        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")

        # Process pins
        for pin in symbol.pins:
            pin_bounds = cls._get_pin_bounds(pin)
            if pin_bounds:
                p_min_x, p_min_y, p_max_x, p_max_y = pin_bounds
                min_x = min(min_x, p_min_x)
                min_y = min(min_y, p_min_y)
                max_x = max(max_x, p_max_x)
                max_y = max(max_y, p_max_y)

        # Process graphics from raw KiCAD data
        if hasattr(symbol, "raw_kicad_data") and symbol.raw_kicad_data:
            graphics_bounds = cls._extract_graphics_bounds(symbol.raw_kicad_data)
            for g_min_x, g_min_y, g_max_x, g_max_y in graphics_bounds:
                min_x = min(min_x, g_min_x)
                min_y = min(min_y, g_min_y)
                max_x = max(max_x, g_max_x)
                max_y = max(max_y, g_max_y)

        # Fallback for known symbols if no bounds found
        if min_x == float("inf") or max_x == float("-inf"):
            if "Device:R" in symbol.lib_id:
                # Standard resistor dimensions
                min_x, min_y, max_x, max_y = -1.016, -2.54, 1.016, 2.54
            else:
                # Default fallback
                min_x, min_y, max_x, max_y = -2.54, -2.54, 2.54, 2.54

        # Add margin for safety
        margin = 0.254  # 10 mils
        min_x -= margin
        min_y -= margin
        max_x += margin
        max_y += margin

        # Include space for properties if requested
        if include_properties:
            property_width = 10.0  # Conservative estimate
            property_height = cls.DEFAULT_TEXT_HEIGHT

            # Reference above, Value/Footprint below
            min_y -= 5.0 + property_height
            max_y += 10.0 + property_height

            # Extend horizontally for property text
            center_x = (min_x + max_x) / 2
            min_x = min(min_x, center_x - property_width / 2)
            max_x = max(max_x, center_x + property_width / 2)

        return BoundingBox(min_x, min_y, max_x, max_y)

    @classmethod
    def _get_pin_bounds(cls, pin) -> Optional[Tuple[float, float, float, float]]:
        """Calculate pin bounds including labels."""
        x, y = pin.position.x, pin.position.y
        length = getattr(pin, "length", cls.DEFAULT_PIN_LENGTH)
        rotation = getattr(pin, "rotation", 0)

        # Calculate pin endpoint
        angle_rad = math.radians(rotation)
        end_x = x + length * math.cos(angle_rad)
        end_y = y + length * math.sin(angle_rad)

        # Start with pin line bounds
        min_x = min(x, end_x)
        min_y = min(y, end_y)
        max_x = max(x, end_x)
        max_y = max(y, end_y)

        # Add space for pin name
        pin_name = getattr(pin, "name", "")
        if pin_name and pin_name != "~":
            name_width = len(pin_name) * cls.DEFAULT_TEXT_HEIGHT * cls.DEFAULT_PIN_TEXT_WIDTH_RATIO

            # Adjust bounds based on pin orientation
            if rotation == 0:  # Right
                max_x = end_x + name_width
            elif rotation == 180:  # Left
                min_x = end_x - name_width
            elif rotation == 90:  # Up
                max_y = end_y + name_width
            elif rotation == 270:  # Down
                min_y = end_y - name_width

        # Add margin for pin number
        pin_number = getattr(pin, "number", "")
        if pin_number:
            margin = cls.DEFAULT_PIN_NUMBER_SIZE * 1.5
            min_x -= margin
            min_y -= margin
            max_x += margin
            max_y += margin

        return (min_x, min_y, max_x, max_y)

    @classmethod
    def _extract_graphics_bounds(cls, raw_data) -> List[Tuple[float, float, float, float]]:
        """Extract graphics bounds from raw KiCAD symbol data."""
        bounds_list = []

        if not isinstance(raw_data, list):
            return bounds_list

        # Look through symbol sub-definitions for graphics
        for item in raw_data[1:]:  # Skip symbol name
            if isinstance(item, list) and len(item) > 0:
                # Check for symbol unit definitions like "R_0_1"
                if hasattr(item[0], "value") and item[0].value == "symbol":
                    bounds_list.extend(cls._extract_unit_graphics_bounds(item))

        return bounds_list

    @classmethod
    def _extract_unit_graphics_bounds(cls, unit_data) -> List[Tuple[float, float, float, float]]:
        """Extract graphics bounds from symbol unit definition."""
        bounds_list = []

        for item in unit_data[1:]:  # Skip unit name
            if isinstance(item, list) and len(item) > 0 and hasattr(item[0], "value"):
                element_type = item[0].value

                if element_type == "rectangle":
                    bounds = cls._extract_rectangle_bounds(item)
                    if bounds:
                        bounds_list.append(bounds)
                elif element_type == "circle":
                    bounds = cls._extract_circle_bounds(item)
                    if bounds:
                        bounds_list.append(bounds)
                elif element_type == "polyline":
                    bounds = cls._extract_polyline_bounds(item)
                    if bounds:
                        bounds_list.append(bounds)
                elif element_type == "arc":
                    bounds = cls._extract_arc_bounds(item)
                    if bounds:
                        bounds_list.append(bounds)

        return bounds_list

    @classmethod
    def _extract_rectangle_bounds(cls, rect_data) -> Optional[Tuple[float, float, float, float]]:
        """Extract bounds from rectangle definition."""
        try:
            start_point = None
            end_point = None

            for item in rect_data[1:]:
                if isinstance(item, list) and len(item) >= 3:
                    if hasattr(item[0], "value") and item[0].value == "start":
                        start_point = (float(item[1]), float(item[2]))
                    elif hasattr(item[0], "value") and item[0].value == "end":
                        end_point = (float(item[1]), float(item[2]))

            if start_point and end_point:
                min_x = min(start_point[0], end_point[0])
                min_y = min(start_point[1], end_point[1])
                max_x = max(start_point[0], end_point[0])
                max_y = max(start_point[1], end_point[1])
                return (min_x, min_y, max_x, max_y)

        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing rectangle: {e}")

        return None

    @classmethod
    def _extract_circle_bounds(cls, circle_data) -> Optional[Tuple[float, float, float, float]]:
        """Extract bounds from circle definition."""
        try:
            center = None
            radius = 0

            for item in circle_data[1:]:
                if isinstance(item, list) and len(item) >= 3:
                    if hasattr(item[0], "value") and item[0].value == "center":
                        center = (float(item[1]), float(item[2]))
                elif isinstance(item, list) and len(item) >= 2:
                    if hasattr(item[0], "value") and item[0].value == "radius":
                        radius = float(item[1])

            if center and radius > 0:
                cx, cy = center
                return (cx - radius, cy - radius, cx + radius, cy + radius)

        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing circle: {e}")

        return None

    @classmethod
    def _extract_polyline_bounds(cls, poly_data) -> Optional[Tuple[float, float, float, float]]:
        """Extract bounds from polyline definition."""
        coordinates = []

        try:
            for item in poly_data[1:]:
                if isinstance(item, list) and len(item) > 0:
                    if hasattr(item[0], "value") and item[0].value == "pts":
                        for pt_item in item[1:]:
                            if isinstance(pt_item, list) and len(pt_item) >= 3:
                                if hasattr(pt_item[0], "value") and pt_item[0].value == "xy":
                                    coordinates.append((float(pt_item[1]), float(pt_item[2])))

            if coordinates:
                min_x = min(coord[0] for coord in coordinates)
                min_y = min(coord[1] for coord in coordinates)
                max_x = max(coord[0] for coord in coordinates)
                max_y = max(coord[1] for coord in coordinates)
                return (min_x, min_y, max_x, max_y)

        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing polyline: {e}")

        return None

    @classmethod
    def _extract_arc_bounds(cls, arc_data) -> Optional[Tuple[float, float, float, float]]:
        """Extract bounds from arc definition (simplified approach)."""
        try:
            start = None
            mid = None
            end = None

            for item in arc_data[1:]:
                if isinstance(item, list) and len(item) >= 3:
                    if hasattr(item[0], "value"):
                        if item[0].value == "start":
                            start = (float(item[1]), float(item[2]))
                        elif item[0].value == "mid":
                            mid = (float(item[1]), float(item[2]))
                        elif item[0].value == "end":
                            end = (float(item[1]), float(item[2]))

            if start and end:
                # Simple approach: use bounding box of start/mid/end points
                points = [start, end]
                if mid:
                    points.append(mid)

                min_x = min(p[0] for p in points)
                min_y = min(p[1] for p in points)
                max_x = max(p[0] for p in points)
                max_y = max(p[1] for p in points)
                return (min_x, min_y, max_x, max_y)

        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing arc: {e}")

        return None


def get_component_bounding_box(
    component: SchematicSymbol, include_properties: bool = True
) -> BoundingBox:
    """
    Get component bounding box in world coordinates.

    Args:
        component: The schematic component
        include_properties: Whether to include space for Reference/Value labels

    Returns:
        BoundingBox in world coordinates
    """
    # Get symbol definition
    cache = get_symbol_cache()
    symbol = cache.get_symbol(component.lib_id)

    if not symbol:
        logger.warning(f"Symbol not found for {component.lib_id}")
        # Return default size centered at component position
        default_size = 5.08  # 4 grid units
        return BoundingBox(
            component.position.x - default_size / 2,
            component.position.y - default_size / 2,
            component.position.x + default_size / 2,
            component.position.y + default_size / 2,
        )

    # Calculate symbol bounding box
    symbol_bbox = SymbolBoundingBoxCalculator.calculate_bounding_box(symbol, include_properties)

    # Transform to world coordinates with rotation
    # Apply rotation matrix to bounding box corners, then find new min/max
    import math

    angle_rad = math.radians(component.rotation)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Get all 4 corners of the symbol bounding box
    corners = [
        (symbol_bbox.min_x, symbol_bbox.min_y),  # Bottom-left
        (symbol_bbox.max_x, symbol_bbox.min_y),  # Bottom-right
        (symbol_bbox.max_x, symbol_bbox.max_y),  # Top-right
        (symbol_bbox.min_x, symbol_bbox.max_y),  # Top-left
    ]

    # Rotate each corner using standard 2D rotation matrix
    rotated_corners = []
    for x, y in corners:
        rotated_x = x * cos_a - y * sin_a
        rotated_y = x * sin_a + y * cos_a
        rotated_corners.append((rotated_x, rotated_y))

    # Find min/max of rotated corners
    rotated_xs = [x for x, y in rotated_corners]
    rotated_ys = [y for x, y in rotated_corners]

    world_bbox = BoundingBox(
        component.position.x + min(rotated_xs),
        component.position.y + min(rotated_ys),
        component.position.x + max(rotated_xs),
        component.position.y + max(rotated_ys),
    )

    logger.debug(
        f"Component {component.reference} at {component.rotation}° world bbox: {world_bbox}"
    )
    return world_bbox


def get_schematic_component_bboxes(components: List[SchematicSymbol]) -> List[BoundingBox]:
    """Get bounding boxes for all components in a schematic."""
    return [get_component_bounding_box(comp) for comp in components]


def check_path_collision(
    start: Point, end: Point, obstacles: List[BoundingBox], clearance: float = 1.27
) -> bool:
    """
    Check if a straight line path collides with any obstacle bounding boxes.

    Args:
        start: Starting point
        end: Ending point
        obstacles: List of obstacle bounding boxes
        clearance: Minimum clearance from obstacles (default: 1 grid unit)

    Returns:
        True if path collides with any obstacle
    """
    # Expand obstacles by clearance
    expanded_obstacles = [obs.expand(clearance) for obs in obstacles]

    # Check if line segment intersects any expanded obstacle
    for bbox in expanded_obstacles:
        if _line_intersects_bbox(start, end, bbox):
            logger.debug(f"Path collision detected with obstacle {bbox}")
            return True

    return False


def _line_intersects_bbox(start: Point, end: Point, bbox: BoundingBox) -> bool:
    """
    Check if line segment intersects bounding box using line-box intersection.

    Uses efficient line-box intersection algorithm.
    """
    # Get line direction
    dx = end.x - start.x
    dy = end.y - start.y

    # Handle degenerate case (point)
    if dx == 0 and dy == 0:
        return bbox.contains_point(start)

    # Calculate intersection parameters using slab method
    if dx == 0:
        # Vertical line
        if start.x < bbox.min_x or start.x > bbox.max_x:
            return False
        t_min = (bbox.min_y - start.y) / dy if dy != 0 else float("-inf")
        t_max = (bbox.max_y - start.y) / dy if dy != 0 else float("inf")
        if t_min > t_max:
            t_min, t_max = t_max, t_min
    elif dy == 0:
        # Horizontal line
        if start.y < bbox.min_y or start.y > bbox.max_y:
            return False
        t_min = (bbox.min_x - start.x) / dx
        t_max = (bbox.max_x - start.x) / dx
        if t_min > t_max:
            t_min, t_max = t_max, t_min
    else:
        # General case
        t_min_x = (bbox.min_x - start.x) / dx
        t_max_x = (bbox.max_x - start.x) / dx
        if t_min_x > t_max_x:
            t_min_x, t_max_x = t_max_x, t_min_x

        t_min_y = (bbox.min_y - start.y) / dy
        t_max_y = (bbox.max_y - start.y) / dy
        if t_min_y > t_max_y:
            t_min_y, t_max_y = t_max_y, t_min_y

        t_min = max(t_min_x, t_min_y)
        t_max = min(t_max_x, t_max_y)

    # Check if intersection is within line segment [0, 1]
    return t_min <= t_max and t_min <= 1.0 and t_max >= 0.0
