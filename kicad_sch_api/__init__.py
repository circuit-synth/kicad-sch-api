"""
kicad-sch-api: Professional KiCAD Schematic Manipulation Library

A modern, high-performance Python library for programmatic manipulation of KiCAD schematic files
with exact format preservation, advanced component management, and AI agent integration.

Key Features:
- Exact format preservation (output matches KiCAD exactly)
- Enhanced object model with intuitive API
- Symbol library caching and management
- Multi-source component intelligence
- Native MCP server for AI agent integration
- Professional error handling and validation

Basic Usage:
    import kicad_sch_api as ksa

    # Load schematic
    sch = ksa.Schematic('my_circuit.kicad_sch')

    # Add components
    resistor = sch.components.add('Device:R', ref='R1', value='10k', pos=(100, 100))

    # Modify properties
    resistor.footprint = 'Resistor_SMD:R_0603_1608Metric'

    # Save with exact format preservation
    sch.save()

Advanced Usage:
    # Bulk operations
    resistors = sch.components.filter(lib_id='Device:R')
    for r in resistors:
        r.properties['Tolerance'] = '1%'

    # Library management
    sch.libraries.add_path('/path/to/custom/symbols.kicad_sym')

    # Validation
    issues = sch.validate()
    if issues:
        print(f"Found {len(issues)} validation issues")
"""

__version__ = "0.4.2"
__author__ = "Circuit-Synth"
__email__ = "info@circuit-synth.com"

from .core.components import Component, ComponentCollection
from .core.config import KiCADConfig, config

# Core imports for public API
from .core.schematic import Schematic
from .library.cache import SymbolLibraryCache, get_symbol_cache
from .utils.validation import ValidationError, ValidationIssue

# Version info
VERSION_INFO = (0, 4, 0)

# Public API
__all__ = [
    # Core classes
    "Schematic",
    "Component",
    "ComponentCollection",
    "SymbolLibraryCache",
    "get_symbol_cache",
    # Configuration
    "KiCADConfig",
    "config",
    # Exceptions
    "ValidationError",
    "ValidationIssue",
    # Version info
    "__version__",
    "VERSION_INFO",
]


# Convenience functions
def load_schematic(file_path: str) -> "Schematic":
    """
    Load a KiCAD schematic file.

    Args:
        file_path: Path to .kicad_sch file

    Returns:
        Schematic object for manipulation

    Example:
        >>> sch = ksa.load_schematic('my_circuit.kicad_sch')
        >>> print(f"Loaded {len(sch.components)} components")
    """
    return Schematic.load(file_path)


def create_schematic(name: str = "Untitled") -> "Schematic":
    """
    Create a new empty schematic.

    Args:
        name: Optional schematic name

    Returns:
        New empty Schematic object

    Example:
        >>> sch = ksa.create_schematic("My New Circuit")
        >>> sch.components.add('Device:R', 'R1', '10k')
    """
    return Schematic.create(name)


# Add convenience functions to __all__
__all__.extend(["load_schematic", "create_schematic"])
