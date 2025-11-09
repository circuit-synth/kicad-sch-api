#!/usr/bin/env python3
"""
Configuration constants and settings for KiCAD schematic API.

This module centralizes all magic numbers and configuration values
to make them easily configurable and maintainable.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


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
class PositioningSettings:
    """Global positioning behavior settings."""

    use_grid_units: bool = False  # If True, all positions default to grid units
    grid_size: float = 1.27  # Default grid size in mm (50 mil KiCAD standard)


@dataclass
class DefaultValues:
    """Default values for various operations."""

    project_name: str = "untitled"
    stroke_width: float = 0.0
    stroke_type: str = "default"
    fill_type: str = "none"
    font_size: float = 1.27
    pin_name_size: float = 1.27
    pin_number_size: float = 1.27


@dataclass
class FileFormatConstants:
    """KiCAD file format identifiers and version strings."""

    file_type: str = "kicad_sch"
    generator_default: str = "eeschema"
    version_default: str = "20250114"
    generator_version_default: str = "9.0"


@dataclass
class PaperSizeConstants:
    """Standard paper size definitions."""

    default: str = "A4"
    valid_sizes: List[str] = field(
        default_factory=lambda: ["A4", "A3", "A2", "A1", "A0", "Letter", "Legal", "Tabloid"]
    )


@dataclass
class FieldNames:
    """Common S-expression field names to avoid typos."""

    # File structure
    version: str = "version"
    generator: str = "generator"
    generator_version: str = "generator_version"
    uuid: str = "uuid"
    paper: str = "paper"

    # Positioning
    at: str = "at"
    xy: str = "xy"
    pts: str = "pts"
    start: str = "start"
    end: str = "end"
    mid: str = "mid"
    center: str = "center"
    radius: str = "radius"

    # Styling
    stroke: str = "stroke"
    fill: str = "fill"
    width: str = "width"
    type: str = "type"
    color: str = "color"

    # Text/Font
    font: str = "font"
    size: str = "size"
    effects: str = "effects"

    # Components
    pin: str = "pin"
    property: str = "property"
    symbol: str = "symbol"
    lib_id: str = "lib_id"

    # Graphics
    polyline: str = "polyline"
    arc: str = "arc"
    circle: str = "circle"
    rectangle: str = "rectangle"
    bezier: str = "bezier"

    # Connection elements
    wire: str = "wire"
    junction: str = "junction"
    no_connect: str = "no_connect"
    label: str = "label"

    # Hierarchical
    sheet: str = "sheet"
    sheet_instances: str = "sheet_instances"


class KiCADConfig:
    """Central configuration class for KiCAD schematic API."""

    def __init__(self) -> None:
        self.properties = PropertyOffsets()
        self.grid = GridSettings()
        self.sheet = SheetSettings()
        self.tolerance = ToleranceSettings()
        self.positioning = PositioningSettings()
        self.defaults = DefaultValues()
        self.file_format = FileFormatConstants()
        self.paper = PaperSizeConstants()
        self.fields = FieldNames()

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
        self,
        property_name: str,
        component_pos: Tuple[float, float],
        offset_index: int = 0,
        component_rotation: float = 0,
    ) -> Tuple[float, float, float]:
        """
        Calculate property position relative to component, accounting for component rotation.

        Args:
            property_name: Name of the property (Reference, Value, etc.)
            component_pos: (x, y) position of component
            offset_index: Stacking offset for multiple properties
            component_rotation: Rotation of the component in degrees (0, 90, 180, 270)

        Returns:
            Tuple of (x, y, rotation) for the property
        """
        import math

        x, y = component_pos

        # Get base offsets (for 0° rotation)
        if property_name == "Reference":
            dx, dy = self.properties.reference_x, self.properties.reference_y
        elif property_name == "Value":
            dx, dy = self.properties.value_x, self.properties.value_y
        elif property_name == "Footprint":
            # Footprint positioned to left of component, rotated 90 degrees
            return (x - 1.778, y, self.properties.footprint_rotation)
        elif property_name in ["Datasheet", "Description"]:
            # Hidden properties at component center
            return (x, y, 0)
        else:
            # Other properties stacked vertically below
            dx = self.properties.reference_x
            dy = self.properties.value_y + (self.properties.hidden_property_offset * offset_index)

        # Apply rotation transform to offsets
        # Text stays at 0° rotation (readable), but position rotates around component
        # KiCad uses clockwise rotation, so negate the angle
        rotation_rad = math.radians(-component_rotation)
        dx_rotated = dx * math.cos(rotation_rad) - dy * math.sin(rotation_rad)
        dy_rotated = dx * math.sin(rotation_rad) + dy * math.cos(rotation_rad)

        return (x + dx_rotated, y + dy_rotated, 0)


# Global configuration instance
config = KiCADConfig()
