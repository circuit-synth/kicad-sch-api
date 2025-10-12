"""
Geometry utilities for KiCAD schematic manipulation.

Provides coordinate transformation, pin positioning, and geometric calculations
migrated from circuit-synth for improved maintainability.
"""

import logging
import math
from typing import Optional, Tuple

from .types import Point

logger = logging.getLogger(__name__)


def snap_to_grid(position: Tuple[float, float], grid_size: float = 2.54) -> Tuple[float, float]:
    """
    Snap a position to the nearest grid point.

    Args:
        position: (x, y) coordinate
        grid_size: Grid size in mm (default 2.54mm = 0.1 inch)

    Returns:
        Grid-aligned (x, y) coordinate
    """
    x, y = position
    aligned_x = round(x / grid_size) * grid_size
    aligned_y = round(y / grid_size) * grid_size
    return (aligned_x, aligned_y)


def points_equal(p1: Point, p2: Point, tolerance: float = 0.01) -> bool:
    """
    Check if two points are equal within tolerance.

    Args:
        p1: First point
        p2: Second point
        tolerance: Distance tolerance

    Returns:
        True if points are equal within tolerance
    """
    return abs(p1.x - p2.x) < tolerance and abs(p1.y - p2.y) < tolerance


def distance_between_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate distance between two points.

    Args:
        p1: First point (x, y)
        p2: Second point (x, y)

    Returns:
        Distance between points
    """
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def apply_transformation(
    point: Tuple[float, float],
    origin: Point,
    rotation: float,
    mirror: Optional[str] = None,
) -> Tuple[float, float]:
    """
    Apply rotation and mirroring transformation to a point.

    Migrated from circuit-synth for accurate pin position calculation.

    Args:
        point: Point to transform (x, y) relative to origin
        origin: Component origin point
        rotation: Rotation in degrees (0, 90, 180, 270)
        mirror: Mirror axis ("x" or "y" or None)

    Returns:
        Transformed absolute position (x, y)
    """
    x, y = point

    logger.debug(f"Transforming point ({x}, {y}) with rotation={rotation}°, mirror={mirror}")

    # Apply mirroring first
    if mirror == "x":
        x = -x
        logger.debug(f"After X mirror: ({x}, {y})")
    elif mirror == "y":
        y = -y
        logger.debug(f"After Y mirror: ({x}, {y})")

    # Apply rotation
    if rotation == 90:
        x, y = -y, x
        logger.debug(f"After 90° rotation: ({x}, {y})")
    elif rotation == 180:
        x, y = -x, -y
        logger.debug(f"After 180° rotation: ({x}, {y})")
    elif rotation == 270:
        x, y = y, -x
        logger.debug(f"After 270° rotation: ({x}, {y})")

    # Translate to absolute position
    final_x = origin.x + x
    final_y = origin.y + y

    logger.debug(f"Final absolute position: ({final_x}, {final_y})")
    return (final_x, final_y)
