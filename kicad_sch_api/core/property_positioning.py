"""
Property positioning module for KiCAD-exact component property placement.

This module implements library-specific positioning rules discovered by analyzing
KiCAD's native fields_autoplaced behavior across different component types.

Analysis source: docs/PROPERTY_POSITIONING_ANALYSIS.md
Reference schematics: tests/reference_kicad_projects/property_positioning_*/
"""

import logging
from dataclasses import dataclass
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class PropertyOffset:
    """Offset for a single property at 0° rotation."""

    x: float
    y: float
    rotation: float = 0.0  # Text rotation in degrees


@dataclass
class ComponentPositioningRule:
    """Positioning rules for a component type."""

    reference_offset: PropertyOffset
    value_offset: PropertyOffset
    footprint_offset: Optional[PropertyOffset] = None


# Library-specific positioning rules discovered from KiCAD reference schematics
POSITIONING_RULES = {
    # Resistor: RIGHT side, vertical stacking
    "Device:R": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=2.54, y=-1.2701, rotation=0),
        value_offset=PropertyOffset(x=2.54, y=1.2699, rotation=0),
        footprint_offset=PropertyOffset(x=-1.778, y=0, rotation=90),
    ),
    # Capacitor (unpolarized): RIGHT side, vertical stacking (same pattern as resistor)
    "Device:C": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=3.81, y=-1.2701, rotation=0),
        value_offset=PropertyOffset(x=3.81, y=1.2699, rotation=0),
        footprint_offset=PropertyOffset(x=0.9652, y=3.81, rotation=0),
    ),
    # Capacitor (polarized): Different Y offsets than unpolarized
    "Device:C_Polarized": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=3.81, y=-2.1591, rotation=0),
        value_offset=PropertyOffset(x=3.81, y=0.3809, rotation=0),
        footprint_offset=PropertyOffset(x=0.9652, y=3.81, rotation=0),
    ),
    # Inductor: RIGHT side, vertical stacking (narrower than resistor)
    "Device:L": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=1.27, y=-1.2701, rotation=0),
        value_offset=PropertyOffset(x=1.27, y=1.2699, rotation=0),
        footprint_offset=PropertyOffset(x=0, y=0, rotation=0),
    ),
    # Diode: CENTERED, both properties ABOVE component
    "Device:D": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=0, y=-6.35, rotation=0),
        value_offset=PropertyOffset(x=0, y=-3.81, rotation=0),
        footprint_offset=PropertyOffset(x=0, y=0, rotation=0),
    ),
    # LED: LEFT side, both properties ABOVE component
    "Device:LED": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=-1.5875, y=-6.35, rotation=0),
        value_offset=PropertyOffset(x=-1.5875, y=-3.81, rotation=0),
        footprint_offset=PropertyOffset(x=0, y=0, rotation=0),
    ),
    # BJT Transistor: RIGHT and stacked
    "Transistor_BJT:2N2219": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=5.08, y=-1.2701, rotation=0),
        value_offset=PropertyOffset(x=5.08, y=1.2699, rotation=0),
        footprint_offset=PropertyOffset(x=5.08, y=1.905, rotation=0),
    ),
    # Op-Amp: CENTERED, both properties ABOVE component with larger IC spacing
    "Amplifier_Operational:TL072": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=0, y=-10.16, rotation=0),
        value_offset=PropertyOffset(x=0, y=-7.62, rotation=0),
        footprint_offset=PropertyOffset(x=0, y=0, rotation=0),
    ),
    # Logic IC: SLIGHT RIGHT, both properties ABOVE with very large spacing
    "74xx:74HC595": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=2.1433, y=-17.78, rotation=0),
        value_offset=PropertyOffset(x=2.1433, y=-15.24, rotation=0),
        footprint_offset=PropertyOffset(x=0, y=0, rotation=0),
    ),
    # Connector: SLIGHT RIGHT, both properties ABOVE
    "Connector:Conn_01x04_Pin": ComponentPositioningRule(
        reference_offset=PropertyOffset(x=0.635, y=-7.62, rotation=0),
        value_offset=PropertyOffset(x=0.635, y=-5.08, rotation=0),
        footprint_offset=PropertyOffset(x=0, y=0, rotation=0),
    ),
    # NOTE: Additional component positioning rules are loaded dynamically from
    # KiCAD symbol library files. See _get_offset_from_symbol_library() function.
    # Hard-coded rules above remain for backward compatibility and fallback.
}


