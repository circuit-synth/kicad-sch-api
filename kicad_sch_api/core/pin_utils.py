"""
Pin positioning utilities for KiCAD schematic manipulation.

Provides accurate pin position calculation with component transformations,
migrated and improved from circuit-synth.
"""

import logging
from typing import List, Optional, Tuple

from ..library.cache import get_symbol_cache
from .geometry import apply_transformation
from .types import Point, SchematicSymbol

logger = logging.getLogger(__name__)


def get_component_pin_position(component: SchematicSymbol, pin_number: str) -> Optional[Point]:
    """
    Get the absolute position of a component pin.

    Migrated from circuit-synth with enhanced logging for verification.

    Args:
        component: Component containing the pin
        pin_number: Pin number to find

    Returns:
        Absolute position of the pin, or None if not found
    """
    logger.info(f"Getting position for {component.reference} pin {pin_number}")
    logger.info(f"  Component position: ({component.position.x}, {component.position.y})")
    logger.info(f"  Component rotation: {getattr(component, 'rotation', 0)}°")
    logger.info(f"  Component mirror: {getattr(component, 'mirror', None)}")

    # First check if pin is already in component data
    for pin in component.pins:
        if pin.number == pin_number:
            logger.info(f"  Found pin {pin_number} in component data")
            logger.info(f"  Pin relative position: ({pin.position.x}, {pin.position.y})")

            # Apply component transformations
            absolute_pos = apply_transformation(
                (pin.position.x, pin.position.y),
                component.position,
                getattr(component, "rotation", 0),
                getattr(component, "mirror", None),
            )

            result = Point(absolute_pos[0], absolute_pos[1])
            logger.info(f"  Final absolute position: ({result.x}, {result.y})")
            return result

    # If not in component data, try to get from symbol library
    logger.info(f"  Pin {pin_number} not in component data, checking symbol library")

    try:
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(component.lib_id)

        if not symbol_def:
            logger.warning(f"  Symbol definition not found for {component.lib_id}")
            return None

        logger.info(f"  Found symbol definition for {component.lib_id}")

        # Look for pin in symbol definition
        pins_found = []
        for pin_def in symbol_def.pins:
            pins_found.append(pin_def.number)
            if pin_def.number == pin_number:
                logger.info(f"  Found pin {pin_number} in symbol definition")

                # Get pin position from definition
                pin_x = pin_def.position.x
                pin_y = pin_def.position.y
                logger.info(f"  Symbol pin position: ({pin_x}, {pin_y})")

                # Apply component transformations
                absolute_pos = apply_transformation(
                    (pin_x, pin_y),
                    component.position,
                    getattr(component, "rotation", 0),
                    getattr(component, "mirror", None),
                )

                result = Point(absolute_pos[0], absolute_pos[1])
                logger.info(f"  Final absolute position: ({result.x}, {result.y})")
                return result

        logger.warning(f"  Pin {pin_number} not found in symbol. Available pins: {pins_found}")

    except Exception as e:
        logger.error(f"  Error accessing symbol cache: {e}")

    return None


