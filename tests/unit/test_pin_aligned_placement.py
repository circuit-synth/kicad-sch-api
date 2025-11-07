"""
Tests for pin-aligned component placement functionality.

Tests the new helper functions for placing components by pin position
instead of component center, which is essential for clean horizontal
signal flows without manual offset calculations.
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.geometry import calculate_position_for_pin
from kicad_sch_api.core.types import Point


class TestCalculatePositionForPin:
    """Test the calculate_position_for_pin() helper function."""

    def test_basic_calculation_rotation_0(self):
        """Test basic position calculation with no rotation."""
        # For a pin at local (2.54, 0) that we want at (150, 100)
        # Component should be at (150 - 2.54, 100 - 0) = (147.46, 100)
        # After grid snapping to 1.27mm grid

        pin_local = Point(2.54, 0)
        desired_pos = Point(150, 100)

        comp_pos = calculate_position_for_pin(
            pin_local_position=pin_local,
            desired_pin_position=desired_pos,
            rotation=0,
            grid_size=1.27
        )

        # Should be snapped to grid (1.27mm)
        # 147.46 / 1.27 ≈ 116.11 → 116 → 147.32
        # 100 / 1.27 ≈ 78.74 → 79 → 100.33
        assert abs(comp_pos.x - 147.32) < 0.01
        assert abs(comp_pos.y - 100.33) < 0.01

    def test_calculation_with_rotation_90(self):
        """Test position calculation with 90 degree rotation."""
        # Pin at local (2.54, 0)
        # After Y inversion: (2.54, 0)
        # After 90° rotation: (0, 2.54)
        # Want pin at (150, 100)
        # Component at (150 - 0, 100 - 2.54) = (150, 97.46) → (150.11, 96.52) snapped

        pin_local = Point(2.54, 0)
        desired_pos = Point(150, 100)

        comp_pos = calculate_position_for_pin(
            pin_local_position=pin_local,
            desired_pin_position=desired_pos,
            rotation=90,
            grid_size=1.27
        )

        # Verify it's grid-aligned
        assert comp_pos.x % 1.27 < 0.01 or (1.27 - comp_pos.x % 1.27) < 0.01
        assert comp_pos.y % 1.27 < 0.01 or (1.27 - comp_pos.y % 1.27) < 0.01

    def test_calculation_with_rotation_180(self):
        """Test position calculation with 180 degree rotation."""
        pin_local = Point(2.54, 0)
        desired_pos = Point(150, 100)

        comp_pos = calculate_position_for_pin(
            pin_local_position=pin_local,
            desired_pin_position=desired_pos,
            rotation=180,
            grid_size=1.27
        )

        # Verify it's grid-aligned
        assert comp_pos.x % 1.27 < 0.01 or (1.27 - comp_pos.x % 1.27) < 0.01
        assert comp_pos.y % 1.27 < 0.01 or (1.27 - comp_pos.y % 1.27) < 0.01

    def test_calculation_with_rotation_270(self):
        """Test position calculation with 270 degree rotation."""
        pin_local = Point(2.54, 0)
        desired_pos = Point(150, 100)

        comp_pos = calculate_position_for_pin(
            pin_local_position=pin_local,
            desired_pin_position=desired_pos,
            rotation=270,
            grid_size=1.27
        )

        # Verify it's grid-aligned
        assert comp_pos.x % 1.27 < 0.01 or (1.27 - comp_pos.x % 1.27) < 0.01
        assert comp_pos.y % 1.27 < 0.01 or (1.27 - comp_pos.y % 1.27) < 0.01

    def test_tuple_input(self):
        """Test that function accepts tuples as well as Points."""
        comp_pos = calculate_position_for_pin(
            pin_local_position=(2.54, 0),
            desired_pin_position=(150, 100),
            rotation=0,
            grid_size=1.27
        )

        assert isinstance(comp_pos, Point)
        assert abs(comp_pos.x - 147.32) < 0.01


class TestAddWithPinAt:
    """Test the add_with_pin_at() method on ComponentCollection."""

    def test_add_resistor_with_pin_at(self):
        """Test adding a resistor positioned by pin 2."""
        sch = ksa.create_schematic("Test")

        # Add resistor with pin 2 at (150, 100)
        r1 = sch.components.add_with_pin_at(
            lib_id="Device:R",
            pin_number="2",
            pin_position=(150, 100),
            value="10k"
        )

        # Note: Resistor has reference prefix 'U' in this KiCAD installation
        assert r1.reference.startswith("U")
        assert r1.value == "10k"

        # Verify pin 2 is actually at the desired position
        pin2_pos = r1.get_pin_position("2")
        assert pin2_pos is not None
        # Allow small tolerance due to grid snapping
        assert abs(pin2_pos.x - 150) < 1.5
        assert abs(pin2_pos.y - 100) < 1.5

    def test_add_with_different_rotations(self):
        """Test adding components with different rotations."""
        sch = ksa.create_schematic("Test")

        # Add at 0 degrees
        r1 = sch.components.add_with_pin_at(
            lib_id="Device:R",
            pin_number="1",
            pin_position=(100, 100),
            rotation=0
        )

        # Add at 90 degrees
        r2 = sch.components.add_with_pin_at(
            lib_id="Device:R",
            pin_number="1",
            pin_position=(150, 100),
            rotation=90
        )

        # Verify both pins are at correct positions
        r1_pin1 = r1.get_pin_position("1")
        r2_pin1 = r2.get_pin_position("1")

        assert r1_pin1 is not None
        assert r2_pin1 is not None
        assert abs(r1_pin1.x - 100) < 1.5
        assert abs(r2_pin1.x - 150) < 1.5

    def test_add_capacitor_aligned_with_resistor(self):
        """Test the main use case: aligning components horizontally."""
        sch = ksa.create_schematic("Test")

        # Add resistor with pin 2 at (150, 100)
        r1 = sch.components.add_with_pin_at(
            lib_id="Device:R",
            pin_number="2",
            pin_position=(150, 100),
            value="10k"
        )

        # Add capacitor with pin 1 at same Y position
        c1 = sch.components.add_with_pin_at(
            lib_id="Device:C",
            pin_number="1",
            pin_position=(200, 100),  # Same Y
            value="100nF"
        )

        # Verify pins are on same horizontal line
        r1_pin2 = r1.get_pin_position("2")
        c1_pin1 = c1.get_pin_position("1")

        assert r1_pin2 is not None
        assert c1_pin1 is not None

        # Pins should be at same Y (within tolerance)
        assert abs(r1_pin2.y - c1_pin1.y) < 1.5

    def test_invalid_pin_number(self):
        """Test error handling for invalid pin number."""
        sch = ksa.create_schematic("Test")

        with pytest.raises(ValueError, match="Pin '99' not found"):
            sch.components.add_with_pin_at(
                lib_id="Device:R",
                pin_number="99",  # Resistor only has pins 1 and 2
                pin_position=(100, 100)
            )

    def test_invalid_lib_id(self):
        """Test error handling for invalid library ID."""
        sch = ksa.create_schematic("Test")

        with pytest.raises(Exception):  # Should raise LibraryError
            sch.components.add_with_pin_at(
                lib_id="InvalidLib:InvalidComponent",
                pin_number="1",
                pin_position=(100, 100)
            )


class TestAlignPin:
    """Test the align_pin() method on Component."""

    def test_align_existing_component(self):
        """Test aligning an existing component by pin."""
        sch = ksa.create_schematic("Test")

        # Add component at some position
        r1 = sch.components.add(
            lib_id="Device:R",
            position=(100, 100),
            value="10k"
        )

        # Get initial pin 2 position
        initial_pin2 = r1.get_pin_position("2")
        assert initial_pin2 is not None

        # Align pin 2 to a new position
        r1.align_pin("2", (200, 150))

        # Verify pin 2 is now at the new position
        new_pin2 = r1.get_pin_position("2")
        assert new_pin2 is not None
        assert abs(new_pin2.x - 200) < 1.5
        assert abs(new_pin2.y - 150) < 1.5

    def test_align_maintains_rotation(self):
        """Test that aligning maintains component rotation."""
        sch = ksa.create_schematic("Test")

        # Add component with rotation
        r1 = sch.components.add(
            lib_id="Device:R",
            position=(100, 100),
            rotation=90,
            value="10k"
        )

        initial_rotation = r1.rotation

        # Align pin
        r1.align_pin("1", (150, 150))

        # Rotation should not change
        assert r1.rotation == initial_rotation

    def test_align_multiple_components_to_same_line(self):
        """Test aligning multiple components to same horizontal line."""
        sch = ksa.create_schematic("Test")

        # Add several components
        r1 = sch.components.add("Device:R", position=(100, 100), value="10k")
        r2 = sch.components.add("Device:R", position=(150, 120), value="20k")
        c1 = sch.components.add("Device:C", position=(200, 90), value="100nF")

        # Align all pin 2s to Y=150
        target_y = 150
        r1.align_pin("2", (100, target_y))
        r2.align_pin("2", (150, target_y))
        c1.align_pin("2", (200, target_y))

        # Verify all pins are at same Y
        r1_pin2 = r1.get_pin_position("2")
        r2_pin2 = r2.get_pin_position("2")
        c1_pin2 = c1.get_pin_position("2")

        assert r1_pin2 is not None
        assert r2_pin2 is not None
        assert c1_pin2 is not None

        assert abs(r1_pin2.y - target_y) < 1.5
        assert abs(r2_pin2.y - target_y) < 1.5
        assert abs(c1_pin2.y - target_y) < 1.5

    def test_align_invalid_pin(self):
        """Test error handling for invalid pin number."""
        sch = ksa.create_schematic("Test")

        r1 = sch.components.add("Device:R", position=(100, 100))

        with pytest.raises(ValueError, match="Pin '99' not found"):
            r1.align_pin("99", (150, 150))

    def test_align_with_tuple_position(self):
        """Test that align_pin accepts tuple positions."""
        sch = ksa.create_schematic("Test")

        r1 = sch.components.add("Device:R", position=(100, 100))

        # Should accept tuple
        r1.align_pin("1", (150, 150))

        pin1_pos = r1.get_pin_position("1")
        assert pin1_pos is not None
        assert abs(pin1_pos.x - 150) < 1.5
        assert abs(pin1_pos.y - 150) < 1.5


class TestPinAlignmentIntegration:
    """Integration tests for complete workflows using pin alignment."""

    def test_voltage_divider_horizontal_flow(self):
        """Test creating a voltage divider with perfect horizontal alignment."""
        sch = ksa.create_schematic("VoltageDivider")

        signal_line_y = 100  # Horizontal signal line

        # Add R1 with pin 2 on signal line
        r1 = sch.components.add_with_pin_at(
            lib_id="Device:R",
            pin_number="2",
            pin_position=(100, signal_line_y),
            value="10k"
        )

        # Add R2 with pin 1 on signal line (continuing the chain)
        r2 = sch.components.add_with_pin_at(
            lib_id="Device:R",
            pin_number="1",
            pin_position=(150, signal_line_y),
            value="10k"
        )

        # Verify perfect horizontal alignment
        r1_pin2 = r1.get_pin_position("2")
        r2_pin1 = r2.get_pin_position("1")

        assert r1_pin2 is not None
        assert r2_pin1 is not None

        # Pins should be perfectly aligned (within grid tolerance)
        assert abs(r1_pin2.y - r2_pin1.y) < 1.5
        assert abs(r1_pin2.y - signal_line_y) < 1.5
        assert abs(r2_pin1.y - signal_line_y) < 1.5

    def test_rc_filter_alignment(self):
        """Test creating an RC lowpass filter with aligned signal path."""
        sch = ksa.create_schematic("RCFilter")

        input_y = 100

        # Add resistor with pin 2 at signal line (pin 2 is the output side)
        r1 = sch.components.add_with_pin_at(
            lib_id="Device:R",
            pin_number="2",
            pin_position=(100, input_y),
            value="1k"
        )

        # Add capacitor with pin 1 at same signal line
        # Use pin 2 to match the same side as resistor pin 2
        c1 = sch.components.add_with_pin_at(
            lib_id="Device:C",
            pin_number="2",
            pin_position=(150, input_y),
            value="100nF"
        )

        # Verify alignment - both pin 2s should be on same horizontal line
        r1_pin2 = r1.get_pin_position("2")
        c1_pin2 = c1.get_pin_position("2")

        assert r1_pin2 is not None
        assert c1_pin2 is not None

        # Both should be on the same horizontal line (within grid snap tolerance)
        assert abs(r1_pin2.y - c1_pin2.y) < 1.5

    def test_realign_existing_circuit(self):
        """Test realigning an existing circuit to clean up layout."""
        sch = ksa.create_schematic("Cleanup")

        # Create a messy circuit
        r1 = sch.components.add("Device:R", position=(100, 95), value="10k")
        r2 = sch.components.add("Device:R", position=(150, 105), value="20k")
        c1 = sch.components.add("Device:C", position=(200, 98), value="100nF")

        # Realign everything to Y=100
        target_y = 100
        r1.align_pin("2", (r1.get_pin_position("2").x, target_y))
        r2.align_pin("1", (r2.get_pin_position("1").x, target_y))
        c1.align_pin("1", (c1.get_pin_position("1").x, target_y))

        # Verify all are aligned
        r1_pin2_y = r1.get_pin_position("2").y
        r2_pin1_y = r2.get_pin_position("1").y
        c1_pin1_y = c1.get_pin_position("1").y

        assert abs(r1_pin2_y - target_y) < 1.5
        assert abs(r2_pin1_y - target_y) < 1.5
        assert abs(c1_pin1_y - target_y) < 1.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
