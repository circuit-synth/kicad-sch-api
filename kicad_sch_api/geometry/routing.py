"""
Orthogonal routing algorithms for automatic wire routing between points.

This module provides functions for creating orthogonal (Manhattan) wire routes
between component pins, with support for direct routing when points are aligned
and L-shaped routing when they are not.

CRITICAL: KiCAD Y-axis is INVERTED (+Y is DOWN)
- Lower Y values = visually HIGHER on screen (top)
- Higher Y values = visually LOWER on screen (bottom)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from kicad_sch_api.core.types import Point


class CornerDirection(Enum):
    """Direction preference for L-shaped routing corner."""

    AUTO = "auto"  # Automatic selection based on distance heuristic
    HORIZONTAL_FIRST = "horizontal_first"  # Route horizontally, then vertically
    VERTICAL_FIRST = "vertical_first"  # Route vertically, then horizontally


@dataclass
class RoutingResult:
    """
    Result of orthogonal routing calculation.

    Attributes:
        segments: List of wire segments as (start, end) point tuples
        corner: Corner junction point (None if direct routing)
        is_direct: True if routing is a single straight line
    """

    segments: List[Tuple[Point, Point]]
    corner: Optional[Point]
    is_direct: bool


def create_orthogonal_routing(
    from_pos: Point, to_pos: Point, corner_direction: CornerDirection = CornerDirection.AUTO
) -> RoutingResult:
    """
    Create orthogonal (Manhattan) routing between two points.

    Generates either direct routing (when points are aligned on same axis)
    or L-shaped routing (when points require a corner).

    CRITICAL: Remember KiCAD Y-axis is INVERTED:
    - Lower Y values = visually HIGHER (top of screen)
    - Higher Y values = visually LOWER (bottom of screen)

    Args:
        from_pos: Starting point
        to_pos: Ending point
        corner_direction: Direction preference for L-shaped corner
            - AUTO: Choose based on distance heuristic (horizontal if dx >= dy)
            - HORIZONTAL_FIRST: Route horizontally, then vertically
            - VERTICAL_FIRST: Route vertically, then horizontally

    Returns:
        RoutingResult with segments list, corner point, and direct flag

    Examples:
        >>> # Direct horizontal routing (aligned on Y axis)
        >>> result = create_orthogonal_routing(
        ...     Point(100, 100),
        ...     Point(150, 100)
        ... )
        >>> result.is_direct
        True
        >>> len(result.segments)
        1

        >>> # L-shaped routing (not aligned)
        >>> result = create_orthogonal_routing(
        ...     Point(100, 100),
        ...     Point(150, 125),
        ...     corner_direction=CornerDirection.HORIZONTAL_FIRST
        ... )
        >>> result.is_direct
        False
        >>> len(result.segments)
        2
        >>> result.corner
        Point(x=150.0, y=100.0)
    """
    # Check if points are aligned on same axis (direct routing possible)
    if from_pos.x == to_pos.x or from_pos.y == to_pos.y:
        # Direct line - no corner needed
        return RoutingResult(segments=[(from_pos, to_pos)], corner=None, is_direct=True)

    # Points are not aligned - need L-shaped routing with corner
    corner = _calculate_corner_point(from_pos, to_pos, corner_direction)

    return RoutingResult(
        segments=[(from_pos, corner), (corner, to_pos)], corner=corner, is_direct=False
    )


def _calculate_corner_point(
    from_pos: Point, to_pos: Point, corner_direction: CornerDirection
) -> Point:
    """
    Calculate the corner point for L-shaped routing.

    Args:
        from_pos: Starting point
        to_pos: Ending point
        corner_direction: Direction preference for corner

    Returns:
        Corner point position
    """
    if corner_direction == CornerDirection.HORIZONTAL_FIRST:
        # Route horizontally first, then vertically
        # Corner is at destination X, source Y
        return Point(to_pos.x, from_pos.y)

    elif corner_direction == CornerDirection.VERTICAL_FIRST:
        # Route vertically first, then horizontally
        # Corner is at source X, destination Y
        return Point(from_pos.x, to_pos.y)

    else:  # AUTO
        # Heuristic: prefer horizontal first if horizontal distance >= vertical distance
        dx = abs(to_pos.x - from_pos.x)
        dy = abs(to_pos.y - from_pos.y)

        if dx >= dy:
            # Horizontal distance is greater - route horizontally first
            return Point(to_pos.x, from_pos.y)
        else:
            # Vertical distance is greater - route vertically first
            return Point(from_pos.x, to_pos.y)


def validate_routing_result(result: RoutingResult) -> bool:
    """
    Validate that routing result is correct.

    Checks:
    - All segments are orthogonal (horizontal or vertical)
    - Segments connect end-to-end
    - Corner point matches segment endpoints if present

    Args:
        result: Routing result to validate

    Returns:
        True if routing is valid

    Raises:
        ValueError: If routing is invalid
    """
    if not result.segments:
        raise ValueError("Routing must have at least one segment")

    for start, end in result.segments:
        # Check orthogonality - each segment must be horizontal OR vertical
        if start.x != end.x and start.y != end.y:
            raise ValueError(
                f"Segment ({start}, {end}) is not orthogonal - "
                f"must be horizontal (same Y) or vertical (same X)"
            )

    # Check segment connectivity - segments must connect end-to-end
    for i in range(len(result.segments) - 1):
        current_end = result.segments[i][1]
        next_start = result.segments[i + 1][0]

        if current_end.x != next_start.x or current_end.y != next_start.y:
            raise ValueError(
                f"Segments not connected: segment {i} ends at {current_end}, "
                f"segment {i+1} starts at {next_start}"
            )

    # Check corner consistency
    if result.corner is not None:
        if len(result.segments) < 2:
            raise ValueError("Corner specified but less than 2 segments present")

        # Corner should be the endpoint of first segment and startpoint of second
        first_end = result.segments[0][1]
        second_start = result.segments[1][0]

        if (
            result.corner.x != first_end.x
            or result.corner.y != first_end.y
            or result.corner.x != second_start.x
            or result.corner.y != second_start.y
        ):
            raise ValueError(
                f"Corner point {result.corner} does not match segment endpoints: "
                f"first segment ends at {first_end}, second starts at {second_start}"
            )

    return True
