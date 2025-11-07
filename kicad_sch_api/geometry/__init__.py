"""
Geometry module for KiCad schematic operations.

This module provides:
- Accurate bounding box calculations for KiCad symbols
- Orthogonal (Manhattan) routing for wire connections
- Font metrics and symbol geometry analysis

Migrated from circuit-synth to kicad-sch-api for better architectural separation.
"""

from .font_metrics import (
    DEFAULT_PIN_LENGTH,
    DEFAULT_PIN_NAME_OFFSET,
    DEFAULT_PIN_NUMBER_SIZE,
    DEFAULT_PIN_TEXT_WIDTH_RATIO,
    DEFAULT_TEXT_HEIGHT,
)
from .routing import (
    CornerDirection,
    RoutingResult,
    create_orthogonal_routing,
    validate_routing_result,
)
from .symbol_bbox import SymbolBoundingBoxCalculator

__all__ = [
    "SymbolBoundingBoxCalculator",
    "DEFAULT_TEXT_HEIGHT",
    "DEFAULT_PIN_LENGTH",
    "DEFAULT_PIN_NAME_OFFSET",
    "DEFAULT_PIN_NUMBER_SIZE",
    "DEFAULT_PIN_TEXT_WIDTH_RATIO",
    "CornerDirection",
    "RoutingResult",
    "create_orthogonal_routing",
    "validate_routing_result",
]
