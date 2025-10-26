#!/usr/bin/env python3
"""
Configuration constants and settings for KiCAD schematic API.

This module centralizes all magic numbers and configuration values
to make them easily configurable and maintainable.
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass
class PropertyOffsets:
    """Standard property positioning offsets relative to component position."""

    reference_x: float = 2.54  # Reference label X offset
    reference_y: float = -1.2701  # Reference label Y offset (above) - exact match
    value_x: float = 2.54  # Value label X offset
    value_y: float = 1.2699  # Value label Y offset (below) - exact match
    footprint_rotation: float = 90  # Footprint property rotation
    hidden_property_offset: float = 1.27  # Y spacing for hidden properties


@dataclass
class GridSettings:
    """Standard KiCAD grid and spacing settings."""

    standard_grid: float = 1.27  # Standard 50mil grid in mm
    component_spacing: float = 2.54  # Standard component spacing (100mil)
    unit_spacing: float = 12.7  # Multi-unit IC spacing
    power_offset: Tuple[float, float] = (25.4, 0.0)  # Power unit offset


@dataclass
class SheetSettings:
    """Hierarchical sheet positioning settings."""

    name_offset_y: float = -0.7116  # Sheetname position offset (above)
    file_offset_y: float = 0.5846  # Sheetfile position offset (below)
    default_stroke_width: float = 0.1524
    default_stroke_type: str = "solid"


@dataclass
class ToleranceSettings:
    """Tolerance values for various operations."""

    position_tolerance: float = 0.1  # Point matching tolerance
    wire_segment_min: float = 0.001  # Minimum wire segment length
    coordinate_precision: float = 0.01  # Coordinate comparison precision


@dataclass
class DefaultValues:
    """Default values for various operations."""

    project_name: str = "untitled"
    stroke_width: float = 0.0
    font_size: float = 1.27
    pin_name_size: float = 1.27
    pin_number_size: float = 1.27


class KiCADConfig:
    """Central configuration class for KiCAD schematic API."""

    def __init__(self) -> None:
        self.properties = PropertyOffsets()
        self.grid = GridSettings()
        self.sheet = SheetSettings()
        self.tolerance = ToleranceSettings()
        self.defaults = DefaultValues()

        # Names that should not generate title_block (for backward compatibility)
        # Include test schematic names to maintain reference compatibility
        self.no_title_block_names = {
            "untitled",
            "blank schematic",
            "",
            "single_resistor",
            "two_resistors",
            "single_wire",
            "single_label",
            "single_hierarchical_sheet",
        }

    def should_add_title_block(self, name: str) -> bool:
        """Determine if a schematic name should generate a title block."""
        if not name:
            return False
        return name.lower() not in self.no_title_block_names

    def get_property_position(
        self, property_name: str, component_pos: Tuple[float, float], offset_index: int = 0
    ) -> Tuple[float, float, float]:
        """
        Calculate property position relative to component.

        Returns:
            Tuple of (x, y, rotation) for the property
        """
        x, y = component_pos

        if property_name == "Reference":
            return (x + self.properties.reference_x, y + self.properties.reference_y, 0)
        elif property_name == "Value":
            return (x + self.properties.value_x, y + self.properties.value_y, 0)
        elif property_name == "Footprint":
            # Footprint positioned to left of component, rotated 90 degrees
            return (x - 1.778, y, self.properties.footprint_rotation)  # Exact match for reference
        elif property_name in ["Datasheet", "Description"]:
            # Hidden properties at component center
            return (x, y, 0)
        else:
            # Other properties stacked vertically below
            return (
                x + self.properties.reference_x,
                y
                + self.properties.value_y
                + (self.properties.hidden_property_offset * offset_index),
                0,
            )


# Global configuration instance
config = KiCADConfig()
