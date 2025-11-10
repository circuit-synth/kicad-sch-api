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
from kicad_sch_api.geometry import create_orthogonal_routing, CornerDirection
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


async def connect_components(
    from_component: str,
    from_pin: str,
    to_component: str,
    to_pin: str,
    corner_direction: str = "auto",
    add_label: Optional[str] = None,
    add_junction: bool = True,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Connect two component pins with automatic orthogonal routing.

    Uses Manhattan-style (orthogonal) routing to create L-shaped or direct wire
    paths between component pins. Automatically calculates pin positions and
    generates appropriate wire segments with optional junctions and labels.

    Args:
        from_component: Source component reference (e.g., "R1")
        from_pin: Source pin number (e.g., "2")
        to_component: Destination component reference (e.g., "R2")
        to_pin: Destination pin number (e.g., "1")
        corner_direction: Routing direction preference:
            - "auto": Smart heuristic (horizontal if dx >= dy, else vertical)
            - "horizontal_first": Route horizontally then vertically
            - "vertical_first": Route vertically then horizontally
        add_label: Optional net label text to add at start of routing
        add_junction: Whether to add junction at L-shaped corners (default: True)
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and connection information including:
        - from/to component and pin details with positions
        - routing type (direct or L-shaped)
        - segments list with start/end positions
        - wire_uuids list
        - junction_uuid (if junction was added)
        - label_uuid (if label was added)

    Examples:
        >>> # Simple connection with auto routing
        >>> result = await connect_components("R1", "2", "R2", "1")

        >>> # With label and horizontal-first routing
        >>> result = await connect_components(
        ...     "R1", "2", "R2", "1",
        ...     corner_direction="horizontal_first",
        ...     add_label="VCC"
        ... )

        >>> # Vertical-first without junction
        >>> result = await connect_components(
        ...     "R1", "1", "C1", "1",
        ...     corner_direction="vertical_first",
        ...     add_junction=False
        ... )
    """
    logger.info(
        f"[MCP] connect_components called: {from_component}:{from_pin} -> "
        f"{to_component}:{to_pin}, direction={corner_direction}"
    )

    if ctx:
        await ctx.report_progress(0, 100, "Connecting components")

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
            await ctx.report_progress(10, 100, "Looking up components")

        # Get components
        try:
            from_comp = schematic.components.get(from_component)
            to_comp = schematic.components.get(to_component)
        except KeyError as e:
            logger.error(f"[MCP] Component not found: {e}")
            return {
                "success": False,
                "error": "COMPONENT_NOT_FOUND",
                "message": f"Component not found: {str(e)}",
            }

        if ctx:
            await ctx.report_progress(30, 100, "Getting pin positions")

        # Get pin positions
        from_pins = schematic.components.get_pins_info(from_component)
        to_pins = schematic.components.get_pins_info(to_component)

        # Check if pin info was successfully retrieved
        if from_pins is None:
            logger.error(f"[MCP] Could not get pins for {from_component}")
            return {
                "success": False,
                "error": "PIN_INFO_ERROR",
                "message": f"Could not get pin information for component {from_component}",
            }

        if to_pins is None:
            logger.error(f"[MCP] Could not get pins for {to_component}")
            return {
                "success": False,
                "error": "PIN_INFO_ERROR",
                "message": f"Could not get pin information for component {to_component}",
            }

        from_pin_obj = next((p for p in from_pins if p.number == from_pin), None)
        to_pin_obj = next((p for p in to_pins if p.number == to_pin), None)

        if not from_pin_obj:
            logger.error(f"[MCP] Pin {from_pin} not found on {from_component}")
            return {
                "success": False,
                "error": "PIN_NOT_FOUND",
                "message": f"Pin {from_pin} not found on component {from_component}",
            }

        if not to_pin_obj:
            logger.error(f"[MCP] Pin {to_pin} not found on {to_component}")
            return {
                "success": False,
                "error": "PIN_NOT_FOUND",
                "message": f"Pin {to_pin} not found on component {to_component}",
            }

        if ctx:
            await ctx.report_progress(50, 100, "Calculating routing")

        # Parse corner direction
        try:
            if corner_direction.upper() == "AUTO":
                direction = CornerDirection.AUTO
            elif corner_direction.upper() == "HORIZONTAL_FIRST":
                direction = CornerDirection.HORIZONTAL_FIRST
            elif corner_direction.upper() == "VERTICAL_FIRST":
                direction = CornerDirection.VERTICAL_FIRST
            else:
                logger.warning(f"[MCP] Invalid corner direction: {corner_direction}, using AUTO")
                direction = CornerDirection.AUTO
        except Exception:
            logger.warning(f"[MCP] Error parsing corner direction, using AUTO")
            direction = CornerDirection.AUTO

        # Create orthogonal routing
        routing_result = create_orthogonal_routing(
            from_pin_obj.position, to_pin_obj.position, corner_direction=direction
        )

        logger.info(
            f"[MCP] Routing calculated: {len(routing_result.segments)} segments, "
            f"direct={routing_result.is_direct}, corner={routing_result.corner}"
        )

        if ctx:
            await ctx.report_progress(70, 100, "Adding wires")

        # Add wire segments
        wire_uuids = []
        for start, end in routing_result.segments:
            wire_uuid = schematic.wires.add(start=start, end=end)
            wire_uuids.append(wire_uuid)

        # Add junction at corner if requested and routing is L-shaped
        junction_uuid = None
        if add_junction and routing_result.corner and not routing_result.is_direct:
            if ctx:
                await ctx.report_progress(80, 100, "Adding junction at corner")

            junction_uuid = schematic.junctions.add(
                position=(routing_result.corner.x, routing_result.corner.y)
            )
            logger.info(f"[MCP] Added junction at corner: {junction_uuid}")

        # Add label if requested
        label_uuid = None
        if add_label:
            if ctx:
                await ctx.report_progress(90, 100, f"Adding label {add_label}")

            label = schematic.labels.add(
                text=add_label,
                position=(from_pin_obj.position.x, from_pin_obj.position.y),
            )
            label_uuid = str(label.uuid)
            logger.info(f"[MCP] Added label '{add_label}': {label_uuid}")

        if ctx:
            await ctx.report_progress(100, 100, "Complete: components connected")

        logger.info(
            f"[MCP] Successfully connected {from_component}:{from_pin} to "
            f"{to_component}:{to_pin} with {len(wire_uuids)} wires"
        )

        return {
            "success": True,
            "from": {
                "component": from_component,
                "pin": from_pin,
                "position": {"x": from_pin_obj.position.x, "y": from_pin_obj.position.y},
            },
            "to": {
                "component": to_component,
                "pin": to_pin,
                "position": {"x": to_pin_obj.position.x, "y": to_pin_obj.position.y},
            },
            "routing": {
                "type": "direct" if routing_result.is_direct else "l_shaped",
                "segments": len(routing_result.segments),
                "corner": (
                    {"x": routing_result.corner.x, "y": routing_result.corner.y}
                    if routing_result.corner
                    else None
                ),
            },
            "segments": [
                {"start": {"x": s.x, "y": s.y}, "end": {"x": e.x, "y": e.y}}
                for s, e in routing_result.segments
            ],
            "wire_uuids": wire_uuids,
            "junction_uuid": junction_uuid,
            "label_uuid": label_uuid,
            "message": f"Connected {from_component}:{from_pin} to {to_component}:{to_pin} "
            f"with {len(wire_uuids)} wire segment(s)",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error connecting components: {str(e)}",
        }


async def add_bus_wire(
    start: Tuple[float, float],
    end: Tuple[float, float],
    ctx: Optional[Context] = None,
) -> dict:
    """
    Add a bus wire between two points.

    Bus wires represent multi-bit signal connections (e.g., data buses, address buses).
    They are visually thicker than regular wires and use different styling in KiCAD.

    Args:
        start: Start point as (x, y) tuple in mm
        end: End point as (x, y) tuple in mm
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and bus wire information

    Examples:
        >>> # Create 8-bit data bus
        >>> result = await add_bus_wire(
        ...     start=(50.0, 50.0),
        ...     end=(100.0, 50.0)
        ... )
    """
    logger.info(f"[MCP] add_bus_wire called: start={start}, end={end}")

    if ctx:
        await ctx.report_progress(0, 100, "Adding bus wire")

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
            await ctx.report_progress(50, 100, "Creating bus wire connection")

        # Add bus wire using library API
        wire_uuid = schematic.wires.add(
            start=start,
            end=end,
            wire_type=WireType.BUS,  # This makes it a bus wire
        )

        if ctx:
            await ctx.report_progress(100, 100, "Complete: bus wire added")

        logger.info(f"[MCP] Successfully added bus wire {wire_uuid}")
        return {
            "success": True,
            "uuid": wire_uuid,
            "start": {"x": start[0], "y": start[1]},
            "end": {"x": end[0], "y": end[1]},
            "message": f"Added bus wire from ({start[0]}, {start[1]}) to ({end[0]}, {end[1]})",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error adding bus wire: {str(e)}",
        }


async def add_bus_entry(
    position: Tuple[float, float],
    rotation: int = 0,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Add a bus entry to the schematic.

    Bus entries connect individual wires to bus wires. They are typically placed
    at a 45-degree angle and show where a single signal branches off from a
    multi-bit bus.

    Args:
        position: Entry point as (x, y) tuple in mm
        rotation: Rotation angle in degrees (0, 90, 180, 270), defaults to 0
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and bus entry information

    Examples:
        >>> # Add bus entry at position with 270 degree rotation
        >>> result = await add_bus_entry(
        ...     position=(60.0, 50.0),
        ...     rotation=270
        ... )
    """
    logger.info(f"[MCP] add_bus_entry called: position={position}, rotation={rotation}")

    if ctx:
        await ctx.report_progress(0, 100, "Adding bus entry")

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
            await ctx.report_progress(25, 100, "Validating bus entry parameters")

        # Validate rotation (must be 0, 90, 180, or 270)
        if rotation not in [0, 90, 180, 270]:
            logger.warning(f"[MCP] Invalid rotation {rotation}")
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": f"Rotation must be 0, 90, 180, or 270 degrees, got {rotation}",
            }

        if ctx:
            await ctx.report_progress(50, 100, "Creating bus entry")

        # Add bus entry using library API
        entry_uuid = schematic.bus_entries.add(
            position=position,
            rotation=rotation,
        )

        if ctx:
            await ctx.report_progress(100, 100, "Complete: bus entry added")

        logger.info(f"[MCP] Successfully added bus entry {entry_uuid}")
        return {
            "success": True,
            "uuid": entry_uuid,
            "position": {"x": position[0], "y": position[1]},
            "rotation": rotation,
            "message": f"Added bus entry at ({position[0]}, {position[1]}) with rotation {rotation}",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error adding bus entry: {str(e)}",
        }


