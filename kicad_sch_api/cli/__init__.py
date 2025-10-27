"""
KiCad CLI wrappers for schematic operations.

This module provides Python wrappers around kicad-cli commands with automatic
fallback to Docker when kicad-cli is not installed locally.

Supported operations:
- ERC (Electrical Rule Check)
- Netlist export (8 formats)
- BOM (Bill of Materials) export
- PDF export
- SVG export
- DXF export

Example:
    >>> import kicad_sch_api as ksa
    >>> sch = ksa.Schematic('circuit.kicad_sch')
    >>> sch.run_erc()
    >>> sch.export_netlist(format='spice')
    >>> sch.export_bom(exclude_dnp=True)
"""

from kicad_sch_api.cli.base import (
    ExecutionMode,
    KiCadExecutor,
    get_executor_info,
    set_execution_mode,
)
from kicad_sch_api.cli.types import (
    ErcFormat,
    ErcSeverity,
    NetlistFormat,
    Units,
)

__all__ = [
    "KiCadExecutor",
    "ExecutionMode",
    "get_executor_info",
    "set_execution_mode",
    "NetlistFormat",
    "ErcFormat",
    "ErcSeverity",
    "Units",
]
