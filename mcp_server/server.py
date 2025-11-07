#!/usr/bin/env python3
"""
MCP server main entry point for kicad-sch-api.

Provides schematic management and pin discovery tools via the Model Context Protocol.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

import kicad_sch_api as ksa
from mcp_server.models import ErrorOutput
from mcp_server.tools.pin_discovery import (
    find_pins_by_name,
    find_pins_by_type,
    get_component_pins,
    get_current_schematic,
    set_current_schematic,
)
from mcp_server.tools.component_tools import add_component


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("kicad-sch-api")


# ========== Schematic Management Tools ==========


@mcp.tool()
async def create_schematic(name: str) -> dict:
    """
    Create a new blank KiCAD schematic.

    Args:
        name: Project name for the schematic

    Returns:
        Dictionary with success status and schematic information

    Examples:
        >>> result = await create_schematic("MyProject")
        >>> print(result['message'])
        Created new schematic: MyProject
    """
    logger.info(f"[MCP] create_schematic called with name: {name}")

    try:
        # Create new schematic
        schematic = ksa.create_schematic(name)

        # Set as current working schematic
        set_current_schematic(schematic)

        logger.info(f"[MCP] Created and set schematic: {name}")
        return {
            "success": True,
            "message": f"Created new schematic: {name}",
            "project_name": name,
            "uuid": str(schematic.uuid),
        }

    except Exception as e:
        logger.error(f"[MCP] Error creating schematic: {e}", exc_info=True)
        return {
            "success": False,
            "error": "CREATION_ERROR",
            "message": f"Failed to create schematic: {str(e)}",
        }


@mcp.tool()
async def load_schematic(file_path: str) -> dict:
    """
    Load an existing KiCAD schematic file.

    Args:
        file_path: Absolute path to .kicad_sch file

    Returns:
        Dictionary with success status and schematic information

    Examples:
        >>> result = await load_schematic("/path/to/project.kicad_sch")
        >>> print(f"Loaded: {result['project_name']}")
    """
    logger.info(f"[MCP] load_schematic called with path: {file_path}")

    try:
        # Validate path
        path = Path(file_path)
        if not path.exists():
            logger.error(f"[MCP] File not found: {file_path}")
            return {
                "success": False,
                "error": "FILE_NOT_FOUND",
                "message": f"Schematic file not found: {file_path}",
            }

        if not path.suffix == ".kicad_sch":
            logger.error(f"[MCP] Invalid file extension: {file_path}")
            return {
                "success": False,
                "error": "INVALID_FILE",
                "message": "File must have .kicad_sch extension",
            }

        # Load schematic
        schematic = ksa.Schematic.load(str(path))

        # Set as current working schematic
        set_current_schematic(schematic)

        # Count components
        component_count = len(list(schematic.components.all()))

        logger.info(
            f"[MCP] Loaded schematic: {schematic.title_block.title} "
            f"({component_count} components)"
        )
        return {
            "success": True,
            "message": f"Loaded schematic: {path.name}",
            "file_path": str(path),
            "project_name": schematic.title_block.title,
            "uuid": str(schematic.uuid),
            "component_count": component_count,
        }

    except Exception as e:
        logger.error(f"[MCP] Error loading schematic: {e}", exc_info=True)
        return {
            "success": False,
            "error": "LOAD_ERROR",
            "message": f"Failed to load schematic: {str(e)}",
        }


@mcp.tool()
async def save_schematic(file_path: Optional[str] = None) -> dict:
    """
    Save the current schematic to disk.

    Args:
        file_path: Optional path to save to. If not provided, saves to original location.

    Returns:
        Dictionary with success status

    Examples:
        >>> # Save to original location
        >>> result = await save_schematic()

        >>> # Save to new location
        >>> result = await save_schematic("/path/to/new_location.kicad_sch")
    """
    logger.info(f"[MCP] save_schematic called with path: {file_path}")

    # Check if schematic is loaded
    schematic = get_current_schematic()
    if schematic is None:
        logger.error("[MCP] No schematic loaded")
        return {
            "success": False,
            "error": "NO_SCHEMATIC_LOADED",
            "message": "No schematic is currently loaded. Please load or create a schematic first.",
        }

    try:
        if file_path:
            # Save to specified path
            path = Path(file_path)
            if not path.suffix == ".kicad_sch":
                logger.error(f"[MCP] Invalid file extension: {file_path}")
                return {
                    "success": False,
                    "error": "INVALID_FILE",
                    "message": "File must have .kicad_sch extension",
                }
            schematic.save(str(path))
            logger.info(f"[MCP] Saved schematic to: {path}")
            return {
                "success": True,
                "message": f"Saved schematic to: {path.name}",
                "file_path": str(path),
            }
        else:
            # Save to original location
            schematic.save()
            logger.info("[MCP] Saved schematic to original location")
            return {
                "success": True,
                "message": "Saved schematic to original location",
            }

    except Exception as e:
        logger.error(f"[MCP] Error saving schematic: {e}", exc_info=True)
        return {
            "success": False,
            "error": "SAVE_ERROR",
            "message": f"Failed to save schematic: {str(e)}",
        }


@mcp.tool()
async def get_schematic_info() -> dict:
    """
    Get information about the currently loaded schematic.

    Returns:
        Dictionary with schematic metadata

    Examples:
        >>> result = await get_schematic_info()
        >>> print(f"Components: {result['component_count']}")
    """
    logger.info("[MCP] get_schematic_info called")

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
        # Collect schematic information
        components = list(schematic.components.all())
        component_refs = [c.reference for c in components]

        info = {
            "success": True,
            "project_name": schematic.title_block.title,
            "uuid": str(schematic.uuid),
            "component_count": len(components),
            "component_references": component_refs,
            "lib_symbols_count": len(schematic.lib_symbols),
        }

        logger.info(
            f"[MCP] Schematic info: {info['project_name']} ({info['component_count']} components)"
        )
        return info

    except Exception as e:
        logger.error(f"[MCP] Error getting schematic info: {e}", exc_info=True)
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"Failed to get schematic info: {str(e)}",
        }


# ========== Register Pin Discovery Tools ==========

# Register the pin discovery tools from pin_discovery.py
mcp.tool()(get_component_pins)
mcp.tool()(find_pins_by_name)
mcp.tool()(find_pins_by_type)


# ========== Register Component Management Tools ==========

# Register the component management tools from component_tools.py
mcp.tool()(add_component)


# ========== Server Entry Point ==========


def main() -> None:
    """
    Main entry point for the MCP server.

    Starts the FastMCP server with STDIO transport for Claude Desktop integration.
    """
    logger.info("Starting kicad-sch-api MCP server...")
    logger.info(f"kicad-sch-api version: {ksa.__version__}")

    try:
        # Run the MCP server with STDIO transport
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
