#!/usr/bin/env python3
"""
Integration tests for MCP server functionality.

Tests the complete MCP server workflow including schematic management
and pin discovery tools.
"""

import logging
from pathlib import Path

import pytest
from mcp_server.tools.component_tools import (
    add_component,
    filter_components,
    list_components,
    remove_component,
    update_component,
)
from mcp_server.tools.connectivity_tools import (
    add_junction,
    add_label,
    add_wire,
)
from mcp_server.tools.pin_discovery import (
    find_pins_by_name,
    find_pins_by_type,
    get_component_pins,
    get_current_schematic,
    set_current_schematic,
)

import kicad_sch_api as ksa

logger = logging.getLogger(__name__)


class TestMCPSchematicManagement:
    """Test MCP schematic management functionality."""

    def test_create_and_set_schematic(self):
        """Test creating and setting current schematic."""
        # Create schematic
        sch = ksa.create_schematic("TestProject")

        # Set as current
        set_current_schematic(sch)

        # Verify it's set
        current = get_current_schematic()
        assert current is not None
        assert current.title_block["title"] == "TestProject"

    def test_clear_current_schematic(self):
        """Test clearing current schematic."""
        sch = ksa.create_schematic("TestProject")
        set_current_schematic(sch)

        # Clear by setting None
        set_current_schematic(None)

        current = get_current_schematic()
        assert current is None


