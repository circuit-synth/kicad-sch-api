#!/usr/bin/env python3
"""
Basic KiCAD Schematic MCP Server

Simple FastMCP server for schematic manipulation with stateful operation.
"""

import logging
import sys
import traceback
from typing import Optional, Dict, Any, List, Tuple

# Configure logging to stderr (required for MCP STDIO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

try:
    from mcp.server import FastMCP
except ImportError:
    logger.error("MCP not installed. Run: uv add 'mcp[cli]'")
    sys.exit(1)

try:
    import kicad_sch_api as ksa
except ImportError:
    logger.error("kicad-sch-api not found. Make sure it's installed.")
    sys.exit(1)


class SchematicState:
    """Maintains current schematic state for stateful operations."""
    
    def __init__(self):
        self.current_schematic: Optional[ksa.Schematic] = None
        self.current_file_path: Optional[str] = None
    
    def load_schematic(self, file_path: str) -> bool:
        """Load a schematic file."""
        try:
            self.current_schematic = ksa.load_schematic(file_path)
            self.current_file_path = file_path
            logger.info(f"Loaded schematic: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load schematic {file_path}: {e}")
            return False
    
    def create_schematic(self, name: str) -> bool:
        """Create a new schematic."""
        try:
            self.current_schematic = ksa.create_schematic(name)
            self.current_file_path = None  # Not saved yet
            logger.info(f"Created new schematic: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create schematic {name}: {e}")
            return False
    
    def save_schematic(self, file_path: Optional[str] = None) -> bool:
        """Save the current schematic."""
        if not self.current_schematic:
            return False
        
        try:
            save_path = file_path or self.current_file_path
            if not save_path:
                return False
            
            self.current_schematic.save(save_path)
            self.current_file_path = save_path
            logger.info(f"Saved schematic to: {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save schematic: {e}")
            return False
    
    def is_loaded(self) -> bool:
        """Check if a schematic is currently loaded."""
        return self.current_schematic is not None


# Global state instance
state = SchematicState()

# Initialize FastMCP server
mcp = FastMCP("KiCAD-Sch-API")

@mcp.tool()
def create_schematic(name: str) -> Dict[str, Any]:
    """Create a new schematic file."""
    try:
        success = state.create_schematic(name)
        return {
            "success": success,
            "message": f"Created schematic: {name}" if success else "Failed to create schematic",
            "current_schematic": name if success else None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating schematic: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def load_schematic(file_path: str) -> Dict[str, Any]:
    """Load an existing schematic file."""
    try:
        success = state.load_schematic(file_path)
        return {
            "success": success,
            "message": f"Loaded schematic: {file_path}" if success else f"Failed to load: {file_path}",
            "current_schematic": file_path if success else None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error loading schematic: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def save_schematic(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Save the current schematic to a file."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded"
            }
        
        success = state.save_schematic(file_path)
        save_path = file_path or state.current_file_path
        return {
            "success": success,
            "message": f"Saved to: {save_path}" if success else "Failed to save",
            "file_path": save_path if success else None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error saving schematic: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def get_schematic_info() -> Dict[str, Any]:
    """Get information about the currently loaded schematic."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded"
            }
        
        sch = state.current_schematic
        component_count = len(sch.components) if hasattr(sch, 'components') else 0
        
        return {
            "success": True,
            "file_path": state.current_file_path,
            "component_count": component_count,
            "message": f"Schematic loaded with {component_count} components"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting schematic info: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def add_component(lib_id: str, reference: str, value: str, 
                 position: Tuple[float, float], **properties) -> Dict[str, Any]:
    """Add a component to the current schematic."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded. Use load_schematic() or create_schematic() first."
            }
        
        # Add component using our API
        component = state.current_schematic.components.add(
            lib_id=lib_id,
            reference=reference,
            value=value,
            position=position,
            **properties
        )
        
        return {
            "success": True,
            "message": f"Added component {reference} ({lib_id})",
            "reference": reference,
            "lib_id": lib_id,
            "position": position
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding component: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def list_components() -> Dict[str, Any]:
    """List all components in the current schematic."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded"
            }
        
        components = []
        for comp in state.current_schematic.components:
            components.append({
                "reference": comp.reference,
                "lib_id": getattr(comp, 'lib_id', 'Unknown'),
                "value": getattr(comp, 'value', ''),
                "position": getattr(comp, 'position', (0, 0))
            })
        
        return {
            "success": True,
            "components": components,
            "count": len(components),
            "message": f"Found {len(components)} components"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing components: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def add_wire(start_pos: Tuple[float, float], end_pos: Tuple[float, float]) -> Dict[str, Any]:
    """Add a wire connection between two points."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded"
            }
        
        # Add wire using our API
        wire = state.current_schematic.wires.add(
            start=start_pos,
            end=end_pos
        )
        
        return {
            "success": True,
            "message": f"Added wire from {start_pos} to {end_pos}",
            "start": start_pos,
            "end": end_pos
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding wire: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.resource("schematic://current")
def get_current_schematic() -> str:
    """Get current schematic state as text."""
    if not state.is_loaded():
        return "No schematic currently loaded"
    
    try:
        info = {
            "file_path": state.current_file_path or "Unsaved",
            "component_count": len(state.current_schematic.components) if hasattr(state.current_schematic, 'components') else 0,
            "loaded": True
        }
        return f"Current schematic: {info}"
    except Exception as e:
        return f"Error getting current schematic info: {e}"

def main():
    """Run the MCP server."""
    logger.info("Starting KiCAD Schematic MCP Server...")
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()