#!/usr/bin/env python3
"""
Unit tests for pin position rotation transformation.

Tests that pin positions are correctly calculated for rotated components
using the standard 2D rotation matrix.
"""

import math

import pytest

import kicad_sch_api as ksa


class TestPinRotation:
    """Test pin position calculations with component rotation."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("pin_rotation_test")

    def test_pin_position_0_degrees(self, schematic):
        """Test pin positions at 0° rotation (vertical resistor)."""
        # Add resistor at 0° (default vertical orientation)
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0
        )

        # Get actual component position (may be grid-snapped)
        comp_x, comp_y = comp.position.x, comp.position.y

        # Device:R has pins at (0, 3.81) and (0, -3.81) in symbol coordinates
        # At 0° rotation, these should remain unchanged
        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        assert pin1_pos is not None, "Pin 1 should exist"
        assert pin2_pos is not None, "Pin 2 should exist"

        # Pin 1 at top: (comp_x + 0, comp_y + 3.81)
        assert math.isclose(pin1_pos.x, comp_x, abs_tol=0.01)
        assert math.isclose(pin1_pos.y, comp_y + 3.81, abs_tol=0.01)

        # Pin 2 at bottom: (comp_x + 0, comp_y - 3.81)
        assert math.isclose(pin2_pos.x, comp_x, abs_tol=0.01)
        assert math.isclose(pin2_pos.y, comp_y - 3.81, abs_tol=0.01)

    def test_pin_position_90_degrees(self, schematic):
        """Test pin positions at 90° rotation (horizontal resistor)."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=90
        )

        comp_x, comp_y = comp.position.x, comp.position.y

        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        assert pin1_pos is not None
        assert pin2_pos is not None

        # At 90° rotation:
        # Pin 1: (0, 3.81) → (-3.81, 0) → (comp_x - 3.81, comp_y)
        # Pin 2: (0, -3.81) → (3.81, 0) → (comp_x + 3.81, comp_y)
        assert math.isclose(pin1_pos.x, comp_x - 3.81, abs_tol=0.01)
        assert math.isclose(pin1_pos.y, comp_y, abs_tol=0.01)

        assert math.isclose(pin2_pos.x, comp_x + 3.81, abs_tol=0.01)
        assert math.isclose(pin2_pos.y, comp_y, abs_tol=0.01)

    def test_pin_position_180_degrees(self, schematic):
        """Test pin positions at 180° rotation (vertical, flipped)."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=180
        )

        comp_x, comp_y = comp.position.x, comp.position.y

        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        assert pin1_pos is not None
        assert pin2_pos is not None

        # At 180° rotation:
        # Pin 1: (0, 3.81) → (0, -3.81) → (comp_x, comp_y - 3.81)
        # Pin 2: (0, -3.81) → (0, 3.81) → (comp_x, comp_y + 3.81)
        assert math.isclose(pin1_pos.x, comp_x, abs_tol=0.01)
        assert math.isclose(pin1_pos.y, comp_y - 3.81, abs_tol=0.01)

        assert math.isclose(pin2_pos.x, comp_x, abs_tol=0.01)
        assert math.isclose(pin2_pos.y, comp_y + 3.81, abs_tol=0.01)

    def test_pin_position_270_degrees(self, schematic):
        """Test pin positions at 270° rotation (horizontal, flipped)."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=270
        )

        comp_x, comp_y = comp.position.x, comp.position.y

        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        assert pin1_pos is not None
        assert pin2_pos is not None

        # At 270° rotation:
        # Pin 1: (0, 3.81) → (3.81, 0) → (comp_x + 3.81, comp_y)
        # Pin 2: (0, -3.81) → (-3.81, 0) → (comp_x - 3.81, comp_y)
        assert math.isclose(pin1_pos.x, comp_x + 3.81, abs_tol=0.01)
        assert math.isclose(pin1_pos.y, comp_y, abs_tol=0.01)

        assert math.isclose(pin2_pos.x, comp_x - 3.81, abs_tol=0.01)
        assert math.isclose(pin2_pos.y, comp_y, abs_tol=0.01)

    @pytest.mark.parametrize("rotation", [0, 90, 180, 270])
    def test_pin_position_all_rotations(self, schematic, rotation):
        """Test pin positions for all valid rotation angles."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=rotation
        )

        comp_x, comp_y = comp.position.x, comp.position.y

        # Both pins should be found
        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        assert pin1_pos is not None, f"Pin 1 not found at {rotation}°"
        assert pin2_pos is not None, f"Pin 2 not found at {rotation}°"

        # Verify pins are at the expected distance from component center
        # Resistor pins are at 3.81mm from center
        dist1 = math.sqrt((pin1_pos.x - comp_x) ** 2 + (pin1_pos.y - comp_y) ** 2)
        dist2 = math.sqrt((pin2_pos.x - comp_x) ** 2 + (pin2_pos.y - comp_y) ** 2)

        assert math.isclose(dist1, 3.81, abs_tol=0.01), f"Pin 1 distance incorrect at {rotation}°"
        assert math.isclose(dist2, 3.81, abs_tol=0.01), f"Pin 2 distance incorrect at {rotation}°"

    def test_pin_position_nonexistent_pin(self, schematic):
        """Test that get_pin_position returns None for non-existent pins."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0
        )

        # Resistor only has pins 1 and 2
        pin_pos = comp.get_pin_position("99")
        assert pin_pos is None, "Should return None for non-existent pin"

    def test_pin_position_with_offset_component_position(self, schematic):
        """Test pin positions with non-standard component position."""
        comp = schematic.components.add(
            "Device:R", "R1", "10k", position=(150.5, 200.7), rotation=90
        )

        comp_x, comp_y = comp.position.x, comp.position.y

        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        # At 90° with offset position:
        # Pin 1: (comp_x - 3.81, comp_y)
        # Pin 2: (comp_x + 3.81, comp_y)
        assert math.isclose(pin1_pos.x, comp_x - 3.81, abs_tol=0.01)
        assert math.isclose(pin1_pos.y, comp_y, abs_tol=0.01)

        assert math.isclose(pin2_pos.x, comp_x + 3.81, abs_tol=0.01)
        assert math.isclose(pin2_pos.y, comp_y, abs_tol=0.01)

    def test_pin_position_different_component_types(self, schematic):
        """Test pin positions work with different component types."""
        # Test with capacitor (also 2-pin component)
        cap = schematic.components.add(
            "Device:C", "C1", "100nF", position=(100.0, 100.0), rotation=90
        )

        cap_pin1 = cap.get_pin_position("1")
        cap_pin2 = cap.get_pin_position("2")

        assert cap_pin1 is not None
        assert cap_pin2 is not None

        # Verify pins are rotated correctly (horizontal at 90°)
        assert not math.isclose(
            cap_pin1.x, cap_pin2.x, abs_tol=0.1
        ), "Pins should be horizontally separated at 90°"
        assert math.isclose(
            cap_pin1.y, cap_pin2.y, abs_tol=0.1
        ), "Pins should be at same Y coordinate at 90°"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
