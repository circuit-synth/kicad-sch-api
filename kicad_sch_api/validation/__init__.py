"""
Electrical Rules Check (ERC) validation module.

Provides comprehensive electrical validation for KiCAD schematics.
"""

from kicad_sch_api.validation.erc_models import (
    ERCViolation,
    ERCResult,
    ERCConfig,
)
from kicad_sch_api.validation.pin_matrix import (
    PinConflictMatrix,
    PinSeverity,
)
from kicad_sch_api.validation.erc import ElectricalRulesChecker

__all__ = [
    "ERCViolation",
    "ERCResult",
    "ERCConfig",
    "PinConflictMatrix",
    "PinSeverity",
    "ElectricalRulesChecker",
]
