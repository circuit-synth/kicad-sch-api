"""
MCP tools for schematic connectivity.

Provides MCP-compatible tools for adding wires, labels, junctions, and managing
circuit connections in KiCAD schematics.
"""

import logging
from typing import TYPE_CHECKING, Optional, Tuple, List

if TYPE_CHECKING:
    from fastmcp import Context
else:
    try:
        from fastmcp import Context
    except ImportError:
        Context = None  # type: ignore

import kicad_sch_api as ksa
from kicad_sch_api.core.types import WireType
from mcp_server.models import PointModel


logger = logging.getLogger(__name__)


# Import global schematic state from pin_discovery
from mcp_server.tools.pin_discovery import get_current_schematic


async def add_wire(
    start: Tuple[float, float],
    end: Tuple[float, float],
    ctx: Optional[Context] = None,
) -> dict:
    """
    Add a wire between two points.

    Creates a wire connection between start and end points. Wires are used to
    connect component pins and establish electrical nets.

    Args:
        start: Start point as (x, y) tuple in mm
        end: End point as (x, y) tuple in mm
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and wire information

    Examples:
        >>> # Connect two points horizontally
        >>> result = await add_wire(
        ...     start=(100.0, 100.0),
        ...     end=(150.0, 100.0)
        ... )

        >>> # Vertical wire
        >>> result = await add_wire(
        ...     start=(100.0, 100.0),
        ...     end=(100.0, 150.0)
        ... )
    """
    logger.info(f"[MCP] add_wire called: start={start}, end={end}")

    if ctx:
        await ctx.report_progress(0, 100, "Adding wire")

    # Check if schematic is loaded
    schematic = get_current_schematic()
    if schematic is None:
        logger.error("[MCP] No schematic loaded")
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    try:
        if ctx:
            await ctx.report_progress(50, 100, "Creating wire connection")

        # Add wire using library API
        wire_uuid = schematic.wires.add(
            start=start,
            end=end,
            wire_type=WireType.WIRE,
        )

        if ctx:
            await ctx.report_progress(100, 100, "Complete: wire added")

        logger.info(f"[MCP] Successfully added wire {wire_uuid}")
        return {
            "success": True,
            "uuid": wire_uuid,
            "start": {"x": start[0], "y": start[1]},
            "end": {"x": end[0], "y": end[1]},
            "message": f"Added wire from ({start[0]}, {start[1]}) to ({end[0]}, {end[1]})",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error adding wire: {str(e)}",
        }


async def add_label(
    text: str,
    position: Tuple[float, float],
    rotation: float = 0.0,
    size: float = 1.27,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Add a net label to the schematic.

    Net labels are used to name electrical nets and establish connections
    between non-physically connected wires with the same label name.

    Args:
        text: Label text (net name)
        position: Label position as (x, y) tuple in mm
        rotation: Label rotation in degrees (0, 90, 180, 270), defaults to 0
        size: Text size in mm, defaults to 1.27 (KiCAD standard)
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and label information

    Examples:
        >>> # Add VCC label
        >>> result = await add_label(
        ...     text="VCC",
        ...     position=(100.0, 100.0)
        ... )

        >>> # Add label with rotation
        >>> result = await add_label(
        ...     text="GND",
        ...     position=(150.0, 100.0),
        ...     rotation=90.0
        ... )
    """
    logger.info(f"[MCP] add_label called: text={text}, position={position}")

    if ctx:
        await ctx.report_progress(0, 100, f"Adding label {text}")

    # Check if schematic is loaded
    schematic = get_current_schematic()
    if schematic is None:
        logger.error("[MCP] No schematic loaded")
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    try:
        if ctx:
            await ctx.report_progress(25, 100, "Validating label parameters")

        # Validate rotation (KiCAD supports 0, 90, 180, 270)
        if rotation not in [0.0, 90.0, 180.0, 270.0]:
            logger.warning(f"[MCP] Invalid rotation {rotation}")
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": f"Rotation must be 0, 90, 180, or 270 degrees, got {rotation}",
            }

        if ctx:
            await ctx.report_progress(50, 100, "Creating label")

        # Add label using library API
        label = schematic.labels.add(
            text=text,
            position=position,
            rotation=rotation,
            size=size,
        )

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: label {text} added")

        logger.info(f"[MCP] Successfully added label {text}")
        return {
            "success": True,
            "uuid": str(label.uuid),
            "text": text,
            "position": {"x": position[0], "y": position[1]},
            "rotation": rotation,
            "size": size,
            "message": f"Added label '{text}' at ({position[0]}, {position[1]})",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error adding label: {str(e)}",
        }


async def add_junction(
    position: Tuple[float, float],
    diameter: float = 0.0,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Add a wire junction at the specified position.

    Junctions indicate T-connections where three or more wires meet. They are
    required in KiCAD when a wire branches into multiple paths.

    Args:
        position: Junction position as (x, y) tuple in mm
        diameter: Junction diameter in mm (0 = use KiCAD default)
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and junction information

    Examples:
        >>> # Add junction at T-connection
        >>> result = await add_junction(
        ...     position=(100.0, 100.0)
        ... )

        >>> # Add junction with custom diameter
        >>> result = await add_junction(
        ...     position=(150.0, 100.0),
        ...     diameter=0.8
        ... )
    """
    logger.info(f"[MCP] add_junction called: position={position}")

    if ctx:
        await ctx.report_progress(0, 100, "Adding junction")

    # Check if schematic is loaded
    schematic = get_current_schematic()
    if schematic is None:
        logger.error("[MCP] No schematic loaded")
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    try:
        if ctx:
            await ctx.report_progress(50, 100, "Creating junction")

        # Add junction using library API
        junction_uuid = schematic.junctions.add(
            position=position,
            diameter=diameter,
        )

        if ctx:
            await ctx.report_progress(100, 100, "Complete: junction added")

        logger.info(f"[MCP] Successfully added junction {junction_uuid}")
        return {
            "success": True,
            "uuid": junction_uuid,
            "position": {"x": position[0], "y": position[1]},
            "diameter": diameter,
            "message": f"Added junction at ({position[0]}, {position[1]})",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error adding junction: {str(e)}",
        }
