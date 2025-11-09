"""
Consolidated MCP tools for KiCAD schematic management.

This module provides 8 consolidated MCP tools that handle all CRUD operations
for schematic entities (schematics, components, wires, labels, text boxes,
power symbols, hierarchical sheets, and global labels).

Each tool uses an `action` parameter to specify the operation (create, read,
update, delete) and returns a standardized response dictionary.

Design: 8 tools × multiple actions = complete schematic management coverage
Benefit: Minimal tool count for optimal LLM performance
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from fastmcp import Context
else:
    try:
        from fastmcp import Context
    except ImportError:
        Context = None  # type: ignore

import kicad_sch_api as ksa

logger = logging.getLogger(__name__)

# Import global schematic state
from mcp_server.tools.pin_discovery import get_current_schematic, set_current_schematic

# ============================================================================
# 1. MANAGE SCHEMATIC (create, read, save, load)
# ============================================================================


async def manage_schematic(
    action: str,
    name: Optional[str] = None,
    file_path: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage schematic project (create, read, save, load).

    Args:
        action: Operation to perform ("create", "read", "save", "load")
        name: Project name (required for "create")
        file_path: File path (required for "load"/"save", optional for others)
        ctx: MCP context for progress reporting (optional)

    Returns:
        Dictionary with success status and operation results
    """
    logger.info(f"[MCP] manage_schematic called: action={action}")

    if action == "create":
        if not name:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "name parameter required for create action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Creating schematic: {name}")

            sch = ksa.create_schematic(name)
            set_current_schematic(sch)

            if ctx:
                await ctx.report_progress(100, 100, f"Created: {name}")

            logger.info(f"[MCP] Created schematic: {name}")
            return {
                "success": True,
                "project_name": sch.title_block.get("title") or name,
                "uuid": str(sch.uuid),
                "message": f"Created schematic: {name}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error creating schematic: {e}", exc_info=True)
            return {
                "success": False,
                "error": "CREATE_ERROR",
                "message": f"Failed to create schematic: {str(e)}",
            }

    elif action == "read":
        schematic = get_current_schematic()
        if schematic is None:
            return {
                "success": False,
                "error": "NO_SCHEMATIC_LOADED",
                "message": "No schematic is currently loaded",
            }

        try:
            component_refs = [c.reference for c in schematic.components]
            return {
                "success": True,
                "project_name": schematic.title_block.get("title") or "Untitled",
                "uuid": str(schematic.uuid),
                "component_count": len(schematic.components),
                "component_references": component_refs,
            }
        except Exception as e:
            logger.error(f"[MCP] Error reading schematic: {e}", exc_info=True)
            return {
                "success": False,
                "error": "READ_ERROR",
                "message": f"Failed to read schematic: {str(e)}",
            }

    elif action == "save":
        schematic = get_current_schematic()
        if schematic is None:
            return {
                "success": False,
                "error": "NO_SCHEMATIC_LOADED",
                "message": "No schematic is currently loaded",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, "Saving schematic")

            schematic.save(file_path) if file_path else schematic.save()
            actual_path = file_path or getattr(schematic, "_file_path", "")

            if ctx:
                await ctx.report_progress(100, 100, "Save complete")

            logger.info(f"[MCP] Saved schematic to: {actual_path}")
            return {
                "success": True,
                "message": f"Saved to {actual_path or 'original location'}",
                "file_path": actual_path,
            }
        except Exception as e:
            logger.error(f"[MCP] Error saving schematic: {e}", exc_info=True)
            return {
                "success": False,
                "error": "SAVE_ERROR",
                "message": f"Failed to save schematic: {str(e)}",
            }

    elif action == "load":
        if not file_path:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "file_path parameter required for load action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Loading schematic: {file_path}")

            sch = ksa.Schematic.load(file_path)
            set_current_schematic(sch)

            if ctx:
                await ctx.report_progress(100, 100, "Load complete")

            logger.info(f"[MCP] Loaded schematic from: {file_path}")
            return {
                "success": True,
                "project_name": sch.title_block.get("title") or "Untitled",
                "uuid": str(sch.uuid),
                "component_count": len(sch.components),
                "file_path": file_path,
                "message": f"Loaded schematic from {file_path}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error loading schematic: {e}", exc_info=True)
            return {
                "success": False,
                "error": "LOAD_ERROR",
                "message": f"Failed to load schematic: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: create, read, save, load",
        }


