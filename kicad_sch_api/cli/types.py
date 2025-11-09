"""Type definitions for KiCad CLI operations."""

from typing import Literal

# Netlist export formats
NetlistFormat = Literal[
    "kicadsexpr",  # KiCad S-expression netlist (default)
    "kicadxml",  # KiCad XML netlist
    "cadstar",  # Cadstar format
    "orcadpcb2",  # OrCAD PCB2 format
    "spice",  # SPICE netlist
    "spicemodel",  # SPICE with models
    "pads",  # PADS format
    "allegro",  # Allegro format
]

# ERC (Electrical Rule Check) formats
ErcFormat = Literal[
    "json",  # JSON format (machine-readable)
    "report",  # Human-readable text report
]

# ERC severity levels
ErcSeverity = Literal[
    "all",  # Report all violations
    "error",  # Error level only
    "warning",  # Warning level only
    "exclusions",  # Excluded violations only
]

# Units for measurements
Units = Literal[
    "mm",  # Millimeters (default)
    "in",  # Inches
    "mils",  # Mils (1/1000 inch)
]

# Execution modes
ExecutionMode = Literal[
    "auto",  # Auto-detect (try local, fall back to Docker)
    "local",  # Force local kicad-cli
    "docker",  # Force Docker mode
]
