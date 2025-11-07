"""KiCAD Schematic API - MCP Server Package

This package contains the Model Context Protocol (MCP) server implementation
for the kicad-sch-api library.

Main features:
- Tool implementations for schematic manipulation
- Integrated logging framework
- Performance monitoring
- Error handling and recovery
"""

from mcp_server.utils import (
    configure_mcp_logging,
    get_mcp_logger,
)
from mcp_server.models import (
    PointModel,
    PinInfoOutput,
    ComponentPinsOutput,
    ComponentInfoOutput,
    ErrorOutput,
)

__version__ = "0.1.0"
__all__ = [
    "configure_mcp_logging",
    "get_mcp_logger",
    "PointModel",
    "PinInfoOutput",
    "ComponentPinsOutput",
    "ComponentInfoOutput",
    "ErrorOutput",
]
