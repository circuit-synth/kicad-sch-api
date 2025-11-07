"""
Pydantic models for MCP server API responses.

Provides type-safe data models for MCP tools that interact with the schematic API,
ensuring consistent serialization and validation across all endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PointModel(BaseModel):
    """2D point coordinates."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"x": 100.0, "y": 100.0},
            "description": "Position in KiCAD schematic coordinates",
        }
    )

    x: float = Field(..., description="X coordinate in mm")
    y: float = Field(..., description="Y coordinate in mm")


class PinInfoOutput(BaseModel):
    """
    Complete pin information for MCP clients.

    Provides comprehensive pin metadata including position, electrical type,
    graphical representation, and unique identification.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "number": "1",
                "name": "~",
                "position": {"x": 100.33, "y": 104.14},
                "electrical_type": "passive",
                "shape": "line",
                "length": 2.54,
                "orientation": 0.0,
                "uuid": "1f8ab1be-1ad8-469d-8ba9-667910bdee9e:1",
            }
        }
    )

    number: str = Field(
        ...,
        description="Pin number or designator (e.g., '1', '2', 'A1')",
        examples=["1", "2", "A1", "CLK"],
    )
    name: str = Field(
        ...,
        description="Pin name or signal designation (e.g., 'VCC', 'GND', 'CLK')",
        examples=["VCC", "GND", "CLK", "D0"],
    )
    position: PointModel = Field(
        ...,
        description="Absolute position in schematic coordinates (mm), "
        "accounting for component rotation and mirroring",
    )
    electrical_type: str = Field(
        ...,
        description="Pin electrical type (input, output, passive, power_in, power_out, bidirectional, etc.)",
        examples=["passive", "input", "output", "power_in", "power_out"],
    )
    shape: str = Field(
        ...,
        description="Pin graphical shape (line, inverted, clock, inverted_clock, input_low, etc.)",
        examples=["line", "inverted", "clock"],
    )
    length: float = Field(
        ...,
        description="Pin length in mm (typically 2.54 for standard pins)",
        examples=[2.54],
    )
    orientation: float = Field(
        ...,
        description="Pin orientation in degrees (0, 90, 180, or 270)",
        examples=[0.0, 90.0, 180.0, 270.0],
    )
    uuid: str = Field(
        ...,
        description="Unique identifier for this pin instance (composite: component_uuid:pin_number)",
        examples=["1f8ab1be-1ad8-469d-8ba9-667910bdee9e:1"],
    )


class ComponentPinsOutput(BaseModel):
    """
    Output model for get_component_pins MCP tool.

    Returns all pins for a specified component with complete metadata.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reference": "R1",
                "lib_id": "Device:R",
                "pins": [
                    {
                        "number": "1",
                        "name": "~",
                        "position": {"x": 100.33, "y": 104.14},
                        "electrical_type": "passive",
                        "shape": "line",
                        "length": 2.54,
                        "orientation": 0.0,
                        "uuid": "1f8ab1be-1ad8-469d-8ba9-667910bdee9e:1",
                    },
                    {
                        "number": "2",
                        "name": "~",
                        "position": {"x": 100.33, "y": 95.86},
                        "electrical_type": "passive",
                        "shape": "line",
                        "length": 2.54,
                        "orientation": 0.0,
                        "uuid": "1f8ab1be-1ad8-469d-8ba9-667910bdee9e:2",
                    },
                ],
                "pin_count": 2,
                "success": True,
            }
        }
    )

    reference: str = Field(
        ...,
        description="Component reference designator (e.g., 'R1', 'U2', 'C1')",
        examples=["R1", "U2", "C1"],
    )
    lib_id: str = Field(
        ...,
        description="Library identifier (e.g., 'Device:R', 'Amplifier_Operational:TL072')",
        examples=["Device:R", "Amplifier_Operational:TL072", "LED:LED"],
    )
    pins: List[PinInfoOutput] = Field(
        ...,
        description="List of all pins for this component with complete metadata",
    )
    pin_count: int = Field(
        ...,
        description="Total number of pins",
        examples=[2, 8, 14, 48],
    )
    success: bool = Field(
        default=True,
        description="Whether the operation was successful",
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional message or error description",
    )


class ComponentInfoOutput(BaseModel):
    """
    Component information output model.

    Provides comprehensive component metadata including position, properties,
    and unique identification.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reference": "R1",
                "lib_id": "Device:R",
                "value": "10k",
                "position": {"x": 100.0, "y": 100.0},
                "rotation": 0.0,
                "footprint": "Resistor_SMD:R_0603_1608Metric",
                "uuid": "1f8ab1be-1ad8-469d-8ba9-667910bdee9e",
                "success": True,
            }
        }
    )

    reference: str = Field(
        ...,
        description="Component reference designator (e.g., 'R1', 'U2', 'C1')",
        examples=["R1", "U2", "C1"],
    )
    lib_id: str = Field(
        ...,
        description="Library identifier (e.g., 'Device:R', 'Amplifier_Operational:TL072')",
        examples=["Device:R", "Amplifier_Operational:TL072", "LED:LED"],
    )
    value: str = Field(
        ...,
        description="Component value or part description",
        examples=["10k", "100nF", "TL072"],
    )
    position: PointModel = Field(
        ...,
        description="Component position in schematic coordinates (mm)",
    )
    rotation: float = Field(
        ...,
        description="Component rotation in degrees (0, 90, 180, or 270)",
        examples=[0.0, 90.0, 180.0, 270.0],
    )
    footprint: Optional[str] = Field(
        default=None,
        description="PCB footprint identifier",
        examples=["Resistor_SMD:R_0603_1608Metric", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"],
    )
    uuid: str = Field(
        ...,
        description="Unique identifier for this component instance",
        examples=["1f8ab1be-1ad8-469d-8ba9-667910bdee9e"],
    )
    success: bool = Field(
        default=True,
        description="Whether the operation was successful",
    )
    message: Optional[str] = Field(
        default=None,
        description="Optional message or error description",
    )


class ErrorOutput(BaseModel):
    """Standard error response model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "COMPONENT_NOT_FOUND",
                "message": "Component 'R999' not found in schematic",
            }
        }
    )

    success: bool = Field(
        default=False,
        description="Operation success status",
    )
    error: str = Field(
        ...,
        description="Error type or code",
        examples=["COMPONENT_NOT_FOUND", "LIBRARY_ERROR"],
    )
    message: str = Field(
        ...,
        description="Detailed error message",
    )
