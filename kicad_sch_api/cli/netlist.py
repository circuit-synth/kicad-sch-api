"""Netlist export functionality using kicad-cli."""

from pathlib import Path
from typing import Optional

from kicad_sch_api.cli.base import KiCadExecutor
from kicad_sch_api.cli.types import NetlistFormat


def export_netlist(
    schematic_path: Path,
    output_path: Optional[Path] = None,
    format: NetlistFormat = "kicadsexpr",
    executor: Optional[KiCadExecutor] = None,
) -> Path:
    """
    Export netlist from schematic using kicad-cli.

    Supports 8 different netlist formats for PCB layout and simulation.

    Args:
        schematic_path: Path to .kicad_sch file
        output_path: Output netlist path (auto-generated if None)
        format: Netlist format (see NetlistFormat for options)
        executor: Custom KiCadExecutor instance (creates default if None)

    Returns:
        Path to generated netlist file

    Raises:
        RuntimeError: If kicad-cli not found or netlist generation fails
        FileNotFoundError: If schematic file doesn't exist

    Example:
        >>> from pathlib import Path
        >>> netlist = export_netlist(
        ...     Path('circuit.kicad_sch'),
        ...     format='spice'
        ... )
        >>> print(f"Netlist: {netlist}")

    Supported formats:
        - kicadsexpr: KiCad S-expression netlist (default)
        - kicadxml: KiCad XML netlist
        - cadstar: Cadstar format
        - orcadpcb2: OrCAD PCB2 format
        - spice: SPICE netlist
        - spicemodel: SPICE with models
        - pads: PADS format
        - allegro: Allegro format
    """
    schematic_path = Path(schematic_path)

    if not schematic_path.exists():
        raise FileNotFoundError(f"Schematic not found: {schematic_path}")

    # Auto-generate output path if not provided
    if output_path is None:
        ext = _get_extension_for_format(format)
        output_path = schematic_path.with_suffix(ext)
    else:
        output_path = Path(output_path)

    # Create executor if not provided
    if executor is None:
        executor = KiCadExecutor()

    # Build command
    args = [
        "sch",
        "export",
        "netlist",
        "--format",
        format,
        "--output",
        str(output_path),
        str(schematic_path),
    ]

    # Execute command
    executor.run(args, cwd=schematic_path.parent)

    return output_path


def _get_extension_for_format(format: NetlistFormat) -> str:
    """Get file extension for netlist format."""
    extensions = {
        "kicadsexpr": ".net",
        "kicadxml": ".xml",
        "cadstar": ".frp",
        "orcadpcb2": ".net",
        "spice": ".cir",
        "spicemodel": ".cir",
        "pads": ".asc",
        "allegro": ".alg",
    }
    return extensions.get(format, ".net")