# ============================================================================
# 2. MANAGE COMPONENTS (add, list, get_pins, update, remove)
# ============================================================================


async def manage_components(
    action: str,
    lib_id: Optional[str] = None,
    value: Optional[str] = None,
    reference: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    rotation: Optional[float] = None,
    footprint: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage components (add, list, get_pins, update, remove).

    Args:
        action: Operation ("add", "list", "get_pins", "update", "remove")
        lib_id: Library ID (required for "add")
        value: Component value (required for "add")
        reference: Reference designator (optional for "add", required for others)
        position: Position tuple (for "add"/"update")
        rotation: Rotation in degrees (for "add"/"update")
        footprint: Footprint string (for "add"/"update")
        ctx: MCP context (optional)

    Returns:
        Dictionary with component data or error
    """
    logger.info(f"[MCP] manage_components called: action={action}")

    schematic = get_current_schematic()
    if schematic is None and action != "add":
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not lib_id or not value:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "lib_id and value are required for add action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Adding component: {lib_id}")

            component = schematic.components.add(
                lib_id=lib_id,
                reference=reference,
                value=value,
                position=position,
                rotation=rotation or 0.0,
                footprint=footprint,
            )

            if ctx:
                await ctx.report_progress(100, 100, f"Added {component.reference}")

            logger.info(f"[MCP] Added component: {component.reference}")
            return {
                "success": True,
                "reference": component.reference,
                "lib_id": component.lib_id,
                "value": component.value,
                "position": {"x": component.position.x, "y": component.position.y},
                "rotation": component.rotation,
                "uuid": str(component.uuid),
                "message": f"Added {component.reference} ({value})",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding component: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add component: {str(e)}",
            }

    elif action == "list":
        try:
            components = []
            for comp in schematic.components:
                components.append(
                    {
                        "reference": comp.reference,
                        "lib_id": comp.lib_id,
                        "value": comp.value,
                        "position": {"x": comp.position.x, "y": comp.position.y},
                        "rotation": comp.rotation,
                        "uuid": str(comp.uuid),
                    }
                )

            logger.info(f"[MCP] Listed {len(components)} components")
            return {
                "success": True,
                "count": len(components),
                "components": components,
            }
        except Exception as e:
            logger.error(f"[MCP] Error listing components: {e}", exc_info=True)
            return {
                "success": False,
                "error": "LIST_ERROR",
                "message": f"Failed to list components: {str(e)}",
            }

    elif action == "get_pins":
        if not reference:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "reference parameter required for get_pins action",
            }

        try:
            # Get pin information using the schematic's pin discovery method
            pins_data = schematic.components.get_pins_info(reference)
            if not pins_data:
                return {
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": f"Component {reference} not found",
                }

            pins = []
            for pin in pins_data:
                pins.append(
                    {
                        "number": str(pin.number),
                        "name": pin.name,
                        "position": {
                            "x": pin.position.x,
                            "y": pin.position.y,
                        },
                        "electrical_type": (
                            pin.electrical_type.value
                            if hasattr(pin.electrical_type, "value")
                            else str(pin.electrical_type)
                        ),
                        "pin_type": (
                            pin.shape.value if hasattr(pin.shape, "value") else str(pin.shape)
                        ),
                    }
                )

            logger.info(f"[MCP] Got pins for {reference}: {len(pins)} pins")
            return {
                "success": True,
                "reference": reference,
                "pin_count": len(pins),
                "pins": pins,
            }
        except Exception as e:
            logger.error(f"[MCP] Error getting pins for {reference}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "GET_PINS_ERROR",
                "message": f"Failed to get pins: {str(e)}",
            }

    elif action == "update":
        if not reference:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "reference parameter required for update action",
            }

        try:
            component = schematic.components.get(reference)
            if not component:
                return {
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": f"Component {reference} not found",
                }

            updated_fields = []
            if value is not None:
                component.value = value
                updated_fields.append("value")
            if position is not None:
                component.position = position
                updated_fields.append("position")
            if rotation is not None:
                component.rotation = rotation
                updated_fields.append("rotation")
            if footprint is not None:
                component.footprint = footprint
                updated_fields.append("footprint")

            logger.info(f"[MCP] Updated {reference}: {updated_fields}")
            return {
                "success": True,
                "reference": reference,
                "message": f"Updated {reference}",
                "updated_fields": updated_fields,
            }
        except Exception as e:
            logger.error(f"[MCP] Error updating {reference}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "UPDATE_ERROR",
                "message": f"Failed to update component: {str(e)}",
            }

    elif action == "remove":
        if not reference:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "reference parameter required for remove action",
            }

        try:
            schematic.components.remove(reference)

            logger.info(f"[MCP] Removed component: {reference}")
            return {
                "success": True,
                "reference": reference,
                "message": f"Removed {reference} and all connected wires",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing {reference}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove component: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, list, get_pins, update, remove",
        }


# ============================================================================
# 3. MANAGE WIRES (add, remove)
# ============================================================================


async def manage_wires(
    action: str,
    start: Optional[Tuple[float, float]] = None,
    end: Optional[Tuple[float, float]] = None,
    wire_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage wires (add, remove).

    Args:
        action: Operation ("add", "remove")
        start: Start point (required for "add")
        end: End point (required for "add")
        wire_uuid: Wire UUID (required for "remove")
        ctx: MCP context (optional)

    Returns:
        Dictionary with wire data or error
    """
    logger.info(f"[MCP] manage_wires called: action={action}")

    schematic = get_current_schematic()
    if schematic is None:
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not start or not end:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "start and end parameters required for add action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, "Adding wire")

            wire_uuid = schematic.wires.add(start=start, end=end)

            if ctx:
                await ctx.report_progress(100, 100, "Wire added")

            logger.info(f"[MCP] Added wire: {start} -> {end}")
            return {
                "success": True,
                "wire_uuid": str(wire_uuid),
                "start": {"x": start[0], "y": start[1]},
                "end": {"x": end[0], "y": end[1]},
                "message": "Added wire connection",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding wire: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add wire: {str(e)}",
            }

    elif action == "remove":
        if not wire_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "wire_uuid parameter required for remove action",
            }

        try:
            schematic.remove_wire(wire_uuid)

            logger.info(f"[MCP] Removed wire: {wire_uuid}")
            return {
                "success": True,
                "wire_uuid": wire_uuid,
                "message": "Removed wire",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing wire: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove wire: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, remove",
        }


