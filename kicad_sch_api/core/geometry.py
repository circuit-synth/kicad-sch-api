"""
Geometry utilities for KiCAD schematic manipulation.

Provides coordinate transformation, pin positioning, and geometric calculations
migrated from circuit-synth for improved maintainability.
"""

import logging
import math
from typing import Optional, Tuple, Union

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

    CRITICAL: Symbol coordinates use normal Y-axis (+Y is up), but schematic
    coordinates use inverted Y-axis (+Y is down). We must negate Y from symbol
    space before applying transformations.

    Args:
        point: Point to transform (x, y) relative to origin in SYMBOL space
        origin: Component origin point in SCHEMATIC space
        rotation: Rotation in degrees (0, 90, 180, 270)
        mirror: Mirror axis ("x" or "y" or None)

    Returns:
        Transformed absolute position (x, y) in SCHEMATIC space
    """
    x, y = point

    logger.debug(f"Transforming point ({x}, {y}) with rotation={rotation}°, mirror={mirror}")

    # CRITICAL: Negate Y to convert from symbol space (normal Y) to schematic space (inverted Y)
    # This must happen BEFORE rotation/mirroring
    y = -y
    logger.debug(f"After Y-axis inversion (symbol→schematic): ({x}, {y})")

    # Apply mirroring
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


def calculate_position_for_pin(
    pin_local_position: Union[Point, Tuple[float, float]],
    desired_pin_position: Union[Point, Tuple[float, float]],
    rotation: float = 0.0,
    mirror: Optional[str] = None,
    grid_size: float = 1.27,
) -> Point:
    """
    Calculate component position needed to place a specific pin at a desired location.

    This is the inverse of get_pin_position() - given where you want a pin to be,
    it calculates where the component center needs to be placed.

    Useful for aligning components by their pins rather than their centers, which
    is essential for clean horizontal signal flows without unnecessary wire jogs.

    Args:
        pin_local_position: Pin position in symbol space (from symbol definition)
        desired_pin_position: Where you want the pin to be in schematic space
        rotation: Component rotation in degrees (0, 90, 180, 270)
        mirror: Mirror axis ("x" or "y" or None) - currently unused
        grid_size: Grid size for snapping result (default 1.27mm = 50mil)

    Returns:
        Component position that will place the pin at desired_pin_position

    Example:
        >>> # Place resistor so pin 2 is at (150, 100)
        >>> pin_pos = Point(0, -3.81)  # Pin 2 local position from symbol
        >>> comp_pos = calculate_position_for_pin(pin_pos, (150, 100))
        >>> # Now add component at comp_pos, and pin 2 will be at (150, 100)

    Note:
        The result is automatically snapped to the KiCAD grid for proper connectivity.
        This function matches the behavior of SchematicSymbol.get_pin_position().
    """
    # Convert inputs to proper types
    if isinstance(pin_local_position, Point):
        pin_x, pin_y = pin_local_position.x, pin_local_position.y
    else:
        pin_x, pin_y = pin_local_position

    if isinstance(desired_pin_position, Point):
        target_x, target_y = desired_pin_position.x, desired_pin_position.y
    else:
        target_x, target_y = desired_pin_position

    logger.debug(
        f"Calculating component position for pin at local ({pin_x}, {pin_y}) "
        f"to reach target ({target_x}, {target_y}) with rotation={rotation}°"
    )

    # Apply the same transformation that get_pin_position() uses
    # This is a standard 2D rotation matrix (NO Y-axis inversion)
    angle_rad = math.radians(rotation)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Calculate rotated offset (same as get_pin_position)
    rotated_x = pin_x * cos_a - pin_y * sin_a
    rotated_y = pin_x * sin_a + pin_y * cos_a

    logger.debug(f"Pin offset after rotation: ({rotated_x:.3f}, {rotated_y:.3f})")

    # Calculate component origin
    # Since: target = component + rotated_offset
    # Therefore: component = target - rotated_offset
    component_x = target_x - rotated_x
    component_y = target_y - rotated_y

    logger.debug(
        f"Calculated component position (before grid snap): ({component_x:.3f}, {component_y:.3f})"
    )

    # Snap to grid for proper KiCAD connectivity
    snapped_x, snapped_y = snap_to_grid((component_x, component_y), grid_size=grid_size)

    logger.debug(f"Final component position (after grid snap): ({snapped_x:.3f}, {snapped_y:.3f})")

    return Point(snapped_x, snapped_y)
