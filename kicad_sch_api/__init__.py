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

__version__ = "0.5.1"
__author__ = "Circuit-Synth"
__email__ = "info@circuit-synth.com"

from .core.components import Component, ComponentCollection
from .core.config import KiCADConfig, config

# Commonly-used exceptions (ValidationError re-exported from utils for backward compat)
from .core.exceptions import (
    DuplicateElementError,
    ElementNotFoundError,
    KiCadSchError,
)

# Core imports for public API
from .core.schematic import Schematic
from .core.types import PinInfo
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
    "PinInfo",
    "SymbolLibraryCache",
    "get_symbol_cache",
    # Configuration
    "KiCADConfig",
    "config",
    # Exceptions
    "KiCadSchError",
    "ValidationError",
    "ValidationIssue",
    "ElementNotFoundError",
    "DuplicateElementError",
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


def schematic_to_python(
    input_path: str,
    output_path: str,
    template: str = "default",
    include_hierarchy: bool = True,
    format_code: bool = True,
    add_comments: bool = True,
):
    """
    Convert KiCad schematic to Python code (one-line convenience function).

    Loads a KiCad schematic and generates executable Python code that
    recreates it using the kicad-sch-api library.

    Args:
        input_path: Input .kicad_sch file
        output_path: Output .py file
        template: Code template style ('minimal', 'default', 'verbose', 'documented')
        include_hierarchy: Include hierarchical sheets
        format_code: Format code with Black
        add_comments: Add explanatory comments

    Returns:
        Path to generated Python file

    Raises:
        FileNotFoundError: If input file doesn't exist
        CodeGenerationError: If code generation fails

    Example:
        >>> import kicad_sch_api as ksa
        >>> ksa.schematic_to_python('input.kicad_sch', 'output.py')
        PosixPath('output.py')

        >>> ksa.schematic_to_python('input.kicad_sch', 'output.py',
        ...                         template='minimal',
        ...                         add_comments=False)
        PosixPath('output.py')
    """
    from pathlib import Path

    # Load schematic
    schematic = Schematic.load(input_path)

    # Export to Python
    return schematic.export_to_python(
        output_path=output_path,
        template=template,
        include_hierarchy=include_hierarchy,
        format_code=format_code,
        add_comments=add_comments,
    )


def use_grid_units(enabled: bool = True) -> None:
    """
    Enable or disable grid units for positioning.

    When enabled, all position values are interpreted as grid units
    (1 unit = 1.27mm, the standard KiCAD 50 mil grid).

    Args:
        enabled: If True, use grid units; if False, use millimeters

    Example:
        >>> import kicad_sch_api as ksa
        >>> ksa.use_grid_units(True)
        >>> sch = ksa.create_schematic("MyCircuit")
        >>> # Now positions are in grid units
        >>> sch.components.add('Device:R', 'R1', '10k', position=(20, 20))  # 25.4mm, 25.4mm
    """
    config.positioning.use_grid_units = enabled


# Add convenience functions to __all__
__all__.extend(["load_schematic", "create_schematic", "schematic_to_python", "use_grid_units"])
