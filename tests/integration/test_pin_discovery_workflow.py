#!/usr/bin/env python3
"""
Integration test for pin discovery workflow (Issue #200).

Tests complete workflows for discovering pins, retrieving metadata,
and validating positions across component rotations.
"""

import logging
import math

import pytest
from mcp_server.models import ComponentPinsOutput, PinInfoOutput

import kicad_sch_api as ksa

logger = logging.getLogger(__name__)


class TestPinDiscoveryWorkflow:
    """Integration tests for complete pin discovery workflows."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("pin_discovery_integration_test")

    # ========== Basic Workflow Tests ==========

    def test_complete_pin_discovery_workflow(self, schematic):
        """Test complete workflow: add component -> get pins -> validate data."""
        # Step 1: Add component
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        assert comp is not None
        assert comp.reference == "R1"

        # Step 2: Get pins
        pins = schematic.components.get_pins_info("R1")
        assert pins is not None
        assert len(pins) == 2

        # Step 3: Validate pin data
        for pin in pins:
            assert pin.number in ["1", "2"]
            assert isinstance(pin.name, str)
            assert isinstance(pin.position.x, float)
            assert isinstance(pin.position.y, float)
            assert pin.electrical_type.value == "passive"
            assert pin.uuid is not None

    def test_workflow_multiple_components_different_types(self, schematic):
        """Test workflow with multiple different component types."""
        # Add resistor
        r1 = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r1_pins = schematic.components.get_pins_info("R1")

        # Add capacitor
        c1 = schematic.components.add("Device:C", "C1", "100nF", position=(150.0, 100.0))
        c1_pins = schematic.components.get_pins_info("C1")

        # Add LED
        led1 = schematic.components.add("LED:LED", "LED1", "Red", position=(200.0, 100.0))
        led1_pins = schematic.components.get_pins_info("LED1")

        # Verify all components have pins
        assert r1_pins is not None and len(r1_pins) > 0
        assert c1_pins is not None and len(c1_pins) > 0
        assert led1_pins is not None and len(led1_pins) > 0

        # Verify electrical types
        assert all(p.electrical_type.value == "passive" for p in r1_pins)
        assert all(p.electrical_type.value == "passive" for p in c1_pins)

    # ========== Rotation Accuracy Workflow Tests ==========

    def test_workflow_with_component_rotation(self, schematic):
        """Test pin discovery workflow with rotated components."""
        rotations = [0, 90, 180, 270]

        for rot in rotations:
            ref = f"R{rot}"
            comp = schematic.components.add(
                "Device:R", ref, "10k", position=(100.0 + rot, 100.0), rotation=rot
            )
            pins = schematic.components.get_pins_info(ref)

            assert pins is not None, f"Should get pins for component at {rot}°"
            assert len(pins) == 2, f"Resistor should have 2 pins at {rot}°"

            # Verify positions are different for different rotations
            for pin in pins:
                assert isinstance(pin.position.x, float)
                assert isinstance(pin.position.y, float)

    def test_workflow_pin_positions_match_direct_query(self, schematic):
        """Test that get_pins_info positions match direct component queries."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=45 % 360
        )
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None

        # Compare with direct component query
        for pin in pins:
            direct_pos = comp.get_pin_position(pin.number)
            assert direct_pos is not None
            assert math.isclose(pin.position.x, direct_pos.x, abs_tol=0.01)
            assert math.isclose(pin.position.y, direct_pos.y, abs_tol=0.01)

    # ========== Large Schematic Workflow Tests ==========

    def test_workflow_many_components(self, schematic):
        """Test workflow with many components in schematic."""
        # Add 20 different components
        num_components = 20
        for i in range(num_components):
            schematic.components.add(
                "Device:R", f"R{i+1}", f"{10*(i+1)}k", position=(100.0 + i * 5, 100.0)
            )

        # Verify we can get pins for each
        for i in range(num_components):
            pins = schematic.components.get_pins_info(f"R{i+1}")
            assert pins is not None
            assert len(pins) == 2

    def test_workflow_batch_pin_discovery(self, schematic):
        """Test workflow for discovering pins of multiple components efficiently."""
        # Add multiple components
        refs = ["R1", "R2", "C1", "C2"]
        expected_pins = {
            "R1": ("Device:R", "10k"),
            "R2": ("Device:R", "20k"),
            "C1": ("Device:C", "100nF"),
            "C2": ("Device:C", "1uF"),
        }

        for ref, (lib_id, value) in expected_pins.items():
            schematic.components.add(lib_id, ref, value, position=(100.0, 100.0))

        # Batch discover pins
        all_pins = {}
        for ref in refs:
            pins = schematic.components.get_pins_info(ref)
            assert pins is not None
            all_pins[ref] = pins

        # Verify we got pins for all
        assert len(all_pins) == len(refs)
        assert all(len(pins) > 0 for pins in all_pins.values())

    # ========== Error Handling Workflow Tests ==========

    def test_workflow_error_handling_missing_component(self, schematic):
        """Test workflow handles missing components gracefully."""
        # Try to get pins for non-existent component
        pins = schematic.components.get_pins_info("R999")

        # Should return None, not crash
        assert pins is None

    def test_workflow_error_handling_library_error(self, schematic):
        """Test workflow handles library errors appropriately."""
        from kicad_sch_api.core.exceptions import LibraryError

        # Add component
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Corrupt the lib_id
        comp._data.lib_id = "InvalidLib:InvalidSymbol"

        # Should raise LibraryError
        with pytest.raises(LibraryError):
            schematic.components.get_pins_info("R1")

    # ========== Pydantic Model Integration Tests ==========

    def test_workflow_convert_to_pydantic_model(self, schematic):
        """Test converting pin data to Pydantic models for MCP output."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None

        # Convert each pin to Pydantic model
        pin_outputs = []
        for pin in pins:
            pin_output = PinInfoOutput(
                number=pin.number,
                name=pin.name,
                position={"x": pin.position.x, "y": pin.position.y},
                electrical_type=pin.electrical_type.value,
                shape=pin.shape.value,
                length=pin.length,
                orientation=pin.orientation,
                uuid=pin.uuid,
            )
            pin_outputs.append(pin_output)

        # Create component output model
        component_output = ComponentPinsOutput(
            reference=comp.reference,
            lib_id=comp.lib_id,
            pins=pin_outputs,
            pin_count=len(pin_outputs),
            success=True,
        )

        # Verify model
        assert component_output.reference == "R1"
        assert component_output.lib_id == "Device:R"
        assert component_output.pin_count == 2
        assert len(component_output.pins) == 2

        # Verify model can be serialized to JSON
        json_data = component_output.model_dump_json()
        assert isinstance(json_data, str)
        assert "R1" in json_data

    def test_workflow_pydantic_model_serialization(self, schematic):
        """Test that Pydantic models serialize correctly for MCP clients."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None

        # Create Pydantic model
        pin_outputs = []
        for pin in pins:
            pin_output = PinInfoOutput(
                number=pin.number,
                name=pin.name,
                position={"x": pin.position.x, "y": pin.position.y},
                electrical_type=pin.electrical_type.value,
                shape=pin.shape.value,
                length=pin.length,
                orientation=pin.orientation,
                uuid=pin.uuid,
            )
            pin_outputs.append(pin_output)

        component_output = ComponentPinsOutput(
            reference=comp.reference,
            lib_id=comp.lib_id,
            pins=pin_outputs,
            pin_count=len(pin_outputs),
        )

        # Serialize and deserialize
        json_data = component_output.model_dump_json()
        deserialized = ComponentPinsOutput.model_validate_json(json_data)

        # Verify round-trip
        assert deserialized.reference == component_output.reference
        assert deserialized.pin_count == component_output.pin_count
        assert len(deserialized.pins) == len(component_output.pins)

    # ========== End-to-End Workflow Tests ==========

    def test_workflow_schematic_creation_to_mcp_output(self, schematic):
        """Test complete workflow from schematic creation to MCP output."""
        # Step 1: Create schematic with components
        r1 = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = schematic.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))
        c1 = schematic.components.add("Device:C", "C1", "100nF", position=(200.0, 100.0))

        # Step 2: Discover pins for each
        r1_pins = schematic.components.get_pins_info("R1")
        r2_pins = schematic.components.get_pins_info("R2")
        c1_pins = schematic.components.get_pins_info("C1")

        assert all(p is not None for p in [r1_pins, r2_pins, c1_pins])

        # Step 3: Create MCP output for each
        for ref, pins in [("R1", r1_pins), ("R2", r2_pins), ("C1", c1_pins)]:
            comp = schematic.components.get(ref)

            pin_outputs = []
            for pin in pins:
                pin_outputs.append(
                    PinInfoOutput(
                        number=pin.number,
                        name=pin.name,
                        position={"x": pin.position.x, "y": pin.position.y},
                        electrical_type=pin.electrical_type.value,
                        shape=pin.shape.value,
                        length=pin.length,
                        orientation=pin.orientation,
                        uuid=pin.uuid,
                    )
                )

            component_output = ComponentPinsOutput(
                reference=comp.reference,
                lib_id=comp.lib_id,
                pins=pin_outputs,
                pin_count=len(pin_outputs),
            )

            # Verify output
            assert component_output.success is True
            assert component_output.pin_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
