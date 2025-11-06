#!/usr/bin/env python3
"""
Integration tests for MCP server functionality.

Tests the complete MCP server workflow including schematic management
and pin discovery tools.
"""

import logging
import pytest
from pathlib import Path

import kicad_sch_api as ksa
from mcp_server.tools.pin_discovery import (
    get_component_pins,
    find_pins_by_name,
    find_pins_by_type,
    set_current_schematic,
    get_current_schematic,
)


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
            sch.components.add("Device:R", f"R{i+1}", f"{10*(i+1)}k", position=(100.0 + i*10, 100.0))

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
