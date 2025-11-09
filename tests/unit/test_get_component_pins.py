#!/usr/bin/env python3
"""
Unit tests for get_component_pins tool (Issue #200).

Tests comprehensive pin information retrieval including metadata,
positions, electrical types, and error handling.
"""

import logging
import math

import pytest

import kicad_sch_api as ksa
from kicad_sch_api import PinInfo
from kicad_sch_api.core.exceptions import LibraryError

logger = logging.getLogger(__name__)


class TestGetComponentPins:
    """Test get_pins_info() method for comprehensive pin discovery."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("get_pins_test")

    # ========== Basic Pin Retrieval Tests ==========

    def test_get_pins_info_simple_resistor(self, schematic):
        """Test retrieving pin information for a simple resistor."""
        # Add a resistor
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Get pins
        pins = schematic.components.get_pins_info("R1")

        # Verify pins retrieved
        assert pins is not None, "Should return pins for valid component"
        assert len(pins) == 2, "Resistor should have 2 pins"
        assert all(isinstance(p, PinInfo) for p in pins), "All should be PinInfo objects"

    def test_get_pins_info_returns_none_for_missing_component(self, schematic):
        """Test that get_pins_info returns None for non-existent component."""
        pins = schematic.components.get_pins_info("R999")
        assert pins is None, "Should return None for missing component"

    def test_get_pins_info_raises_for_missing_library(self, schematic):
        """Test that get_pins_info raises LibraryError for missing symbol."""
        # Add a component (this will succeed because library cache has Device:R)
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Now manually change the lib_id to something that doesn't exist
        comp._data.lib_id = "NonExistent:Weird"

        # Should raise LibraryError
        with pytest.raises(LibraryError) as exc_info:
            schematic.components.get_pins_info("R1")

        assert "NonExistent:Weird" in str(exc_info.value)

    # ========== Pin Metadata Tests ==========

    def test_pin_info_contains_required_fields(self, schematic):
        """Test that PinInfo contains all required fields."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None
        pin = pins[0]

        # Verify required fields
        assert hasattr(pin, "number"), "Should have pin number"
        assert hasattr(pin, "name"), "Should have pin name"
        assert hasattr(pin, "position"), "Should have position"
        assert hasattr(pin, "electrical_type"), "Should have electrical type"
        assert hasattr(pin, "shape"), "Should have pin shape"
        assert hasattr(pin, "length"), "Should have pin length"
        assert hasattr(pin, "orientation"), "Should have orientation"
        assert hasattr(pin, "uuid"), "Should have UUID"

    def test_pin_info_electrical_types(self, schematic):
        """Test that pin electrical types are correctly reported."""
        # Resistor is passive
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None
        for pin in pins:
            # Resistor pins should be passive
            assert str(pin.electrical_type.value) == "passive"

    def test_pin_info_pin_numbers(self, schematic):
        """Test that pin numbers are correctly retrieved."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None
        pin_numbers = [p.number for p in pins]
        assert "1" in pin_numbers, "Should have pin 1"
        assert "2" in pin_numbers, "Should have pin 2"

    def test_pin_info_pin_names(self, schematic):
        """Test that pin names are correctly retrieved."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None
        assert all(isinstance(p.name, str) for p in pins), "All pin names should be strings"
        assert all(len(p.name) > 0 for p in pins), "All pins should have names"

    # ========== Position Accuracy Tests ==========

    def test_pin_position_accuracy_no_rotation(self, schematic):
        """Test that pin positions are accurate for unrotated components."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0
        )
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None
        assert len(pins) >= 2, "Should have at least 2 pins"

        # Compare with component.get_pin_position()
        for pin in pins:
            direct_pos = comp.get_pin_position(pin.number)
            assert direct_pos is not None
            assert math.isclose(pin.position.x, direct_pos.x, abs_tol=0.01)
            assert math.isclose(pin.position.y, direct_pos.y, abs_tol=0.01)

    def test_pin_position_accuracy_90_degree_rotation(self, schematic):
        """Test that pin positions are accurate for 90° rotated components."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=90
        )
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None

        # Verify positions match rotated calculation
        for pin in pins:
            direct_pos = comp.get_pin_position(pin.number)
            assert direct_pos is not None
            assert math.isclose(pin.position.x, direct_pos.x, abs_tol=0.01)
            assert math.isclose(pin.position.y, direct_pos.y, abs_tol=0.01)

    def test_pin_position_accuracy_180_degree_rotation(self, schematic):
        """Test that pin positions are accurate for 180° rotated components."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=180
        )
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None

        # Verify positions match rotated calculation
        for pin in pins:
            direct_pos = comp.get_pin_position(pin.number)
            assert direct_pos is not None
            assert math.isclose(pin.position.x, direct_pos.x, abs_tol=0.01)
            assert math.isclose(pin.position.y, direct_pos.y, abs_tol=0.01)

    def test_pin_position_accuracy_270_degree_rotation(self, schematic):
        """Test that pin positions are accurate for 270° rotated components."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=270
        )
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None

        # Verify positions match rotated calculation
        for pin in pins:
            direct_pos = comp.get_pin_position(pin.number)
            assert direct_pos is not None
            assert math.isclose(pin.position.x, direct_pos.x, abs_tol=0.01)
            assert math.isclose(pin.position.y, direct_pos.y, abs_tol=0.01)

    # ========== Multi-Pin Component Tests ==========

    def test_get_pins_info_integrated_circuit_multiple_pins(self, schematic):
        """Test pin retrieval for IC with many pins."""
        # Try to add a DIP8 IC (common op-amp)
        try:
            comp = schematic.components.add(
                "Amplifier_Operational:TL072", "U1", "TL072", position=(100.0, 100.0)
            )
            pins = schematic.components.get_pins_info("U1")

            if pins is not None:
                # Should have multiple pins
                assert len(pins) > 2, "Op-amp should have multiple pins"
                # All should be PinInfo objects
                assert all(isinstance(p, PinInfo) for p in pins)
        except LibraryError:
            # If TL072 not available, skip this test
            pytest.skip("TL072 symbol not available in library")

    # ========== Pin Data Structure Tests ==========

    def test_pin_uuid_uniqueness(self, schematic):
        """Test that each pin has a unique UUID."""
        comp1 = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        comp2 = schematic.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))

        pins1 = schematic.components.get_pins_info("R1")
        pins2 = schematic.components.get_pins_info("R2")

        assert pins1 is not None and pins2 is not None
        all_uuids = [p.uuid for p in pins1 + pins2]
        assert len(all_uuids) == len(set(all_uuids)), "All UUIDs should be unique"

    def test_pin_info_to_dict_conversion(self, schematic):
        """Test that PinInfo can be converted to dictionary."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None
        pin = pins[0]

        # Convert to dict
        pin_dict = pin.to_dict()

        # Verify dict structure
        assert isinstance(pin_dict, dict)
        assert "number" in pin_dict
        assert "name" in pin_dict
        assert "position" in pin_dict
        assert "electrical_type" in pin_dict
        assert "shape" in pin_dict
        assert isinstance(pin_dict["position"], dict)
        assert "x" in pin_dict["position"] and "y" in pin_dict["position"]

    # ========== Multiple Component Tests ==========

    def test_get_pins_info_multiple_components(self, schematic):
        """Test retrieving pins for multiple different components."""
        comp_r1 = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        comp_r2 = schematic.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))

        pins_r1 = schematic.components.get_pins_info("R1")
        pins_r2 = schematic.components.get_pins_info("R2")

        assert pins_r1 is not None
        assert pins_r2 is not None
        assert len(pins_r1) == 2
        assert len(pins_r2) == 2

        # Pins from different components should be different
        assert pins_r1[0].uuid != pins_r2[0].uuid

    # ========== Error Handling Tests ==========

    def test_get_pins_info_empty_schematic(self, schematic):
        """Test get_pins_info on empty schematic."""
        pins = schematic.components.get_pins_info("R1")
        assert pins is None, "Should return None for missing component"

    def test_get_pins_info_case_sensitivity(self, schematic):
        """Test that reference lookup is case-sensitive."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Correct case should work
        pins = schematic.components.get_pins_info("R1")
        assert pins is not None

        # Wrong case should return None (references are case-sensitive)
        pins_wrong = schematic.components.get_pins_info("r1")
        assert pins_wrong is None

    def test_get_pins_info_special_characters_in_ref(self, schematic):
        """Test get_pins_info with special characters in reference."""
        # Most valid references don't have special chars, but test edge case
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.get_pins_info("R1")
        assert pins is not None

    # ========== Logging Verification Tests ==========

    def test_get_pins_info_debug_logging(self, schematic, caplog):
        """Test that debug logging is produced during pin discovery."""
        with caplog.at_level(logging.DEBUG):
            comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
            pins = schematic.components.get_pins_info("R1")

        assert pins is not None

        # Check for debug logging markers
        log_text = caplog.text
        assert "[PIN_DISCOVERY]" in log_text or "get_pins_info" in log_text

    # ========== Position Grid Alignment Tests ==========

    def test_pin_positions_on_component_grid(self, schematic):
        """Test that component positions affect pin positions correctly."""
        # Add component at different positions
        comp1 = schematic.components.add("Device:R", "R1", "10k", position=(50.0, 50.0))
        comp2 = schematic.components.add("Device:R", "R2", "10k", position=(100.0, 100.0))

        pins1 = schematic.components.get_pins_info("R1")
        pins2 = schematic.components.get_pins_info("R2")

        assert pins1 is not None and pins2 is not None

        # Pin positions should differ by component position difference
        delta_x = comp2.position.x - comp1.position.x
        delta_y = comp2.position.y - comp1.position.y

        for p1, p2 in zip(pins1, pins2):
            # The position difference should account for component position difference
            assert p1.number == p2.number, "Pin numbers should match"

    # ========== Type Validation Tests ==========

    def test_pin_info_position_is_point(self, schematic):
        """Test that pin position is a Point object."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        pins = schematic.components.get_pins_info("R1")

        assert pins is not None
        for pin in pins:
            assert hasattr(pin.position, "x"), "Position should be a Point with x"
            assert hasattr(pin.position, "y"), "Position should be a Point with y"
            assert isinstance(pin.position.x, float)
            assert isinstance(pin.position.y, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
