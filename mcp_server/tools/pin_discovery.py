"""
MCP tools for pin discovery and semantic lookup.

Provides MCP-compatible tools that wrap the kicad-sch-api pin discovery
functionality for use by AI assistants.
"""

import logging
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from fastmcp import Context
else:
    try:
        from fastmcp import Context
    except ImportError:
        Context = None  # type: ignore

import kicad_sch_api as ksa
from kicad_sch_api.core.exceptions import LibraryError
from mcp_server.models import ComponentPinsOutput, ErrorOutput, PinInfoOutput, PointModel


logger = logging.getLogger(__name__)


# Global schematic state (simplified for initial implementation)
_current_schematic: Optional[ksa.Schematic] = None


def set_current_schematic(schematic: ksa.Schematic) -> None:
    """Set the current working schematic for MCP tools."""
    global _current_schematic
    _current_schematic = schematic
    logger.info(f"Set current schematic: {schematic}")


def get_current_schematic() -> Optional[ksa.Schematic]:
    """Get the current working schematic."""
    return _current_schematic


async def get_component_pins(
    reference: str,
    ctx: Optional[Context] = None,
) -> ComponentPinsOutput | ErrorOutput:
    """
    Get comprehensive pin information for a component.

    Returns all pins for the specified component with complete metadata including
    positions, electrical types, and pin names. Positions are in absolute schematic
    coordinates accounting for component rotation.

    Args:
        reference: Component reference designator (e.g., "R1", "U2", "IC1")
        ctx: MCP context for progress reporting (optional)

    Returns:
        ComponentPinsOutput with all pin information, or ErrorOutput on failure

    Examples:
        >>> # Get all pins for a resistor
        >>> result = await get_component_pins("R1")
        >>> print(f"Found {result.pin_count} pins")

        >>> # Get pins for an IC
        >>> result = await get_component_pins("U1")
        >>> for pin in result.pins:
        ...     print(f"Pin {pin.number}: {pin.name} @ ({pin.position.x}, {pin.position.y})")
    """
    logger.info(f"[MCP] get_component_pins called for reference: {reference}")

    # Report progress if context available
    if ctx:
        await ctx.report_progress(0, 100, f"Looking up component {reference}")

    # Check if schematic is loaded
    if _current_schematic is None:
        logger.error("[MCP] No schematic loaded")
        return ErrorOutput(
            error="NO_SCHEMATIC_LOADED",
            message="No schematic is currently loaded. Please load or create a schematic first.",
        )

    try:
        if ctx:
            await ctx.report_progress(25, 100, f"Finding pins for {reference}")

        # Get pin information from library
        pins = _current_schematic.components.get_pins_info(reference)

        if pins is None:
            logger.warning(f"[MCP] Component not found: {reference}")
            return ErrorOutput(
                error="COMPONENT_NOT_FOUND",
                message=f"Component '{reference}' not found in schematic",
            )

        if ctx:
            await ctx.report_progress(75, 100, f"Converting {len(pins)} pins to MCP format")

        # Convert to MCP output models
        pin_outputs = []
        for pin in pins:
            pin_output = PinInfoOutput(
                number=pin.number,
                name=pin.name,
                position=PointModel(x=pin.position.x, y=pin.position.y),
                electrical_type=pin.electrical_type.value,
                shape=pin.shape.value,
                length=pin.length,
                orientation=pin.orientation,
                uuid=pin.uuid,
            )
            pin_outputs.append(pin_output)

        # Get component info
        component = _current_schematic.components.get(reference)
        if not component:
            logger.error(f"[MCP] Component lookup failed after pin retrieval: {reference}")
            return ErrorOutput(
                error="INTERNAL_ERROR",
                message=f"Internal error: Component '{reference}' lookup inconsistent",
            )

        result = ComponentPinsOutput(
            reference=component.reference,
            lib_id=component.lib_id,
            pins=pin_outputs,
            pin_count=len(pin_outputs),
            success=True,
        )

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: {len(pins)} pins retrieved")

        logger.info(f"[MCP] Successfully retrieved {len(pins)} pins for {reference}")
        return result

    except LibraryError as e:
        logger.error(f"[MCP] Library error for {reference}: {e}")
        return ErrorOutput(
            error="LIBRARY_ERROR",
            message=f"Symbol library error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"[MCP] Unexpected error for {reference}: {e}", exc_info=True)
        return ErrorOutput(
            error="INTERNAL_ERROR",
            message=f"Unexpected error: {str(e)}",
        )


async def find_pins_by_name(
    reference: str,
    name_pattern: str,
    case_sensitive: bool = False,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Find pin numbers matching a name pattern.

    Supports wildcard patterns (e.g., "CLK*", "*IN*") for semantic pin lookup.
    By default, matching is case-insensitive for maximum flexibility.

    Args:
        reference: Component reference designator (e.g., "R1", "U2")
        name_pattern: Name pattern to search for (e.g., "VCC", "CLK*", "*IN*")
        case_sensitive: If True, matching is case-sensitive (default: False)
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with pin_numbers list and metadata, or error information

    Examples:
        >>> # Find all clock pins
        >>> result = await find_pins_by_name("U1", "CLK*")
        >>> print(f"Clock pins: {result['pin_numbers']}")

        >>> # Find power pins (case-insensitive)
        >>> result = await find_pins_by_name("U1", "vcc")
        >>> print(f"VCC pins: {result['pin_numbers']}")
    """
    logger.info(
        f"[MCP] find_pins_by_name called for {reference} with pattern '{name_pattern}' "
        f"(case_sensitive={case_sensitive})"
    )

    if ctx:
        await ctx.report_progress(0, 100, f"Searching for pins matching '{name_pattern}'")

    # Check if schematic is loaded
    if _current_schematic is None:
        logger.error("[MCP] No schematic loaded")
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    try:
        if ctx:
            await ctx.report_progress(50, 100, f"Searching component {reference}")

        # Find pins by name pattern
        pin_numbers = _current_schematic.components.find_pins_by_name(
            reference, name_pattern, case_sensitive
        )

        if pin_numbers is None:
            logger.warning(f"[MCP] Component not found: {reference}")
            return {
                "success": False,
                "error": "COMPONENT_NOT_FOUND",
                "message": f"Component '{reference}' not found in schematic",
            }

        if ctx:
            await ctx.report_progress(100, 100, f"Found {len(pin_numbers)} matching pins")

        logger.info(
            f"[MCP] Found {len(pin_numbers)} pins matching '{name_pattern}' in {reference}"
        )
        return {
            "success": True,
            "reference": reference,
            "pattern": name_pattern,
            "case_sensitive": case_sensitive,
            "pin_numbers": pin_numbers,
            "count": len(pin_numbers),
        }

    except ValueError as e:
        logger.error(f"[MCP] Validation error: {e}")
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": str(e),
        }
    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error: {str(e)}",
        }


async def find_pins_by_type(
    reference: str,
    pin_type: str,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Find pin numbers by electrical type.

    Returns all pins of a specific electrical type (e.g., all inputs, all power pins).

    Args:
        reference: Component reference designator (e.g., "R1", "U2")
        pin_type: Electrical type filter. Must be one of:
                 "input", "output", "bidirectional", "passive", "power_in",
                 "power_out", "open_collector", "open_emitter", "tri_state",
                 "unspecified", "free", "no_connect"
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with pin_numbers list and metadata, or error information

    Examples:
        >>> # Find all input pins
        >>> result = await find_pins_by_type("U1", "input")
        >>> print(f"Input pins: {result['pin_numbers']}")

        >>> # Find all power input pins
        >>> result = await find_pins_by_type("U1", "power_in")
        >>> print(f"Power pins: {result['pin_numbers']}")
    """
    logger.info(f"[MCP] find_pins_by_type called for {reference} with type '{pin_type}'")

    if ctx:
        await ctx.report_progress(0, 100, f"Searching for {pin_type} pins")

    # Check if schematic is loaded
    if _current_schematic is None:
        logger.error("[MCP] No schematic loaded")
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    try:
        if ctx:
            await ctx.report_progress(50, 100, f"Filtering pins by type {pin_type}")

        # Find pins by type
        pin_numbers = _current_schematic.components.find_pins_by_type(reference, pin_type)

        if pin_numbers is None:
            logger.warning(f"[MCP] Component not found: {reference}")
            return {
                "success": False,
                "error": "COMPONENT_NOT_FOUND",
                "message": f"Component '{reference}' not found in schematic",
            }

        if ctx:
            await ctx.report_progress(100, 100, f"Found {len(pin_numbers)} pins of type {pin_type}")

        logger.info(f"[MCP] Found {len(pin_numbers)} pins of type '{pin_type}' in {reference}")
        return {
            "success": True,
            "reference": reference,
            "pin_type": pin_type,
            "pin_numbers": pin_numbers,
            "count": len(pin_numbers),
        }

    except ValueError as e:
        logger.error(f"[MCP] Validation error: {e}")
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": str(e),
        }
    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error: {str(e)}",
        }