async def add_bus_label(
    text: str,
    position: Tuple[float, float],
    rotation: float = 0.0,
    size: float = 1.27,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Add a bus label to the schematic.

    Bus labels identify multi-bit signals using range notation.
    Examples: "DATA[0..7]", "ADDR[0..15]", "RGB[R,G,B]"

    Args:
        text: Label text with bus notation (e.g., "DATA[0..7]")
        position: Label position as (x, y) tuple in mm
        rotation: Label rotation in degrees (0, 90, 180, 270), defaults to 0
        size: Text size in mm, defaults to 1.27 (KiCAD standard)
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and bus label information

    Examples:
        >>> # Add 8-bit data bus label
        >>> result = await add_bus_label(
        ...     text="DATA[0..7]",
        ...     position=(75.0, 48.0)
        ... )

        >>> # Add RGB bus label
        >>> result = await add_bus_label(
        ...     text="RGB[R,G,B]",
        ...     position=(100.0, 50.0)
        ... )
    """
    logger.info(f"[MCP] add_bus_label called: text={text}, position={position}")

    if ctx:
        await ctx.report_progress(0, 100, f"Adding bus label {text}")

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
            await ctx.report_progress(25, 100, "Validating bus label parameters")

        # Validate bus notation (must contain [...])
        import re

        if not re.search(r"\[.+\]", text):
            logger.warning(f"[MCP] Invalid bus notation: {text}")
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": f"Bus label must contain range notation [...], got: {text}",
            }

        # Validate rotation (KiCAD supports 0, 90, 180, 270)
        if rotation not in [0.0, 90.0, 180.0, 270.0]:
            logger.warning(f"[MCP] Invalid rotation {rotation}")
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": f"Rotation must be 0, 90, 180, or 270 degrees, got {rotation}",
            }

        if ctx:
            await ctx.report_progress(50, 100, "Creating bus label")

        # Add bus label using library API (same as regular label)
        label = schematic.labels.add(
            text=text,
            position=position,
            rotation=rotation,
            size=size,
        )

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: bus label {text} added")

        logger.info(f"[MCP] Successfully added bus label {text}")
        return {
            "success": True,
            "uuid": str(label.uuid),
            "text": text,
            "position": {"x": position[0], "y": position[1]},
            "rotation": rotation,
            "size": size,
            "message": f"Added bus label '{text}' at ({position[0]}, {position[1]})",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error adding bus label: {str(e)}",
        }