# ============================================================================
# 4. MANAGE LABELS (add, remove)
# ============================================================================


async def manage_labels(
    action: str,
    text: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    rotation: float = 0.0,
    label_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage labels (add, remove).

    Args:
        action: Operation ("add", "remove")
        text: Label text (required for "add")
        position: Position (required for "add")
        rotation: Rotation in degrees (optional)
        label_uuid: Label UUID (required for "remove")
        ctx: MCP context (optional)

    Returns:
        Dictionary with label data or error
    """
    logger.info(f"[MCP] manage_labels called: action={action}")

    schematic = get_current_schematic()
    if schematic is None:
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not text or not position:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "text and position parameters required for add action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Adding label: {text}")

            label_uuid = schematic.add_label(text=text, position=position, rotation=rotation)

            if ctx:
                await ctx.report_progress(100, 100, f"Label added: {text}")

            logger.info(f"[MCP] Added label: {text}")
            return {
                "success": True,
                "label_uuid": str(label_uuid),
                "text": text,
                "position": {"x": position[0], "y": position[1]},
                "rotation": rotation,
                "message": f"Added label: {text}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding label: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add label: {str(e)}",
            }

    elif action == "remove":
        if not label_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "label_uuid parameter required for remove action",
            }

        try:
            schematic.remove_label(label_uuid)

            logger.info(f"[MCP] Removed label: {label_uuid}")
            return {
                "success": True,
                "label_uuid": label_uuid,
                "message": "Removed label",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing label: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove label: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, remove",
        }


# ============================================================================
# 5. MANAGE TEXT BOXES (add, update, remove)
# ============================================================================


async def manage_text_boxes(
    action: str,
    text: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    size: Optional[Tuple[float, float]] = None,
    rotation: float = 0.0,
    font_size: Optional[float] = None,
    text_box_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage text boxes (add, update, remove).

    Args:
        action: Operation ("add", "update", "remove")
        text: Text content (required for "add", optional for "update")
        position: Position (required for "add")
        size: Size tuple (required for "add")
        rotation: Rotation in degrees (optional)
        font_size: Font size (optional)
        text_box_uuid: TextBox UUID (required for "update"/"remove")
        ctx: MCP context (optional)

    Returns:
        Dictionary with text box data or error
    """
    logger.info(f"[MCP] manage_text_boxes called: action={action}")

    schematic = get_current_schematic()
    if schematic is None:
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not text or not position or not size:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "text, position, and size parameters required for add action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, "Adding text box")

            text_box_uuid = schematic.add_text_box(
                text=text,
                position=position,
                size=size,
                rotation=rotation,
                font_size=font_size,
            )

            if ctx:
                await ctx.report_progress(100, 100, "Text box added")

            logger.info(f"[MCP] Added text box")
            return {
                "success": True,
                "text_box_uuid": str(text_box_uuid),
                "text": text,
                "position": {"x": position[0], "y": position[1]},
                "size": {"width": size[0], "height": size[1]},
                "message": "Added text box",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding text box: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add text box: {str(e)}",
            }

    elif action == "update":
        if not text_box_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "text_box_uuid parameter required for update action",
            }

        try:
            # Try to update text box via Python API
            text_box = schematic.update_text_box(
                text_box_uuid=text_box_uuid,
                text=text,
                font_size=font_size,
            )

            updated_fields = []
            if text is not None:
                updated_fields.append("text")
            if font_size is not None:
                updated_fields.append("font_size")

            logger.info(f"[MCP] Updated text box: {updated_fields}")
            return {
                "success": True,
                "text_box_uuid": text_box_uuid,
                "message": "Updated text box",
                "updated_fields": updated_fields,
            }
        except Exception as e:
            logger.error(f"[MCP] Error updating text box: {e}", exc_info=True)
            return {
                "success": False,
                "error": "UPDATE_ERROR",
                "message": f"Failed to update text box: {str(e)}",
            }

    elif action == "remove":
        if not text_box_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "text_box_uuid parameter required for remove action",
            }

        try:
            schematic.remove_text_box(text_box_uuid)

            logger.info(f"[MCP] Removed text box: {text_box_uuid}")
            return {
                "success": True,
                "text_box_uuid": text_box_uuid,
                "message": "Removed text box",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing text box: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove text box: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, update, remove",
        }