class TestMCPGetComponentPins:
    """Test get_component_pins MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("PinTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_get_component_pins_success(self, setup_schematic):
        """Test successful pin retrieval."""
        sch = setup_schematic

        # Add component
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Get pins via MCP tool
        result = await get_component_pins("R1")

        assert result.success is True
        assert result.reference == "R1"
        assert result.lib_id == "Device:R"
        assert result.pin_count > 0
        assert len(result.pins) == result.pin_count

        # Verify pin structure
        for pin in result.pins:
            assert pin.number is not None
            assert pin.name is not None
            assert pin.position is not None
            assert pin.electrical_type is not None

    @pytest.mark.asyncio
    async def test_get_component_pins_component_not_found(self, setup_schematic):
        """Test error when component not found."""
        result = await get_component_pins("R999")

        assert result.success is False
        assert result.error == "COMPONENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_component_pins_no_schematic(self):
        """Test error when no schematic is loaded."""
        set_current_schematic(None)

        result = await get_component_pins("R1")

        assert result.success is False
        assert result.error == "NO_SCHEMATIC_LOADED"

    @pytest.mark.asyncio
    async def test_get_component_pins_multiple_components(self, setup_schematic):
        """Test getting pins from multiple components."""
        sch = setup_schematic

        # Add multiple components
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))
        sch.components.add("Device:C", "C1", "100nF", position=(200.0, 100.0))

        # Get pins for each
        r1_result = await get_component_pins("R1")
        r2_result = await get_component_pins("R2")
        c1_result = await get_component_pins("C1")

        assert r1_result.success is True
        assert r2_result.success is True
        assert c1_result.success is True

        # All should have pins
        assert r1_result.pin_count > 0
        assert r2_result.pin_count > 0
        assert c1_result.pin_count > 0


class TestMCPFindPinsByName:
    """Test find_pins_by_name MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("PinNameTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_find_pins_by_exact_name(self, setup_schematic):
        """Test finding pins by exact name match."""
        sch = setup_schematic

        # Add resistor (pins named "~")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Find pins by exact name
        result = await find_pins_by_name("R1", "~")

        assert result["success"] is True
        assert result["reference"] == "R1"
        assert result["pattern"] == "~"
        assert len(result["pin_numbers"]) > 0

    @pytest.mark.asyncio
    async def test_find_pins_by_wildcard(self, setup_schematic):
        """Test finding pins with wildcard pattern."""
        sch = setup_schematic

        # Add component
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Find with wildcard
        result = await find_pins_by_name("R1", "*")

        assert result["success"] is True
        assert len(result["pin_numbers"]) > 0

    @pytest.mark.asyncio
    async def test_find_pins_case_insensitive(self, setup_schematic):
        """Test case-insensitive matching (default)."""
        sch = setup_schematic

        # Add component
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Both should return same results
        result_lower = await find_pins_by_name("R1", "~", case_sensitive=False)
        result_upper = await find_pins_by_name("R1", "~", case_sensitive=False)

        assert result_lower["success"] is True
        assert result_upper["success"] is True
        assert len(result_lower["pin_numbers"]) == len(result_upper["pin_numbers"])

    @pytest.mark.asyncio
    async def test_find_pins_by_name_not_found(self, setup_schematic):
        """Test when no pins match pattern."""
        sch = setup_schematic

        # Add component
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Search for non-existent name
        result = await find_pins_by_name("R1", "NONEXISTENT")

        assert result["success"] is True
        assert len(result["pin_numbers"]) == 0

    @pytest.mark.asyncio
    async def test_find_pins_component_not_found(self, setup_schematic):
        """Test error when component not found."""
        result = await find_pins_by_name("R999", "~")

        assert result["success"] is False
        assert result["error"] == "COMPONENT_NOT_FOUND"


class TestMCPFindPinsByType:
    """Test find_pins_by_type MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("PinTypeTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_find_pins_by_type_passive(self, setup_schematic):
        """Test finding passive pins."""
        sch = setup_schematic

        # Add resistor (passive component)
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Find passive pins
        result = await find_pins_by_type("R1", "passive")

        assert result["success"] is True
        assert result["reference"] == "R1"
        assert result["pin_type"] == "passive"
        assert len(result["pin_numbers"]) > 0

    @pytest.mark.asyncio
    async def test_find_pins_by_type_no_match(self, setup_schematic):
        """Test when no pins match type."""
        sch = setup_schematic

        # Add resistor (has no input pins)
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Search for input pins
        result = await find_pins_by_type("R1", "input")

        assert result["success"] is True
        assert len(result["pin_numbers"]) == 0

    @pytest.mark.asyncio
    async def test_find_pins_invalid_type(self, setup_schematic):
        """Test error for invalid pin type."""
        sch = setup_schematic

        # Add component
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Try invalid type
        result = await find_pins_by_type("R1", "invalid_type")

        assert result["success"] is False
        assert result["error"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_find_pins_component_not_found(self, setup_schematic):
        """Test error when component not found."""
        result = await find_pins_by_type("R999", "passive")

        assert result["success"] is False
        assert result["error"] == "COMPONENT_NOT_FOUND"


class TestMCPCompleteWorkflow:
    """Test complete MCP workflow scenarios."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("WorkflowTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_complete_pin_discovery_workflow(self, setup_schematic):
        """Test complete workflow: create component, find pins, get details."""
        sch = setup_schematic

        # Step 1: Add component
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Step 2: Find pins by name
        name_result = await find_pins_by_name("R1", "~")
        assert name_result["success"] is True
        assert len(name_result["pin_numbers"]) > 0

        # Step 3: Find pins by type
        type_result = await find_pins_by_type("R1", "passive")
        assert type_result["success"] is True
        assert len(type_result["pin_numbers"]) > 0

        # Step 4: Get complete pin details
        pins_result = await get_component_pins("R1")
        assert pins_result.success is True
        assert pins_result.pin_count > 0

        # Verify consistency
        assert len(name_result["pin_numbers"]) == pins_result.pin_count
        assert len(type_result["pin_numbers"]) == pins_result.pin_count

    @pytest.mark.asyncio
    async def test_multiple_component_workflow(self, setup_schematic):
        """Test workflow with multiple components."""
        sch = setup_schematic

        # Add multiple components
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))
        sch.components.add("Device:C", "C1", "100nF", position=(200.0, 100.0))

        # Get pins for all components
        r1_pins = await get_component_pins("R1")
        r2_pins = await get_component_pins("R2")
        c1_pins = await get_component_pins("C1")

        assert r1_pins.success is True
        assert r2_pins.success is True
        assert c1_pins.success is True

        # Find passive pins in all
        r1_passive = await find_pins_by_type("R1", "passive")
        r2_passive = await find_pins_by_type("R2", "passive")
        c1_passive = await find_pins_by_type("C1", "passive")

        assert r1_passive["success"] is True
        assert r2_passive["success"] is True
        assert c1_passive["success"] is True

    @pytest.mark.asyncio
    async def test_save_and_manipulate_schematic(self, setup_schematic, tmp_path):
        """Test creating, saving, and manipulating a schematic."""
        sch = setup_schematic

        # Add components
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))

        # Add a wire
        sch.wires.add(start=(100.0, 100.0), end=(150.0, 100.0))

        # Save schematic
        save_path = tmp_path / "test_workflow.kicad_sch"
        sch.save(str(save_path))

        assert save_path.exists()

        # Load it back
        loaded_sch = ksa.Schematic.load(str(save_path))
        set_current_schematic(loaded_sch)

        # Verify components exist
        r1_pins = await get_component_pins("R1")
        r2_pins = await get_component_pins("R2")

        assert r1_pins.success is True
        assert r2_pins.success is True


