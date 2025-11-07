"""
MCP tools for kicad-sch-api.

Provides tool implementations for pin discovery, component manipulation,
and connectivity operations.
"""

from mcp_server.tools.connectivity_tools import (
    add_junction,
    add_label,
    add_wire,
    connect_components,
)
from mcp_server.tools.pin_discovery import (
    find_pins_by_name,
    find_pins_by_type,
    get_component_pins,
    get_current_schematic,
    set_current_schematic,
)

__all__ = [
    "get_component_pins",
    "find_pins_by_name",
    "find_pins_by_type",
    "get_current_schematic",
    "set_current_schematic",
    "add_wire",
    "add_label",
    "add_junction",
    "connect_components",
]
