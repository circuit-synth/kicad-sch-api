"""
MCP tools for component management.

Provides MCP-compatible tools for adding, updating, listing, filtering, and
removing components in KiCAD schematics.
"""

import logging
from typing import TYPE_CHECKING, List, Optional, Tuple, Dict, Any

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


def _component_to_output(component: Any) -> ComponentInfoOutput:
    """Convert a Component to ComponentInfoOutput."""
    return ComponentInfoOutput(
        reference=component.reference,
        lib_id=component.lib_id,
        value=component.value,
        position=PointModel(x=component.position.x, y=component.position.y),
        rotation=component.rotation,
        footprint=component.footprint,
        uuid=str(component.uuid),
        success=True,
    )


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
        result = _component_to_output(component)
        result.message = f"Added component {component.reference}"

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


async def list_components(
    ctx: Optional[Context] = None,
) -> dict:
    """
    List all components in the current schematic.

    Returns all components with their complete metadata including position,
    rotation, footprint, and properties.

    Args:
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and list of components, or error information

    Examples:
        >>> result = await list_components()
        >>> print(f"Found {result['count']} components")
        >>> for comp in result['components']:
        ...     print(f"{comp['reference']}: {comp['value']}")
    """
    logger.info("[MCP] list_components called")

    if ctx:
        await ctx.report_progress(0, 100, "Listing all components")

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
            await ctx.report_progress(50, 100, "Retrieving components")

        # Get all components (iterate directly)
        components = list(schematic.components)

        if ctx:
            await ctx.report_progress(75, 100, f"Converting {len(components)} components")

        # Convert to output format
        component_list = []
        for comp in components:
            comp_output = _component_to_output(comp)
            component_list.append(comp_output.model_dump())

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: {len(components)} components")

        logger.info(f"[MCP] Listed {len(components)} components")
        return {
            "success": True,
            "count": len(components),
            "components": component_list,
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error listing components: {str(e)}",
        }


