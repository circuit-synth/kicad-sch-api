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
    from ..library.cache import get_symbol_cache
    from ..discovery.search_index import get_search_index, ensure_index_built
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

# Initialize discovery system on server startup
logger.info("Initializing component discovery system...")
try:
    # Ensure search index is available (build if needed)
    component_count = ensure_index_built()
    logger.info(f"Component discovery ready: {component_count} components indexed")
except Exception as e:
    logger.warning(f"Component discovery initialization failed: {e}")
    logger.warning("Search features may not work until manually initialized")

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
    """Add a component to the current schematic with enhanced error handling."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded. Use load_schematic() or create_schematic() first."
            }
        
        # Pre-validate the component exists
        cache = get_symbol_cache()
        symbol = cache.get_symbol(lib_id)
        
        if not symbol:
            # Provide suggestions for invalid lib_id
            search_term = lib_id.split(":")[-1] if ":" in lib_id else lib_id
            suggestions = cache.search_symbols(search_term, limit=3)
            
            return {
                "success": False,
                "message": f"Component '{lib_id}' not found",
                "suggestions": [
                    {
                        "lib_id": s.lib_id,
                        "name": s.name,
                        "description": s.description,
                        "common_footprints": _suggest_common_footprints(s)[:2]
                    }
                    for s in suggestions
                ],
                "help": "Use search_components() to find valid component lib_ids"
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
            "message": f"Added component {reference} ({lib_id}) at {position}",
            "reference": reference,
            "lib_id": lib_id,
            "position": position,
            "pins": len(symbol.pins),
            "suggested_footprints": _suggest_common_footprints(symbol)[:3]
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

@mcp.tool()
def search_components(query: str, library: Optional[str] = None, 
                     category: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """Search for components across KiCAD symbol libraries using fast SQLite index."""
    try:
        # Ensure search index is built
        ensure_index_built()
        
        # Use the fast search index
        search_index = get_search_index()
        results = search_index.search(query, library, category, limit)
        
        # Enhance results with footprint suggestions and usage context
        formatted_results = []
        for result in results:
            # Get footprint suggestions based on component type
            common_footprints = _suggest_common_footprints_by_prefix(result["reference_prefix"])
            
            formatted_results.append({
                "lib_id": result["lib_id"],
                "name": result["name"],
                "description": result["description"],
                "library": result["library"],
                "pins": result["pin_count"],
                "reference_prefix": result["reference_prefix"],
                "keywords": result["keywords"],
                "category": result["category"],
                "match_score": round(result["match_score"], 2),
                "common_footprints": common_footprints,
                "usage_context": _get_usage_context_by_prefix(result["reference_prefix"])
            })
        
        return {
            "success": True,
            "results": formatted_results,
            "total_found": len(results),
            "query": query,
            "search_time_ms": 0,  # SQLite searches are very fast
            "message": f"Found {len(results)} components matching '{query}'"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error searching components: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def list_libraries() -> Dict[str, Any]:
    """List all available KiCAD symbol libraries."""
    try:
        cache = get_symbol_cache()
        
        # Get library statistics
        stats = cache.get_performance_stats()
        
        # Get available libraries from the cache
        libraries = []
        for lib_name, lib_stats in cache._lib_stats.items():
            libraries.append({
                "name": lib_name,
                "path": str(lib_stats.library_path),
                "symbol_count": lib_stats.symbol_count,
                "file_size_mb": round(lib_stats.file_size / (1024 * 1024), 2)
            })
        
        return {
            "success": True,
            "libraries": sorted(libraries, key=lambda x: x["name"]),
            "total_libraries": len(libraries),
            "cache_stats": {
                "total_symbols_cached": stats["total_symbols_cached"],
                "cache_hit_rate": stats["hit_rate_percent"]
            },
            "message": f"Found {len(libraries)} symbol libraries"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing libraries: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def validate_component(lib_id: str) -> Dict[str, Any]:
    """Validate that a component exists and get its details."""
    try:
        # First check search index for fast validation
        search_index = get_search_index()
        result = search_index.validate_component(lib_id)
        
        if not result:
            # Search for similar components
            search_term = lib_id.split(":")[-1] if ":" in lib_id else lib_id
            suggestions = search_index.search(search_term, limit=5)
            
            return {
                "success": False,
                "exists": False,
                "lib_id": lib_id,
                "message": f"Component {lib_id} not found",
                "suggestions": [
                    {
                        "lib_id": s["lib_id"],
                        "name": s["name"],
                        "description": s["description"]
                    }
                    for s in suggestions
                ]
            }
        
        return {
            "success": True,
            "exists": True,
            "lib_id": lib_id,
            "details": {
                "name": result["name"],
                "description": result["description"],
                "library": result["library"],
                "pins": result["pin_count"],
                "reference_prefix": result["reference_prefix"],
                "keywords": result["keywords"],
                "category": result["category"]
            },
            "message": f"Component {lib_id} exists"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error validating component: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def browse_library(library_name: str, limit: int = 50) -> Dict[str, Any]:
    """Browse components in a specific library."""
    try:
        cache = get_symbol_cache()
        
        # Get all symbols from the library
        symbols = cache.get_library_symbols(library_name)
        
        if not symbols:
            return {
                "success": False,
                "message": f"Library '{library_name}' not found or empty"
            }
        
        # Format results
        components = []
        for symbol in symbols[:limit]:
            components.append({
                "lib_id": symbol.lib_id,
                "name": symbol.name,
                "description": symbol.description,
                "pins": len(symbol.pins),
                "reference_prefix": symbol.reference_prefix
            })
        
        return {
            "success": True,
            "library": library_name,
            "components": components,
            "showing": len(components),
            "total_in_library": len(symbols),
            "message": f"Showing {len(components)} of {len(symbols)} components in {library_name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error browsing library: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def list_component_categories() -> Dict[str, Any]:
    """List all component categories with counts."""
    try:
        search_index = get_search_index()
        categories = search_index.get_categories()
        
        return {
            "success": True,
            "categories": categories,
            "total_categories": len(categories),
            "message": f"Found {len(categories)} component categories"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing categories: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def get_search_stats() -> Dict[str, Any]:
    """Get search index statistics and performance info."""
    try:
        search_index = get_search_index()
        stats = search_index.get_stats()
        
        return {
            "success": True,
            "stats": stats,
            "message": f"Search index contains {stats['total_components']} components from {stats['total_libraries']} libraries"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting search stats: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def add_hierarchical_sheet(name: str, filename: str, position: Tuple[float, float], 
                          size: Tuple[float, float], project_name: str = "",
                          page_number: str = "2") -> Dict[str, Any]:
    """Add a hierarchical sheet to the current schematic."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded. Use load_schematic() or create_schematic() first."
            }
        
        # Add the hierarchical sheet
        sheet_uuid = state.current_schematic.add_sheet(
            name=name,
            filename=filename,
            position=position,
            size=size,
            project_name=project_name,
            page_number=page_number
        )
        
        return {
            "success": True,
            "message": f"Added hierarchical sheet '{name}' ({filename}) at {position}",
            "sheet_uuid": sheet_uuid,
            "name": name,
            "filename": filename,
            "position": position,
            "size": size,
            "help": "Use add_hierarchical_label() to add pins to connect this sheet to parent schematic"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding hierarchical sheet: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def add_sheet_pin(sheet_uuid: str, name: str, pin_type: str = "input", 
                  position: Tuple[float, float] = (0, 0), rotation: float = 0,
                  size: float = 1.27) -> Dict[str, Any]:
    """Add a pin to a hierarchical sheet for connecting to parent schematic."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded. Use load_schematic() or create_schematic() first."
            }
        
        # Validate pin_type
        valid_pin_types = ["input", "output", "bidirectional", "tri_state", "passive"]
        if pin_type not in valid_pin_types:
            return {
                "success": False,
                "message": f"Invalid pin_type '{pin_type}'. Valid types: {valid_pin_types}",
                "valid_types": valid_pin_types
            }
        
        # Add the sheet pin
        pin_uuid = state.current_schematic.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name=name,
            pin_type=pin_type,
            position=position,
            rotation=rotation,
            size=size
        )
        
        return {
            "success": True,
            "message": f"Added sheet pin '{name}' ({pin_type}) to sheet {sheet_uuid}",
            "pin_uuid": pin_uuid,
            "name": name,
            "pin_type": pin_type,
            "position": position,
            "help": "Create matching hierarchical_label in child schematic for connectivity"
        }
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding sheet pin: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def add_hierarchical_label(text: str, position: Tuple[float, float], 
                          label_type: str = "input", rotation: float = 0,
                          size: float = 1.27) -> Dict[str, Any]:
    """Add a hierarchical label for connecting to parent schematic via sheet pins."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded. Use load_schematic() or create_schematic() first."
            }
        
        # Validate label_type (hierarchical labels use same types as sheet pins)
        valid_types = ["input", "output", "bidirectional", "tri_state", "passive"]
        if label_type not in valid_types:
            return {
                "success": False,
                "message": f"Invalid label_type '{label_type}'. Valid types: {valid_types}",
                "valid_types": valid_types
            }
        
        # Add the hierarchical label
        from ..core.types import HierarchicalLabelShape
        
        # Map string types to enum
        shape_map = {
            "input": HierarchicalLabelShape.INPUT,
            "output": HierarchicalLabelShape.OUTPUT, 
            "bidirectional": HierarchicalLabelShape.BIDIRECTIONAL,
            "tri_state": HierarchicalLabelShape.TRISTATE,
            "passive": HierarchicalLabelShape.PASSIVE
        }
        
        label_uuid = state.current_schematic.add_hierarchical_label(
            text=text,
            position=position,
            shape=shape_map[label_type],
            rotation=rotation,
            size=size
        )
        
        return {
            "success": True,
            "message": f"Added hierarchical label '{text}' ({label_type}) at {position}",
            "label_uuid": label_uuid,
            "text": text,
            "label_type": label_type,
            "position": position,
            "help": "This label connects to a matching sheet pin in the parent schematic"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding hierarchical label: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

@mcp.tool()
def list_hierarchical_sheets() -> Dict[str, Any]:
    """List all hierarchical sheets in the current schematic."""
    try:
        if not state.is_loaded():
            return {
                "success": False,
                "message": "No schematic loaded"
            }
        
        sheets_data = state.current_schematic._data.get("sheets", [])
        
        sheets = []
        for sheet_data in sheets_data:
            sheet_info = {
                "uuid": sheet_data.get("uuid"),
                "name": sheet_data.get("name"),
                "filename": sheet_data.get("filename"),
                "position": [sheet_data.get("position", {}).get("x", 0), 
                           sheet_data.get("position", {}).get("y", 0)],
                "size": [sheet_data.get("size", {}).get("width", 0),
                        sheet_data.get("size", {}).get("height", 0)],
                "pin_count": len(sheet_data.get("pins", [])),
                "pins": [
                    {
                        "uuid": pin.get("uuid"),
                        "name": pin.get("name"),
                        "pin_type": pin.get("pin_type"),
                        "position": [pin.get("position", {}).get("x", 0),
                                   pin.get("position", {}).get("y", 0)]
                    }
                    for pin in sheet_data.get("pins", [])
                ]
            }
            sheets.append(sheet_info)
        
        return {
            "success": True,
            "sheets": sheets,
            "count": len(sheets),
            "message": f"Found {len(sheets)} hierarchical sheets"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing hierarchical sheets: {str(e)}",
            "errorDetails": traceback.format_exc()
        }

def _suggest_common_footprints(symbol) -> List[str]:
    """Suggest common footprints for a component type using SymbolDefinition."""
    return _suggest_common_footprints_by_prefix(symbol.reference_prefix.upper())

def _suggest_common_footprints_by_prefix(prefix: str) -> List[str]:
    """Suggest common footprints based on reference prefix."""
    footprint_map = {
        "R": ["Resistor_SMD:R_0603_1608Metric", "Resistor_SMD:R_0805_2012Metric", "Resistor_SMD:R_1206_3216Metric"],
        "C": ["Capacitor_SMD:C_0603_1608Metric", "Capacitor_SMD:C_0805_2012Metric", "Capacitor_SMD:C_1206_3216Metric"],
        "L": ["Inductor_SMD:L_0603_1608Metric", "Inductor_SMD:L_0805_2012Metric"],
        "D": ["Diode_SMD:D_SOD-323", "Diode_SMD:D_0603_1608Metric"],
        "LED": ["LED_SMD:LED_0603_1608Metric", "LED_SMD:LED_0805_2012Metric"],
        "Q": ["Package_TO_SOT_SMD:SOT-23", "Package_TO_SOT_SMD:SOT-23-3"],
        "U": ["Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm"],
        "J": ["Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"]
    }
    
    return footprint_map.get(prefix.upper(), ["Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"])

def _get_usage_context(symbol) -> str:
    """Get basic usage context for a component using SymbolDefinition."""
    return _get_usage_context_by_prefix(symbol.reference_prefix.upper())

def _get_usage_context_by_prefix(prefix: str) -> str:
    """Get basic usage context based on reference prefix."""
    context_map = {
        "R": "Use R_0603 for <0.1W signals, R_0805 for 0.1-0.25W power",
        "C": "Use 0603 for <10μF ceramic, 0805 for 10-100μF, larger for >100μF",
        "L": "Use 0603 for <1μH, 0805 for 1-10μH, larger for >10μH",
        "D": "Use SOD-323 for signal diodes, larger packages for power applications",
        "LED": "Use 0603 for indicators, 0805+ for higher current applications",
        "Q": "Use SOT-23 for small signal, larger packages for power switching",
        "U": "Choose package based on pin count and thermal requirements",
        "J": "Select connector based on current rating and mechanical requirements"
    }
    
    return context_map.get(prefix.upper(), "Select package based on electrical and mechanical requirements")

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

@mcp.resource("kicad://components/common-resistors")
def get_common_resistors() -> str:
    """Common resistor components with standard footprints."""
    return """# Common Resistors

## Standard Values (E12 Series)
- Device:R with values: 1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2
- Multiply by: 1Ω, 10Ω, 100Ω, 1kΩ, 10kΩ, 100kΩ, 1MΩ

## Recommended Footprints
- **R_0603_1608Metric**: For <0.1W applications (most common)
- **R_0805_2012Metric**: For 0.1-0.25W applications  
- **R_1206_3216Metric**: For 0.25-0.5W applications

## Common Usage
```python
# Example usage:
add_component("Device:R", "R1", "10k", (100, 100), footprint="Resistor_SMD:R_0603_1608Metric")
```

## Popular Values
- 10kΩ (pull-up resistors)
- 1kΩ (current limiting)  
- 100Ω (series termination)
- 4.7kΩ (I2C pull-up)
"""

@mcp.resource("kicad://components/common-capacitors") 
def get_common_capacitors() -> str:
    """Common capacitor components with standard footprints."""
    return """# Common Capacitors

## Ceramic Capacitors (Device:C)
- Values: 1pF-10µF typical range
- Common: 100nF (0.1µF), 1µF, 10µF, 22µF

## Recommended Footprints  
- **C_0603_1608Metric**: For <10µF ceramic (most common)
- **C_0805_2012Metric**: For 10µF-100µF ceramic
- **C_1206_3216Metric**: For >100µF ceramic

## Electrolytic Capacitors (Device:CP)
- Values: 1µF-1000µF+ for bulk storage
- Common: 10µF, 100µF, 470µF

## Common Usage
```python
# Decoupling capacitor
add_component("Device:C", "C1", "100n", (50, 50), footprint="Capacitor_SMD:C_0603_1608Metric")

# Power supply bulk capacitor  
add_component("Device:CP", "C2", "100u", (75, 75), footprint="Capacitor_SMD:C_0805_2012Metric")
```

## Popular Applications
- 100nF: MCU decoupling
- 1µF: Voltage regulator input/output  
- 10µF: Power supply filtering
"""

@mcp.resource("kicad://components/common-ics")
def get_common_ics() -> str:
    """Common integrated circuit components and packages.""" 
    return """# Common ICs

## Voltage Regulators
- **Regulator_Linear:AMS1117-3.3**: 3.3V LDO regulator
  - Footprint: Package_TO_SOT_SMD:SOT-223-3_TabPin2
- **Regulator_Linear:LM7805_TO220**: 5V linear regulator  
  - Footprint: Package_TO_SOT_THT:TO-220-3_Vertical

## Op-Amps
- **Amplifier_Operational:LM358**: Dual op-amp
  - Footprint: Package_SO:SOIC-8_3.9x4.9mm_P1.27mm
- **Amplifier_Operational:TL072**: JFET input dual op-amp
  - Footprint: Package_DIP:DIP-8_W7.62mm

## Microcontrollers  
- **MCU_ST_STM32F4:STM32F401RETx**: ARM Cortex-M4 MCU
  - Footprint: Package_QFP:LQFP-64_10x10mm_P0.5mm
- **MCU_Microchip_ATmega:ATmega328P-PU**: Arduino-compatible MCU
  - Footprint: Package_DIP:DIP-28_W15.24mm

## Common Usage
```python
# 3.3V regulator
add_component("Regulator_Linear:AMS1117-3.3", "U1", "AMS1117", (100, 100), 
              footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2")
```
"""

@mcp.resource("kicad://footprints/common-packages")
def get_common_packages() -> str:
    """Common footprint packages and their applications."""
    return """# Common Footprint Packages

## Surface Mount Packages

### Resistors & Capacitors
- **0603 (1608 Metric)**: 1.6mm x 0.8mm - Most common for passives
- **0805 (2012 Metric)**: 2.0mm x 1.2mm - Easier hand soldering
- **1206 (3216 Metric)**: 3.2mm x 1.6mm - Higher power rating

### ICs
- **SOIC-8**: 8-pin small outline package - common op-amps
- **SOT-23**: 3-pin small outline transistor package
- **SOT-223**: Power regulator package with tab
- **LQFP-64**: 64-pin low-profile quad flat pack - microcontrollers
- **QFN-16**: 16-pin quad flat no-lead package - compact ICs

## Through-Hole Packages

### Resistors & Capacitors  
- **Axial_DIN0207**: Standard through-hole resistor
- **Radial_D5.0mm**: Through-hole capacitor, 5mm diameter

### ICs
- **DIP-8**: 8-pin dual in-line package - breadboard friendly
- **TO-220**: Power transistor/regulator package

## Package Selection Guide
- Use 0603 for most SMD passives (good balance of size vs assemblability)
- Use SOIC over TSSOP for easier hand assembly  
- Use through-hole (DIP/TO-220) for prototyping and high power
- Use QFN/BGA only when density is critical
"""

@mcp.resource("kicad://circuits/common-patterns")
def get_common_patterns() -> str:
    """Common circuit patterns and component combinations."""
    return """# Common Circuit Patterns

## Voltage Divider
```python
# R1 and R2 create voltage divider: Vout = Vin * R2/(R1+R2)
add_component("Device:R", "R1", "10k", (100, 100))  # Top resistor
add_component("Device:R", "R2", "10k", (100, 120))  # Bottom resistor  
add_wire((100, 110), (100, 120))  # Connect R1 pin2 to R2 pin1
```

## MCU Decoupling
```python
# Always add 100nF ceramic cap near MCU power pins
add_component("Device:C", "C1", "100n", (mcu_x + 5, mcu_y))
# Add bulk capacitor nearby
add_component("Device:C", "C2", "10u", (mcu_x + 10, mcu_y))
```

## LED Current Limiting  
```python
# LED with current limiting resistor
add_component("Device:LED", "D1", "LED", (50, 50))
add_component("Device:R", "R1", "330", (50, 70))  # ~10mA @ 3.3V
add_wire((50, 60), (50, 70))  # Connect LED cathode to resistor
```

## Pull-up Resistor
```python  
# I2C or digital input pull-up
add_component("Device:R", "R1", "4k7", (100, 100))  # 4.7kΩ standard for I2C
add_component("Device:R", "R2", "10k", (120, 100))  # 10kΩ standard for digital
```

## Voltage Regulator Circuit
```python
# Linear regulator with input/output capacitors
add_component("Regulator_Linear:AMS1117-3.3", "U1", "AMS1117", (100, 100))
add_component("Device:C", "C1", "10u", (80, 100))   # Input cap  
add_component("Device:C", "C2", "10u", (120, 100))  # Output cap
add_component("Device:C", "C3", "100n", (120, 110)) # Fast decoupling
```
"""

@mcp.prompt()
def how_to_use_kicad_mcp() -> str:
    """Learn how to use the KiCAD Schematic MCP Server effectively."""
    return """# How to Use KiCAD Schematic MCP Server

## Getting Started

### 1. Create a New Schematic
```
Create a new schematic called "MyCircuit"
```

### 2. Search for Components  
```
Search for resistor components
Search for components in the Device library
Find STM32 microcontrollers
```

### 3. Add Components
```
Add a 10kΩ resistor at position (100, 100) with reference R1
Add a 100nF capacitor next to the resistor
Add an LED with a current limiting resistor
```

### 4. Connect Components
```
Connect the resistor R1 pin 1 to the capacitor C1 pin 1
Add a wire from (100, 100) to (120, 100)
```

### 5. Save Your Work
```
Save the schematic to "MyCircuit.kicad_sch"
```

## Pro Tips

### Component Discovery
- Use `search_components("resistor")` to find available resistor symbols
- Use `validate_component("Device:R")` to check if a component exists
- Use `list_libraries()` to see all available symbol libraries

### Common Components
- **Device:R** - Generic resistor (use with values like "10k", "1M") 
- **Device:C** - Generic ceramic capacitor
- **Device:LED** - Light emitting diode
- **power:GND** - Ground symbol
- **power:+3V3** - 3.3V power symbol

### Hierarchical Design Tools
For complex multi-sheet designs:
- `add_hierarchical_sheet("Sheet Name", "filename.kicad_sch", position, size)` - Create hierarchical sheet
- `add_sheet_pin(sheet_uuid, "NET_NAME", "input/output/bidirectional", position)` - Add sheet pin
- `add_hierarchical_label("NET_NAME", position, "input/output/bidirectional")` - Connect to parent sheet
- `list_hierarchical_sheets()` - Show all sheets and their pins

### Footprint Selection
The server suggests appropriate footprints for each component:
- Resistors: R_0603_1608Metric (most common)
- Capacitors: C_0603_1608Metric (for <10µF)
- ICs: Package varies by pin count and thermal needs

### Best Practices
1. Always search for components before adding them
2. Use standard component values (E12 series for resistors)
3. Add decoupling capacitors near ICs
4. Use proper footprints for your assembly method
5. Validate your design before saving

The server will guide you with suggestions and error messages if components don't exist!
"""

@mcp.prompt()
def common_circuit_examples() -> str:
    """Examples of common circuits you can build with KiCAD MCP."""
    return """# Common Circuit Examples

## 1. Simple LED Blinker
Create a basic LED circuit with current limiting:
```
Create a new schematic called "LED_Blinker"
Add an LED at position (100, 100) 
Add a 330Ω resistor at position (100, 80) for current limiting
Connect the LED anode to one end of the resistor
Add power and ground symbols
Save the schematic
```

## 2. Voltage Divider
Build a voltage divider for level shifting:
```
Add two 10kΩ resistors in series
Connect them to create Vout = Vin/2
Add input and output connectors
```

## 3. MCU Power Supply
Design power conditioning for a microcontroller:
```  
Add a 3.3V voltage regulator (AMS1117-3.3)
Add 10µF input and output capacitors
Add 100nF decoupling capacitors  
Connect ground plane
```

## 4. I2C Pull-up Network
Create proper I2C bus conditioning:
```
Add 4.7kΩ pull-up resistors for SDA and SCL lines
Connect to 3.3V supply
Add I2C connector
```

## 5. Crystal Oscillator Circuit
Build timing reference for MCU:
```
Add crystal oscillator component
Add two 22pF load capacitors to ground
Connect to MCU clock inputs
```

Each example includes component selection, footprint recommendations, and connection guidance!
"""

@mcp.resource("kicad://hierarchy/workflow-guide")
def get_hierarchical_workflow() -> str:
    """Guide for creating hierarchical schematics with multiple sheets."""
    return """# Hierarchical Schematic Workflow

## Overview
Hierarchical schematics organize complex designs into multiple sheets for better readability and modularity. Each hierarchical sheet represents a functional block.

## Step 1: Plan Your Hierarchy
Break your design into logical functional blocks:
- Power Supply
- MCU Core  
- Communication (USB, WiFi, etc.)
- Analog Frontend
- LED Driver
- Debug/Programming Interface

## Step 2: Create Main Schematic
Start with the top-level schematic that shows the overall system architecture:

```python
# Create main schematic
create_schematic("Main_Board")

# Add hierarchical sheets for each subsystem
add_hierarchical_sheet("Power Supply", "power.kicad_sch", (50, 50), (50, 30))
add_hierarchical_sheet("MCU Core", "mcu.kicad_sch", (120, 50), (60, 40)) 
add_hierarchical_sheet("USB Interface", "usb.kicad_sch", (200, 50), (40, 25))
```

## Step 3: Add Sheet Pins
Connect hierarchical sheets by adding pins for signals that cross sheet boundaries:

```python
# Get sheet UUID from add_hierarchical_sheet() return value
power_sheet_uuid = "sheet-uuid-from-previous-call"

# Add power output pins to power supply sheet
add_sheet_pin(power_sheet_uuid, "3V3", "output", (50, 5))
add_sheet_pin(power_sheet_uuid, "5V", "output", (50, 10)) 
add_sheet_pin(power_sheet_uuid, "GND", "passive", (50, 15))

# Add power input pins to MCU sheet  
mcu_sheet_uuid = "mcu-sheet-uuid"
add_sheet_pin(mcu_sheet_uuid, "3V3", "input", (0, 5))
add_sheet_pin(mcu_sheet_uuid, "GND", "passive", (0, 10))

# Add communication signals between MCU and USB
add_sheet_pin(mcu_sheet_uuid, "USB_DP", "bidirectional", (60, 20))
add_sheet_pin(mcu_sheet_uuid, "USB_DN", "bidirectional", (60, 25))
```

## Step 4: Connect Sheet Pins with Wires
Wire the sheet pins together on the main schematic:

```python
# Connect power distribution
add_wire((100, 55), (120, 55))  # 3V3: Power sheet output to MCU sheet input
add_wire((100, 60), (120, 60))  # GND: Power sheet to MCU sheet

# Connect USB signals
add_wire((180, 70), (200, 70))  # USB_DP: MCU to USB sheet
add_wire((180, 75), (200, 75))  # USB_DN: MCU to USB sheet
```

## Step 5: Create Child Schematics
Create separate schematic files for each hierarchical sheet:

```python
# Create power supply schematic
create_schematic("Power_Supply") 
save_schematic("power.kicad_sch")

# Add hierarchical labels that match the sheet pins
add_hierarchical_label("3V3", (150, 50), "output")
add_hierarchical_label("5V", (150, 60), "output")
add_hierarchical_label("GND", (150, 70), "passive")

# Add actual power supply components
add_component("Regulator_Linear:AMS1117-3.3", "U1", "AMS1117", (100, 60))
# ... more components
```

## Pin Type Guidelines

**Input**: Signal flows into the sheet (power inputs, control signals)
**Output**: Signal flows out of the sheet (power outputs, status signals)  
**Bidirectional**: Signal flows both ways (I2C, SPI data lines)
**Tri-state**: Three-state signals (data buses with enable)
**Passive**: Non-directional connections (ground, analog signals)

## Best Practices

1. **Consistent Naming**: Use the same net names for sheet pins and hierarchical labels
2. **Logical Grouping**: Group related signals together on sheet edges
3. **Clear Pin Types**: Use correct pin types for signal direction
4. **Good Placement**: Position sheet pins at logical connection points
5. **Documentation**: Add descriptive names and organize sheets clearly

## Common Patterns

### Power Distribution
```python
# Power sheet outputs
add_sheet_pin(power_uuid, "3V3", "output", (50, 5))
add_sheet_pin(power_uuid, "GND", "passive", (50, 30))

# Consumer sheet inputs  
add_sheet_pin(mcu_uuid, "3V3", "input", (0, 5))
add_sheet_pin(mcu_uuid, "GND", "passive", (0, 30))
```

### Communication Bus
```python  
# MCU sheet (bus master)
add_sheet_pin(mcu_uuid, "I2C_SCL", "output", (60, 10))
add_sheet_pin(mcu_uuid, "I2C_SDA", "bidirectional", (60, 15))

# Sensor sheet (bus slave)
add_sheet_pin(sensor_uuid, "I2C_SCL", "input", (0, 10)) 
add_sheet_pin(sensor_uuid, "I2C_SDA", "bidirectional", (0, 15))
```

This hierarchical approach makes complex designs manageable and promotes reusable functional blocks.
"""

def main():
    """Run the MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="KiCAD Schematic MCP Server")
    parser.add_argument('--test', action='store_true', help='Run quick test and exit')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--status', action='store_true', help='Show server status and exit')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    if args.version:
        print("KiCAD Schematic MCP Server v0.1.1")
        return
    
    if args.status:
        print("KiCAD Schematic MCP Server Status:")
        print(f"  Component discovery: {len(get_search_index().get_categories()) if get_search_index() else 0} categories")
        print(f"  Symbol cache: {get_symbol_cache().get_performance_stats()['total_symbols_cached']} symbols")
        print("  Status: Ready")
        return
    
    if args.test:
        logger.info("Running MCP server test...")
        try:
            # Quick initialization test
            ensure_index_built()
            cache = get_symbol_cache()
            stats = cache.get_performance_stats()
            print(f"✅ Test passed: {stats['total_symbols_cached']} symbols, {len(get_search_index().get_categories())} categories")
            return
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)
    
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