# ============================================================================
# 6. MANAGE POWER (add, list, remove)
# ============================================================================


async def manage_power(
    action: str,
    power_net: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    symbol_variant: str = "auto",
    power_symbol_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage power symbols (add, list, remove).

    Args:
        action: Operation ("add", "list", "remove")
        power_net: Power net name (required for "add")
        position: Position (required for "add")
        symbol_variant: Symbol variant (optional)
        power_symbol_uuid: Power symbol UUID (required for "remove")
        ctx: MCP context (optional)

    Returns:
        Dictionary with power data or error
    """
    logger.info(f"[MCP] manage_power called: action={action}")

    schematic = get_current_schematic()
    if schematic is None:
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not power_net or not position:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "power_net and position parameters required for add action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Adding power symbol: {power_net}")

            symbol = schematic.add_power_symbol(
                power_net=power_net,
                position=position,
                symbol_variant=symbol_variant,
            )

            if ctx:
                await ctx.report_progress(100, 100, f"Power symbol added: {power_net}")

            logger.info(f"[MCP] Added power symbol: {power_net}")
            return {
                "success": True,
                "symbol_uuid": str(symbol.uuid) if hasattr(symbol, "uuid") else power_net,
                "power_net": power_net,
                "position": {"x": position[0], "y": position[1]},
                "message": f"Added power symbol: {power_net}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding power symbol: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add power symbol: {str(e)}",
            }

    elif action == "list":
        try:
            # Try to list power nets from schematic
            power_nets = []
            # This is a placeholder; actual implementation depends on Python API
            try:
                for power_net in schematic.power_nets:  # If method exists
                    power_nets.append(
                        {
                            "name": power_net.name,
                            "position": {"x": power_net.position.x, "y": power_net.position.y},
                            "uuid": str(power_net.uuid),
                        }
                    )
            except AttributeError:
                # Fallback: return empty list if power_nets not available
                power_nets = []

            logger.info(f"[MCP] Listed {len(power_nets)} power nets")
            return {
                "success": True,
                "count": len(power_nets),
                "power_nets": power_nets,
            }
        except Exception as e:
            logger.error(f"[MCP] Error listing power nets: {e}", exc_info=True)
            return {
                "success": False,
                "error": "LIST_ERROR",
                "message": f"Failed to list power nets: {str(e)}",
            }

    elif action == "remove":
        if not power_symbol_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "power_symbol_uuid parameter required for remove action",
            }

        try:
            schematic.remove_power_symbol(power_symbol_uuid)

            logger.info(f"[MCP] Removed power symbol: {power_symbol_uuid}")
            return {
                "success": True,
                "power_symbol_uuid": power_symbol_uuid,
                "message": "Removed power symbol",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing power symbol: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove power symbol: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, list, remove",
        }


# ============================================================================
# 7. MANAGE SHEETS (add, set_context, list, remove)
# ============================================================================


async def manage_sheets(
    action: str,
    name: Optional[str] = None,
    filename: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    size: Optional[Tuple[float, float]] = None,
    project_name: Optional[str] = None,
    parent_uuid: Optional[str] = None,
    sheet_uuid: Optional[str] = None,
    # Pin-related parameters
    pin_name: Optional[str] = None,
    pin_type: Optional[str] = None,
    edge: Optional[str] = None,
    position_along_edge: Optional[float] = None,
    pin_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage hierarchical sheets (add, set_context, list, remove, add_pin, remove_pin).

    Args:
        action: Operation ("add", "set_context", "list", "remove", "add_pin", "remove_pin")
        name: Sheet name (required for "add")
        filename: Filename (required for "add")
        position: Position (required for "add")
        size: Size (required for "add")
        project_name: Project name (optional for "add")
        parent_uuid: Parent UUID (required for "set_context")
        sheet_uuid: Sheet UUID (required for "set_context"/"remove"/"add_pin"/"remove_pin")
        pin_name: Pin name (required for "add_pin")
        pin_type: Pin electrical type (required for "add_pin")
        edge: Pin edge placement (required for "add_pin")
        position_along_edge: Distance along edge in mm (required for "add_pin")
        pin_uuid: Pin UUID (required for "remove_pin")
        ctx: MCP context (optional)

    Returns:
        Dictionary with sheet data or error
    """
    logger.info(f"[MCP] manage_sheets called: action={action}")

    schematic = get_current_schematic()
    if schematic is None:
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not name or not filename or not position or not size:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "name, filename, position, and size are required for add action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Adding hierarchical sheet: {name}")

            sheet_uuid = schematic.sheets.add_sheet(
                name=name,
                filename=filename,
                position=position,
                size=size,
                project_name=project_name or schematic.title_block.get("title"),
            )

            if ctx:
                await ctx.report_progress(100, 100, f"Sheet added: {name}")

            logger.info(f"[MCP] Added hierarchical sheet: {name}")
            return {
                "success": True,
                "sheet_uuid": str(sheet_uuid),
                "name": name,
                "filename": filename,
                "position": {"x": position[0], "y": position[1]},
                "size": {"width": size[0], "height": size[1]},
                "message": f"Added hierarchical sheet: {name}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding hierarchical sheet: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add hierarchical sheet: {str(e)}",
            }

    elif action == "set_context":
        if not parent_uuid or not sheet_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "parent_uuid and sheet_uuid are required for set_context action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, "Setting hierarchy context")

            schematic.set_hierarchy_context(parent_uuid, sheet_uuid)

            if ctx:
                await ctx.report_progress(100, 100, "Context set")

            logger.info(f"[MCP] Set hierarchy context: parent={parent_uuid}, sheet={sheet_uuid}")
            return {
                "success": True,
                "message": "Hierarchy context set",
                "parent_uuid": parent_uuid,
                "sheet_uuid": sheet_uuid,
            }
        except Exception as e:
            logger.error(f"[MCP] Error setting hierarchy context: {e}", exc_info=True)
            return {
                "success": False,
                "error": "CONTEXT_ERROR",
                "message": f"Failed to set hierarchy context: {str(e)}",
            }

    elif action == "list":
        try:
            sheets = []
            # Try to iterate through sheets - handle different API versions
            try:
                # Try getting all sheets
                for sheet in (
                    schematic.sheets.values()
                    if hasattr(schematic.sheets, "values")
                    else schematic.sheets
                ):
                    sheets.append(
                        {
                            "uuid": str(sheet.uuid) if hasattr(sheet, "uuid") else str(sheet),
                            "name": sheet.name if hasattr(sheet, "name") else "",
                            "filename": sheet.filename if hasattr(sheet, "filename") else "",
                            "position": {
                                "x": sheet.position.x if hasattr(sheet, "position") else 0,
                                "y": sheet.position.y if hasattr(sheet, "position") else 0,
                            },
                        }
                    )
            except (TypeError, AttributeError):
                # If iteration doesn't work, try using a method
                pass

            logger.info(f"[MCP] Listed {len(sheets)} hierarchical sheets")
            return {
                "success": True,
                "count": len(sheets),
                "sheets": sheets,
            }
        except Exception as e:
            logger.error(f"[MCP] Error listing sheets: {e}", exc_info=True)
            return {
                "success": False,
                "error": "LIST_ERROR",
                "message": f"Failed to list sheets: {str(e)}",
            }

    elif action == "remove":
        if not sheet_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "sheet_uuid parameter required for remove action",
            }

        try:
            schematic.sheets.remove(sheet_uuid)

            logger.info(f"[MCP] Removed hierarchical sheet: {sheet_uuid}")
            return {
                "success": True,
                "sheet_uuid": sheet_uuid,
                "message": "Removed hierarchical sheet",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing sheet: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove sheet: {str(e)}",
            }

    elif action == "add_pin":
        if (
            not sheet_uuid
            or not pin_name
            or not pin_type
            or not edge
            or position_along_edge is None
        ):
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "sheet_uuid, pin_name, pin_type, edge, and position_along_edge are required for add_pin action",
            }

        # Validate pin_type
        valid_pin_types = ["input", "output", "bidirectional", "tri_state", "passive"]
        if pin_type not in valid_pin_types:
            return {
                "success": False,
                "error": "INVALID_PIN_TYPE",
                "message": f"pin_type must be one of: {', '.join(valid_pin_types)}. Got: {pin_type}",
            }

        # Validate edge
        valid_edges = ["left", "right", "top", "bottom"]
        if edge not in valid_edges:
            return {
                "success": False,
                "error": "INVALID_EDGE",
                "message": f"edge must be one of: {', '.join(valid_edges)}. Got: {edge}",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Adding sheet pin: {pin_name}")

            # Add the pin (core library calculates absolute position)
            pin_uuid = schematic.sheets.add_sheet_pin(
                sheet_uuid=sheet_uuid,
                name=pin_name,
                pin_type=pin_type,
                edge=edge,
                position_along_edge=position_along_edge,
            )

            if pin_uuid is None:
                return {
                    "success": False,
                    "error": "SHEET_NOT_FOUND",
                    "message": f"Sheet not found: {sheet_uuid}",
                }

            if ctx:
                await ctx.report_progress(100, 100, f"Sheet pin added: {pin_name}")

            logger.info(f"[MCP] Added sheet pin: {pin_name} to sheet {sheet_uuid}")
            return {
                "success": True,
                "pin_uuid": str(pin_uuid),
                "sheet_uuid": sheet_uuid,
                "pin_name": pin_name,
                "pin_type": pin_type,
                "edge": edge,
                "position_along_edge": position_along_edge,
                "message": f"Added sheet pin: {pin_name}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding sheet pin: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_PIN_ERROR",
                "message": f"Failed to add sheet pin: {str(e)}",
            }

    elif action == "remove_pin":
        if not sheet_uuid or not pin_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "sheet_uuid and pin_uuid are required for remove_pin action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, "Removing sheet pin")

            schematic.sheets.remove_sheet_pin(
                sheet_uuid=sheet_uuid,
                pin_uuid=pin_uuid,
            )

            if ctx:
                await ctx.report_progress(100, 100, "Sheet pin removed")

            logger.info(f"[MCP] Removed sheet pin: {pin_uuid} from sheet {sheet_uuid}")
            return {
                "success": True,
                "sheet_uuid": sheet_uuid,
                "pin_uuid": pin_uuid,
                "message": "Removed sheet pin",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing sheet pin: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_PIN_ERROR",
                "message": f"Failed to remove sheet pin: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, set_context, list, remove, add_pin, remove_pin",
        }


# ============================================================================
# 8. MANAGE GLOBAL LABELS (add, remove)
# ============================================================================


async def manage_global_labels(
    action: str,
    text: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    shape: str = "input",
    rotation: float = 0.0,
    label_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage global labels (add, remove).

    Args:
        action: Operation ("add", "remove")
        text: Label text (required for "add")
        position: Position (required for "add")
        shape: Label shape (optional)
        rotation: Rotation in degrees (optional)
        label_uuid: Label UUID (required for "remove")
        ctx: MCP context (optional)

    Returns:
        Dictionary with label data or error
    """
    logger.info(f"[MCP] manage_global_labels called: action={action}")

    schematic = get_current_schematic()
    if schematic is None:
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not text or not position:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "text and position parameters required for add action",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Adding global label: {text}")

            label_uuid = schematic.add_global_label(
                text=text,
                position=position,
                shape=shape,
                rotation=rotation,
            )

            if ctx:
                await ctx.report_progress(100, 100, f"Global label added: {text}")

            logger.info(f"[MCP] Added global label: {text}")
            return {
                "success": True,
                "label_uuid": str(label_uuid),
                "text": text,
                "position": {"x": position[0], "y": position[1]},
                "shape": shape,
                "rotation": rotation,
                "message": f"Added global label: {text}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding global label: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add global label: {str(e)}",
            }

    elif action == "remove":
        if not label_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "label_uuid parameter required for remove action",
            }

        try:
            schematic.remove_global_label(label_uuid)

            logger.info(f"[MCP] Removed global label: {label_uuid}")
            return {
                "success": True,
                "label_uuid": label_uuid,
                "message": "Removed global label",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing global label: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove global label: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, remove",
        }


# ============================================================================
# 9. MANAGE HIERARCHICAL LABELS (add, remove)
# ============================================================================


async def manage_hierarchical_labels(
    action: str,
    text: Optional[str] = None,
    position: Optional[Tuple[float, float]] = None,
    shape: str = "input",
    rotation: float = 0.0,
    size: float = 1.27,
    label_uuid: Optional[str] = None,
    ctx: Optional[Context] = None,
) -> dict:
    """
    Manage hierarchical labels (add, remove).

    Hierarchical labels connect child schematics to parent sheet pins.
    They enable signal routing through hierarchical sheet boundaries.

    Args:
        action: Operation ("add", "remove")
        text: Label text (required for "add")
        position: Position (required for "add")
        shape: Label shape - "input", "output", "bidirectional", "tri_state", "passive" (optional)
        rotation: Rotation in degrees (optional)
        size: Text size in mm (optional, default: 1.27)
        label_uuid: Label UUID (required for "remove")
        ctx: MCP context (optional)

    Returns:
        Dictionary with label data or error
    """
    logger.info(f"[MCP] manage_hierarchical_labels called: action={action}")

    schematic = get_current_schematic()
    if schematic is None:
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded",
        }

    if action == "add":
        if not text or not position:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "text and position parameters required for add action",
            }

        # Validate shape
        valid_shapes = ["input", "output", "bidirectional", "tri_state", "passive"]
        if shape not in valid_shapes:
            return {
                "success": False,
                "error": "INVALID_SHAPE",
                "message": f"Shape must be one of: {', '.join(valid_shapes)}. Got: {shape}",
            }

        try:
            if ctx:
                await ctx.report_progress(0, 100, f"Adding hierarchical label: {text}")

            label_uuid = schematic.add_hierarchical_label(
                text=text,
                position=position,
                shape=shape,
                rotation=rotation,
                size=size,
            )

            if ctx:
                await ctx.report_progress(100, 100, f"Hierarchical label added: {text}")

            logger.info(f"[MCP] Added hierarchical label: {text}")
            return {
                "success": True,
                "label_uuid": str(label_uuid),
                "text": text,
                "position": {"x": position[0], "y": position[1]},
                "shape": shape,
                "rotation": rotation,
                "size": size,
                "message": f"Added hierarchical label: {text}",
            }
        except Exception as e:
            logger.error(f"[MCP] Error adding hierarchical label: {e}", exc_info=True)
            return {
                "success": False,
                "error": "ADD_ERROR",
                "message": f"Failed to add hierarchical label: {str(e)}",
            }

    elif action == "remove":
        if not label_uuid:
            return {
                "success": False,
                "error": "INVALID_PARAMS",
                "message": "label_uuid parameter required for remove action",
            }

        try:
            schematic.remove_hierarchical_label(label_uuid)

            logger.info(f"[MCP] Removed hierarchical label: {label_uuid}")
            return {
                "success": True,
                "label_uuid": label_uuid,
                "message": "Removed hierarchical label",
            }
        except Exception as e:
            logger.error(f"[MCP] Error removing hierarchical label: {e}", exc_info=True)
            return {
                "success": False,
                "error": "REMOVE_ERROR",
                "message": f"Failed to remove hierarchical label: {str(e)}",
            }

    else:
        return {
            "success": False,
            "error": "INVALID_ACTION",
            "message": f"Unknown action: {action}. Valid actions: add, remove",
        }