def _get_offset_from_symbol_library(lib_id: str, property_name: str) -> Optional[PropertyOffset]:
    """
    Get property offset from symbol library data.

    Attempts to load the symbol from the cache and extract property positions.

    Args:
        lib_id: Component library ID (e.g., "Device:R")
        property_name: Property name ("Reference", "Value", "Footprint")

    Returns:
        PropertyOffset if found in symbol library, None otherwise
    """
    try:
        from ..library.cache import get_symbol_cache

        cache = get_symbol_cache()
        symbol = cache.get_symbol(lib_id)

        if symbol and symbol.property_positions:
            position = symbol.property_positions.get(property_name)
            if position:
                x, y, rotation = position
                logger.debug(
                    f"Using symbol library position for {lib_id}.{property_name}: ({x}, {y}, {rotation})"
                )
                return PropertyOffset(x=x, y=y, rotation=rotation)

        return None

    except Exception as e:
        logger.debug(f"Could not load symbol library data for {lib_id}: {e}")
        return None


def get_property_position(
    lib_id: str,
    property_name: str,
    component_position: Tuple[float, float],
    component_rotation: float = 0,
) -> Tuple[float, float, float]:
    """
    Calculate KiCAD-exact property position for a component.

    Property positions are extracted dynamically from KiCAD symbol library files.
    Hard-coded fallback rules exist only for compatibility with older code paths.

    Args:
        lib_id: Component library ID (e.g., "Device:R")
        property_name: Property name ("Reference", "Value", or "Footprint")
        component_position: Component position (x, y) in mm
        component_rotation: Component rotation in degrees (0, 90, 180, 270)

    Returns:
        Tuple of (x, y, text_rotation) for the property

    Example:
        >>> pos = get_property_position("Device:R", "Reference", (100, 100), 0)
        >>> pos
        (102.54, 98.7299, 0.0)
    """
    # Try to get property position from symbol library
    offset = _get_offset_from_symbol_library(lib_id, property_name)

    if offset is None:
        # Fall back to hard-coded rules (for backward compatibility)
        rule = POSITIONING_RULES.get(lib_id)

        if rule is None:
            logger.warning(f"No positioning rule for {lib_id}, using default resistor pattern")
            rule = POSITIONING_RULES["Device:R"]  # Default fallback

        # Select offset based on property name
        if property_name == "Reference":
            offset = rule.reference_offset
        elif property_name == "Value":
            offset = rule.value_offset
        elif property_name == "Footprint":
            offset = rule.footprint_offset or PropertyOffset(0, 0, 0)
        else:
            logger.warning(f"Unknown property name: {property_name}")
            offset = PropertyOffset(0, 0, 0)

    # Apply rotation transform
    comp_x, comp_y = component_position
    prop_x, prop_y, prop_rotation = _apply_rotation_transform(
        offset.x, offset.y, offset.rotation, comp_x, comp_y, component_rotation
    )

    return (prop_x, prop_y, prop_rotation)


def _apply_rotation_transform(
    offset_x: float,
    offset_y: float,
    text_rotation: float,
    comp_x: float,
    comp_y: float,
    comp_rotation: float,
) -> Tuple[float, float, float]:
    """
    Apply rotation transform to property offset.

    Transforms property offset from 0° reference to actual component rotation.

    Args:
        offset_x: Property X offset at 0° rotation
        offset_y: Property Y offset at 0° rotation
        text_rotation: Text rotation at 0° rotation
        comp_x: Component X position
        comp_y: Component Y position
        comp_rotation: Component rotation (0, 90, 180, 270)

    Returns:
        Tuple of (absolute_x, absolute_y, text_rotation)
    """
    import math

    # Normalize rotation to 0-360
    comp_rotation = comp_rotation % 360

    if comp_rotation == 0:
        # No rotation - direct offset
        return (comp_x + offset_x, comp_y + offset_y, text_rotation)

    elif comp_rotation == 90:
        # 90° rotation: (x, y) → (-y, x)
        rotated_x = -offset_y
        rotated_y = offset_x
        new_text_rotation = (text_rotation + 90) % 360
        return (comp_x + rotated_x, comp_y + rotated_y, new_text_rotation)

    elif comp_rotation == 180:
        # 180° rotation: (x, y) → (-x, -y)
        rotated_x = -offset_x
        rotated_y = -offset_y
        new_text_rotation = (text_rotation + 180) % 360
        return (comp_x + rotated_x, comp_y + rotated_y, new_text_rotation)

    elif comp_rotation == 270:
        # 270° rotation: (x, y) → (y, -x)
        rotated_x = offset_y
        rotated_y = -offset_x
        new_text_rotation = (text_rotation + 270) % 360
        return (comp_x + rotated_x, comp_y + rotated_y, new_text_rotation)

    else:
        # Non-standard rotation - use matrix transform
        angle_rad = math.radians(comp_rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        rotated_x = offset_x * cos_a - offset_y * sin_a
        rotated_y = offset_x * sin_a + offset_y * cos_a
        new_text_rotation = (text_rotation + comp_rotation) % 360

        return (comp_x + rotated_x, comp_y + rotated_y, new_text_rotation)