def get_component_pin_info(
    component: SchematicSymbol, pin_number: str
) -> Optional[Tuple[Point, float]]:
    """
    Get the absolute position and rotation of a component pin.

    Args:
        component: Component containing the pin
        pin_number: Pin number to find

    Returns:
        Tuple of (absolute_position, absolute_rotation_degrees), or None if not found
    """
    logger.info(f"Getting pin info for {component.reference} pin {pin_number}")
    logger.info(f"  Component position: ({component.position.x}, {component.position.y})")
    component_rotation = getattr(component, "rotation", 0)
    logger.info(f"  Component rotation: {component_rotation}°")
    logger.info(f"  Component mirror: {getattr(component, 'mirror', None)}")

    # First check if pin is already in component data
    for pin in component.pins:
        if pin.number == pin_number:
            logger.info(f"  Found pin {pin_number} in component data")
            logger.info(f"  Pin relative position: ({pin.position.x}, {pin.position.y})")
            logger.info(f"  Pin rotation: {pin.rotation}°")

            # Apply component transformations to position
            absolute_pos = apply_transformation(
                (pin.position.x, pin.position.y),
                component.position,
                component_rotation,
                getattr(component, "mirror", None),
            )

            # Calculate absolute rotation (pin rotation + component rotation)
            absolute_rotation = (pin.rotation + component_rotation) % 360

            result_pos = Point(absolute_pos[0], absolute_pos[1])
            logger.info(
                f"  Final absolute position: ({result_pos.x}, {result_pos.y}), rotation: {absolute_rotation}°"
            )
            return (result_pos, absolute_rotation)

    # If not in component data, try to get from symbol library
    logger.info(f"  Pin {pin_number} not in component data, checking symbol library")

    try:
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(component.lib_id)

        if not symbol_def:
            logger.warning(f"  Symbol definition not found for {component.lib_id}")
            return None

        logger.info(f"  Found symbol definition for {component.lib_id}")

        # Look for pin in symbol definition
        pins_found = []
        for pin_def in symbol_def.pins:
            pins_found.append(pin_def.number)
            if pin_def.number == pin_number:
                logger.info(f"  Found pin {pin_number} in symbol definition")

                # Get pin position and rotation from definition
                pin_x = pin_def.position.x
                pin_y = pin_def.position.y
                pin_rotation = pin_def.rotation
                logger.info(f"  Symbol pin position: ({pin_x}, {pin_y}), rotation: {pin_rotation}°")

                # Apply component transformations to position
                absolute_pos = apply_transformation(
                    (pin_x, pin_y),
                    component.position,
                    component_rotation,
                    getattr(component, "mirror", None),
                )

                # Calculate absolute rotation
                absolute_rotation = (pin_rotation + component_rotation) % 360

                result_pos = Point(absolute_pos[0], absolute_pos[1])
                logger.info(
                    f"  Final absolute position: ({result_pos.x}, {result_pos.y}), rotation: {absolute_rotation}°"
                )
                return (result_pos, absolute_rotation)

        logger.warning(f"  Pin {pin_number} not found in symbol. Available pins: {pins_found}")

    except Exception as e:
        logger.error(f"  Error accessing symbol cache: {e}")

    return None


def list_component_pins(component: SchematicSymbol) -> List[Tuple[str, Point]]:
    """
    List all pins for a component with their absolute positions.

    Args:
        component: Component to analyze

    Returns:
        List of (pin_number, absolute_position) tuples
    """
    logger.info(f"Listing pins for component {component.reference}")

    pins = []

    # Check component data first
    for pin in component.pins:
        absolute_pos = apply_transformation(
            (pin.position.x, pin.position.y),
            component.position,
            getattr(component, "rotation", 0),
            getattr(component, "mirror", None),
        )
        pins.append((pin.number, Point(absolute_pos[0], absolute_pos[1])))

    # If no pins in component data, try symbol library
    if not pins:
        try:
            symbol_cache = get_symbol_cache()
            symbol_def = symbol_cache.get_symbol(component.lib_id)

            if symbol_def:
                for pin_def in symbol_def.pins:
                    pin_number = pin_def.number
                    pin_x = pin_def.position.x
                    pin_y = pin_def.position.y

                    absolute_pos = apply_transformation(
                        (pin_x, pin_y),
                        component.position,
                        getattr(component, "rotation", 0),
                        getattr(component, "mirror", None),
                    )
                    pins.append((pin_number, Point(absolute_pos[0], absolute_pos[1])))
        except Exception as e:
            logger.error(f"Error getting pins from symbol library: {e}")

    logger.info(f"Found {len(pins)} pins for {component.reference}")
    for pin_num, pos in pins:
        logger.info(f"  Pin {pin_num}: ({pos.x}, {pos.y})")

    return pins