class TestMCPAddComponent:
    """Test add_component MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("ComponentTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_add_component_basic(self, setup_schematic):
        """Test basic component addition."""
        sch = setup_schematic

        # Add component via MCP tool
        result = await add_component(
            lib_id="Device:R",
            value="10k",
            reference="R1",
            position=(100.0, 100.0),
        )

        # Verify success
        assert result.success is True
        assert result.reference == "R1"
        assert result.lib_id == "Device:R"
        assert result.value == "10k"
        # Position is grid-snapped (KiCAD's 1.27mm grid)
        assert abs(result.position.x - 100.0) < 0.5
        assert abs(result.position.y - 100.0) < 0.5
        assert result.rotation == 0.0

        # Verify component exists in schematic
        comp = sch.components.get("R1")
        assert comp is not None
        assert comp.value == "10k"

    @pytest.mark.asyncio
    async def test_add_component_auto_reference(self, setup_schematic):
        """Test component addition with auto-generated reference."""
        sch = setup_schematic

        # Add component without reference (should auto-generate)
        result = await add_component(
            lib_id="Device:R",
            value="10k",
            position=(100.0, 100.0),
        )

        # Should succeed with auto-generated reference
        assert result.success is True
        # Reference should be auto-generated (format depends on library)
        assert result.reference is not None
        assert len(result.reference) > 0

        # Verify component exists
        comp = sch.components.get(result.reference)
        assert comp is not None
        assert comp.lib_id == "Device:R"

    @pytest.mark.asyncio
    async def test_add_component_with_footprint(self, setup_schematic):
        """Test component addition with footprint."""
        sch = setup_schematic

        result = await add_component(
            lib_id="Device:R",
            value="10k",
            reference="R1",
            position=(100.0, 100.0),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )

        assert result.success is True
        assert result.footprint == "Resistor_SMD:R_0603_1608Metric"

        # Verify footprint in schematic
        comp = sch.components.get("R1")
        assert comp.footprint == "Resistor_SMD:R_0603_1608Metric"

    @pytest.mark.asyncio
    async def test_add_component_with_rotation(self, setup_schematic):
        """Test component addition with rotation."""
        sch = setup_schematic

        result = await add_component(
            lib_id="Device:R",
            value="10k",
            reference="R1",
            position=(100.0, 100.0),
            rotation=90.0,
        )

        assert result.success is True
        assert result.rotation == 90.0

        # Verify rotation in schematic
        comp = sch.components.get("R1")
        assert comp.rotation == 90.0

    @pytest.mark.asyncio
    async def test_add_component_invalid_rotation(self, setup_schematic):
        """Test error with invalid rotation."""
        sch = setup_schematic

        result = await add_component(
            lib_id="Device:R",
            value="10k",
            reference="R1",
            position=(100.0, 100.0),
            rotation=45.0,  # Invalid - must be 0, 90, 180, or 270
        )

        # Should fail with validation error
        assert result.success is False
        assert result.error == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_add_component_no_schematic(self):
        """Test error when no schematic is loaded."""
        set_current_schematic(None)

        result = await add_component(
            lib_id="Device:R",
            value="10k",
            reference="R1",
            position=(100.0, 100.0),
        )

        # Should fail with no schematic error
        assert result.success is False
        assert result.error == "NO_SCHEMATIC_LOADED"

    @pytest.mark.asyncio
    async def test_add_multiple_components(self, setup_schematic):
        """Test adding multiple components."""
        sch = setup_schematic

        # Add multiple components
        r1 = await add_component(
            lib_id="Device:R",
            value="10k",
            reference="R1",
            position=(100.0, 100.0),
        )

        r2 = await add_component(
            lib_id="Device:R",
            value="20k",
            reference="R2",
            position=(150.0, 100.0),
        )

        c1 = await add_component(
            lib_id="Device:C",
            value="100nF",
            reference="C1",
            position=(200.0, 100.0),
        )

        # All should succeed
        assert r1.success is True
        assert r2.success is True
        assert c1.success is True

        # Verify all exist in schematic
        assert sch.components.get("R1") is not None
        assert sch.components.get("R2") is not None
        assert sch.components.get("C1") is not None

    @pytest.mark.asyncio
    async def test_add_component_auto_position(self, setup_schematic):
        """Test component addition with auto-positioning."""
        sch = setup_schematic

        # Add component without position (should auto-place)
        result = await add_component(
            lib_id="Device:R",
            value="10k",
            reference="R1",
        )

        assert result.success is True
        # Position should be set (auto-placed)
        assert result.position.x is not None
        assert result.position.y is not None


class TestMCPListComponents:
    """Test list_components MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("ListTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_list_components_empty(self, setup_schematic):
        """Test listing components in empty schematic."""
        result = await list_components()

        assert result["success"] is True
        assert result["count"] == 0
        assert result["components"] == []

    @pytest.mark.asyncio
    async def test_list_components_with_components(self, setup_schematic):
        """Test listing components."""
        sch = setup_schematic

        # Add some components
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))
        sch.components.add("Device:C", "C1", "100nF", position=(200.0, 100.0))

        # List components
        result = await list_components()

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["components"]) == 3

        # Check references
        refs = [comp["reference"] for comp in result["components"]]
        assert "R1" in refs
        assert "R2" in refs
        assert "C1" in refs