async def update_component(
    reference: str,
    value: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    rotation: Optional[float] = None,
    footprint: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> ComponentInfoOutput | ErrorOutput:
    """
    Update component properties.

    Updates one or more properties of an existing component. Only provided
    parameters will be updated.

    Args:
        reference: Component reference designator to update (e.g., "R1")
        value: New component value (if provided)
        position: New position as (x, y) tuple in mm (if provided)
        rotation: New rotation in degrees (0, 90, 180, or 270) (if provided)
        footprint: New footprint identifier (if provided)
        ctx: MCP context for progress reporting (optional)

    Returns:
        ComponentInfoOutput with updated component information, or ErrorOutput on failure

    Examples:
        >>> # Update value only
        >>> result = await update_component("R1", value="20k")

        >>> # Update multiple properties
        >>> result = await update_component(
        ...     "R1",
        ...     value="20k",
        ...     footprint="Resistor_SMD:R_0805_2012Metric",
        ...     rotation=90.0
        ... )
    """
    logger.info(f"[MCP] update_component called for {reference}")

    if ctx:
        await ctx.report_progress(0, 100, f"Updating component {reference}")

    # Check if schematic is loaded
    schematic = get_current_schematic()
    if schematic is None:
        logger.error("[MCP] No schematic loaded")
        return ErrorOutput(
            error="NO_SCHEMATIC_LOADED",
            message="No schematic is currently loaded",
        )

    try:
        if ctx:
            await ctx.report_progress(25, 100, f"Finding component {reference}")

        # Get component
        component = schematic.components.get(reference)
        if component is None:
            logger.warning(f"[MCP] Component not found: {reference}")
            return ErrorOutput(
                error="COMPONENT_NOT_FOUND",
                message=f"Component '{reference}' not found in schematic",
            )

        if ctx:
            await ctx.report_progress(50, 100, f"Validating updates")

        # Validate rotation if provided
        if rotation is not None and rotation not in [0.0, 90.0, 180.0, 270.0]:
            logger.warning(f"[MCP] Invalid rotation {rotation}")
            return ErrorOutput(
                error="VALIDATION_ERROR",
                message=f"Rotation must be 0, 90, 180, or 270 degrees, got {rotation}",
            )

        if ctx:
            await ctx.report_progress(75, 100, f"Applying updates")

        # Update provided properties
        if value is not None:
            component.value = value
        if position is not None:
            component.position = position
        if rotation is not None:
            component.rotation = rotation
        if footprint is not None:
            component.footprint = footprint

        # Convert to output
        result = _component_to_output(component)
        result.message = f"Updated component {reference}"

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: updated {reference}")

        logger.info(f"[MCP] Successfully updated component {reference}")
        return result

    except ValidationError as e:
        logger.error(f"[MCP] Validation error: {e}")
        return ErrorOutput(
            error="VALIDATION_ERROR",
            message=f"Update validation failed: {str(e)}",
        )
    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return ErrorOutput(
            error="INTERNAL_ERROR",
            message=f"Unexpected error updating component: {str(e)}",
        )


async def remove_component(
    reference: str,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Remove a component from the schematic.

    Removes the component with the specified reference designator. This also
    removes all associated wires and connections.

    Args:
        reference: Component reference designator to remove (e.g., "R1")
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status

    Examples:
        >>> result = await remove_component("R1")
        >>> if result['success']:
        ...     print(f"Removed component {result['reference']}")
    """
    logger.info(f"[MCP] remove_component called for {reference}")

    if ctx:
        await ctx.report_progress(0, 100, f"Removing component {reference}")

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
            await ctx.report_progress(50, 100, f"Removing {reference}")

        # Remove component
        removed = schematic.components.remove(reference)

        if not removed:
            logger.warning(f"[MCP] Component not found: {reference}")
            return {
                "success": False,
                "error": "COMPONENT_NOT_FOUND",
                "message": f"Component '{reference}' not found in schematic",
            }

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: removed {reference}")

        logger.info(f"[MCP] Successfully removed component {reference}")
        return {
            "success": True,
            "reference": reference,
            "message": f"Removed component {reference}",
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error removing component: {str(e)}",
        }


async def filter_components(
    lib_id: Optional[str] = None,
    value: Optional[str] = None,
    value_pattern: Optional[str] = None,
    footprint: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Filter components by various criteria.

    Returns components matching the specified filter criteria. All provided
    criteria must match (AND logic).

    Args:
        lib_id: Filter by library ID (exact match, e.g., "Device:R")
        value: Filter by value (exact match, e.g., "10k")
        value_pattern: Filter by value pattern (substring match, e.g., "10")
        footprint: Filter by footprint (exact match)
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and list of matching components

    Examples:
        >>> # Find all resistors
        >>> result = await filter_components(lib_id="Device:R")
        >>> print(f"Found {result['count']} resistors")

        >>> # Find all 10k resistors
        >>> result = await filter_components(lib_id="Device:R", value="10k")

        >>> # Find all components with "100" in value
        >>> result = await filter_components(value_pattern="100")
    """
    logger.info(f"[MCP] filter_components called with criteria: "
                f"lib_id={lib_id}, value={value}, value_pattern={value_pattern}")

    if ctx:
        await ctx.report_progress(0, 100, "Filtering components")

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
            await ctx.report_progress(50, 100, "Applying filters")

        # Build filter criteria
        criteria = {}
        if lib_id is not None:
            criteria["lib_id"] = lib_id
        if value is not None:
            criteria["value"] = value
        if value_pattern is not None:
            criteria["value_pattern"] = value_pattern
        if footprint is not None:
            criteria["footprint"] = footprint

        # Apply filter
        components = schematic.components.filter(**criteria)

        if ctx:
            await ctx.report_progress(75, 100, f"Converting {len(components)} components")

        # Convert to output format
        component_list = []
        for comp in components:
            comp_output = _component_to_output(comp)
            component_list.append(comp_output.model_dump())

        if ctx:
            await ctx.report_progress(100, 100, f"Complete: {len(components)} matches")

        logger.info(f"[MCP] Found {len(components)} matching components")
        return {
            "success": True,
            "count": len(components),
            "components": component_list,
            "criteria": criteria,
        }

    except Exception as e:
        logger.error(f"[MCP] Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Unexpected error filtering components: {str(e)}",
        }
