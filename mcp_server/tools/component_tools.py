"""
MCP tools for component management.

Provides MCP-compatible tools for adding, updating, and managing components
in KiCAD schematics.
"""

import logging
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from fastmcp import Context
else:
    try:
        from fastmcp import Context
    except ImportError:
        Context = None  # type: ignore

import kicad_sch_api as ksa
from kicad_sch_api.core.exceptions import LibraryError, ValidationError
from mcp_server.models import ComponentInfoOutput, ErrorOutput, PointModel


logger = logging.getLogger(__name__)


# Import global schematic state from pin_discovery
from mcp_server.tools.pin_discovery import get_current_schematic


async def add_component(
    lib_id: str,
    value: str,
    reference: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    rotation: float = 0.0,
    footprint: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> ComponentInfoOutput | ErrorOutput:
    """
    Add a component to the current schematic.

    Creates a new component with the specified library ID, value, and optional
    parameters. If no reference is provided, one will be auto-generated based on
    the component type (e.g., R1, C1, U1). If no position is provided, the
    component will be auto-placed.

    Args:
        lib_id: Library identifier (e.g., "Device:R", "Amplifier_Operational:TL072")
        value: Component value or part description (e.g., "10k", "100nF", "TL072")
        reference: Component reference designator (e.g., "R1", "U2") - auto-generated if None
        position: Component position as (x, y) tuple in mm - auto-placed if None
        rotation: Component rotation in degrees (0, 90, 180, or 270), defaults to 0
        footprint: PCB footprint identifier (e.g., "Resistor_SMD:R_0603_1608Metric")
        ctx: MCP context for progress reporting (optional)

    Returns:
        ComponentInfoOutput with component information, or ErrorOutput on failure

    Examples:
        >>> # Add a resistor with auto-generated reference
        >>> result = await add_component(
        ...     lib_id="Device:R",
        ...     value="10k",
        ...     position=(100.0, 100.0)
        ... )
        >>> print(f"Added {result.reference}")

        >>> # Add a capacitor with specific reference and footprint
        >>> result = await add_component(
        ...     lib_id="Device:C",
        ...     value="100nF",
        ...     reference="C1",
        ...     position=(120.0, 100.0),
        ...     footprint="Capacitor_SMD:C_0603_1608Metric"
        ... )
    """
    logger.info(
        f"[MCP] add_component called: lib_id={lib_id}, value={value}, "
        f"reference={reference}, position={position}"
    )

    # Report progress if context available
    if ctx:
        await ctx.report_progress(0, 100, f"Adding component {lib_id}")

    # Check if schematic is loaded
    schematic = get_current_schematic()
    if schematic is None:
        logger.error("[MCP] No schematic loaded")
        return ErrorOutput(
            error="NO_SCHEMATIC_LOADED",
            message="No schematic is currently loaded. Please load or create a schematic first.",
        )

    try:
        if ctx:
            await ctx.report_progress(25, 100, f"Validating component parameters")

        # Validate rotation
        if rotation not in [0.0, 90.0, 180.0, 270.0]:
            logger.warning(f"[MCP] Invalid rotation {rotation}, must be 0, 90, 180, or 270")
            return ErrorOutput(
                error="VALIDATION_ERROR",
                message=f"Rotation must be 0, 90, 180, or 270 degrees, got {rotation}",
            )

        if ctx:
            await ctx.report_progress(50, 100, f"Adding component to schematic")

        # Add component using library API
        component = schematic.components.add(
            lib_id=lib_id,
            reference=reference,
            value=value,
            position=position,
            rotation=rotation,
            footprint=footprint,
        )

        if ctx:
            await ctx.report_progress(75, 100, f"Converting to MCP output format")

        # Convert to MCP output model
        result = ComponentInfoOutput(
            reference=component.reference,
            lib_id=component.lib_id,
            value=component.value,
            position=PointModel(x=component.position.x, y=component.position.y),
            rotation=component.rotation,
            footprint=component.footprint,
            uuid=str(component.uuid),
            success=True,
            message=f"Added component {component.reference}",
        )

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: added {component.reference}")

        logger.info(f"[MCP] Successfully added component {component.reference}")
        return result

    except ValidationError as e:
        logger.error(f"[MCP] Validation error: {e}")
        return ErrorOutput(
            error="VALIDATION_ERROR",
            message=f"Component validation failed: {str(e)}",
        )
    except LibraryError as e:
        logger.error(f"[MCP] Library error: {e}")
        return ErrorOutput(
            error="LIBRARY_ERROR",
            message=f"Symbol library error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return ErrorOutput(
            error="INTERNAL_ERROR",
            message=f"Unexpected error adding component: {str(e)}",
        )