class TestMCPUpdateComponent:
    """Test update_component MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("UpdateTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_update_component_value(self, setup_schematic):
        """Test updating component value."""
        sch = setup_schematic
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Update value
        result = await update_component("R1", value="20k")

        assert result.success is True
        assert result.value == "20k"

        # Verify in schematic
        comp = sch.components.get("R1")
        assert comp.value == "20k"

    @pytest.mark.asyncio
    async def test_update_component_multiple_properties(self, setup_schematic):
        """Test updating multiple properties at once."""
        sch = setup_schematic
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Update multiple properties
        result = await update_component(
            "R1", value="20k", rotation=90.0, footprint="Resistor_SMD:R_0805_2012Metric"
        )

        assert result.success is True
        assert result.value == "20k"
        assert result.rotation == 90.0
        assert result.footprint == "Resistor_SMD:R_0805_2012Metric"

    @pytest.mark.asyncio
    async def test_update_component_not_found(self, setup_schematic):
        """Test error when component not found."""
        result = await update_component("R999", value="10k")

        assert result.success is False
        assert result.error == "COMPONENT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_update_component_invalid_rotation(self, setup_schematic):
        """Test error with invalid rotation."""
        sch = setup_schematic
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        result = await update_component("R1", rotation=45.0)

        assert result.success is False
        assert result.error == "VALIDATION_ERROR"


class TestMCPRemoveComponent:
    """Test remove_component MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("RemoveTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_remove_component_success(self, setup_schematic):
        """Test successful component removal."""
        sch = setup_schematic
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Remove component
        result = await remove_component("R1")

        assert result["success"] is True
        assert result["reference"] == "R1"

        # Verify removal
        comp = sch.components.get("R1")
        assert comp is None

    @pytest.mark.asyncio
    async def test_remove_component_not_found(self, setup_schematic):
        """Test error when component not found."""
        result = await remove_component("R999")

        assert result["success"] is False
        assert result["error"] == "COMPONENT_NOT_FOUND"


class TestMCPFilterComponents:
    """Test filter_components MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("FilterTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_filter_by_lib_id(self, setup_schematic):
        """Test filtering by library ID."""
        sch = setup_schematic

        # Add components
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))
        sch.components.add("Device:C", "C1", "100nF", position=(200.0, 100.0))

        # Filter resistors
        result = await filter_components(lib_id="Device:R")

        assert result["success"] is True
        assert result["count"] == 2
        refs = [comp["reference"] for comp in result["components"]]
        assert "R1" in refs
        assert "R2" in refs
        assert "C1" not in refs

    @pytest.mark.asyncio
    async def test_filter_by_value(self, setup_schematic):
        """Test filtering by exact value."""
        sch = setup_schematic

        # Add components
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "10k", position=(150.0, 100.0))
        sch.components.add("Device:R", "R3", "20k", position=(200.0, 100.0))

        # Filter by value
        result = await filter_components(value="10k")

        assert result["success"] is True
        assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_filter_by_value_pattern(self, setup_schematic):
        """Test filtering by value pattern."""
        sch = setup_schematic

        # Add components
        sch.components.add("Device:R", "R1", "100", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "1000", position=(150.0, 100.0))
        sch.components.add("Device:R", "R3", "10k", position=(200.0, 100.0))

        # Filter by pattern (contains "10")
        result = await filter_components(value_pattern="10")

        assert result["success"] is True
        assert result["count"] >= 2  # Should match "1000" and "10k"

    @pytest.mark.asyncio
    async def test_filter_multiple_criteria(self, setup_schematic):
        """Test filtering with multiple criteria (AND logic)."""
        sch = setup_schematic

        # Add components
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        sch.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))
        sch.components.add("Device:C", "C1", "10k", position=(200.0, 100.0))

        # Filter by lib_id AND value
        result = await filter_components(lib_id="Device:R", value="10k")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["components"][0]["reference"] == "R1"


class TestMCPAddWire:
    """Test add_wire MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("WireTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_add_wire_horizontal(self, setup_schematic):
        """Test adding horizontal wire."""
        result = await add_wire(start=(100.0, 100.0), end=(150.0, 100.0))

        assert result["success"] is True
        assert result["start"]["x"] == 100.0
        assert result["start"]["y"] == 100.0
        assert result["end"]["x"] == 150.0
        assert result["end"]["y"] == 100.0
        assert "uuid" in result

    @pytest.mark.asyncio
    async def test_add_wire_vertical(self, setup_schematic):
        """Test adding vertical wire."""
        result = await add_wire(start=(100.0, 100.0), end=(100.0, 150.0))

        assert result["success"] is True
        assert result["start"]["x"] == 100.0
        assert result["end"]["x"] == 100.0

    @pytest.mark.asyncio
    async def test_add_wire_no_schematic(self):
        """Test error when no schematic loaded."""
        set_current_schematic(None)

        result = await add_wire(start=(100.0, 100.0), end=(150.0, 100.0))

        assert result["success"] is False
        assert result["error"] == "NO_SCHEMATIC_LOADED"


class TestMCPAddLabel:
    """Test add_label MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("LabelTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_add_label_basic(self, setup_schematic):
        """Test adding basic label."""
        result = await add_label(text="VCC", position=(100.0, 100.0))

        assert result["success"] is True
        assert result["text"] == "VCC"
        assert result["position"]["x"] == 100.0
        assert result["position"]["y"] == 100.0
        assert result["rotation"] == 0.0
        assert "uuid" in result

    @pytest.mark.asyncio
    async def test_add_label_with_rotation(self, setup_schematic):
        """Test adding label with rotation."""
        result = await add_label(text="GND", position=(100.0, 100.0), rotation=90.0)

        assert result["success"] is True
        assert result["rotation"] == 90.0

    @pytest.mark.asyncio
    async def test_add_label_invalid_rotation(self, setup_schematic):
        """Test error with invalid rotation."""
        result = await add_label(text="VCC", position=(100.0, 100.0), rotation=45.0)

        assert result["success"] is False
        assert result["error"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_add_label_custom_size(self, setup_schematic):
        """Test adding label with custom size."""
        result = await add_label(text="SIGNAL", position=(100.0, 100.0), size=2.54)

        assert result["success"] is True
        assert result["size"] == 2.54


class TestMCPAddJunction:
    """Test add_junction MCP tool."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("JunctionTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_add_junction_basic(self, setup_schematic):
        """Test adding basic junction."""
        result = await add_junction(position=(100.0, 100.0))

        assert result["success"] is True
        assert result["position"]["x"] == 100.0
        assert result["position"]["y"] == 100.0
        assert result["diameter"] == 0.0
        assert "uuid" in result

    @pytest.mark.asyncio
    async def test_add_junction_with_diameter(self, setup_schematic):
        """Test adding junction with custom diameter."""
        result = await add_junction(position=(100.0, 100.0), diameter=0.8)

        assert result["success"] is True
        assert result["diameter"] == 0.8

    @pytest.mark.asyncio
    async def test_add_junction_no_schematic(self):
        """Test error when no schematic loaded."""
        set_current_schematic(None)

        result = await add_junction(position=(100.0, 100.0))

        assert result["success"] is False
        assert result["error"] == "NO_SCHEMATIC_LOADED"


class TestMCPPerformance:
    """Test MCP tool performance."""

    @pytest.fixture(autouse=True)
    def setup_schematic(self):
        """Set up a fresh schematic for each test."""
        sch = ksa.create_schematic("PerformanceTest")
        set_current_schematic(sch)
        yield sch
        set_current_schematic(None)

    @pytest.mark.asyncio
    async def test_performance_many_pin_lookups(self, setup_schematic):
        """Test performance with many pin lookups."""
        sch = setup_schematic

        # Add 10 components
        for i in range(10):
            sch.components.add(
                "Device:R", f"R{i+1}", f"{10*(i+1)}k", position=(100.0 + i * 10, 100.0)
            )

        # Do 10 lookups
        import time

        start = time.time()

        for i in range(10):
            result = await get_component_pins(f"R{i+1}")
            assert result.success is True

        elapsed = (time.time() - start) * 1000  # Convert to ms
        avg_time = elapsed / 10

        # Should be fast (< 50ms average)
        assert avg_time < 50, f"Average lookup took {avg_time:.2f}ms (should be <50ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
