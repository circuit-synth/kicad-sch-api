#!/usr/bin/env python3
"""
Tests for grid snapping functionality.

Ensures all components and pins are properly aligned to KiCAD's 1.27mm grid.
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.geometry import snap_to_grid


class TestGridSnapping:
    """Test grid snapping utilities and component placement."""

    def test_snap_to_grid_basic(self):
        """Test basic grid snapping functionality."""
        grid_size = 1.27  # KiCAD's 50mil grid

        # Test various off-grid positions
        test_cases = [
            ((0, 0), (0, 0)),  # Already on grid
            ((1.27, 2.54), (1.27, 2.54)),  # Already on grid
            ((1.0, 2.0), (1.27, 2.54)),  # Should snap to nearest
            ((100.5, 99.8), (100.33, 100.33)),  # Off-grid positions
            ((0.6, 0.7), (0.0, 1.27)),  # Small offsets
            ((-1.0, -2.0), (-1.27, -2.54)),  # Negative coordinates
        ]

        for input_pos, expected_pos in test_cases:
            result = snap_to_grid(input_pos, grid_size)

            # Check result is close to expected (within 0.001mm tolerance)
            assert (
                abs(result[0] - expected_pos[0]) < 0.001
            ), f"X snap failed for {input_pos}: got {result[0]}, expected {expected_pos[0]}"
            assert (
                abs(result[1] - expected_pos[1]) < 0.001
            ), f"Y snap failed for {input_pos}: got {result[1]}, expected {expected_pos[1]}"

            # Verify result is actually on grid
            x_grid_units = result[0] / grid_size
            y_grid_units = result[1] / grid_size

            assert (
                abs(x_grid_units - round(x_grid_units)) < 0.001
            ), f"X not on grid: {result[0]} = {x_grid_units} grid units"
            assert (
                abs(y_grid_units - round(y_grid_units)) < 0.001
            ), f"Y not on grid: {result[1]} = {y_grid_units} grid units"

    def test_component_position_snapping(self):
        """Test that components are automatically placed on grid."""
        sch = ksa.create_schematic("Grid Component Test")

        # Test off-grid component positions
        test_positions = [
            (100.5, 99.8),  # Slightly off-grid
            (50.123, 75.456),  # Very off-grid
            (25.4, 50.8),  # 1 inch, 2 inch (should be on grid already)
            (0.1, 0.2),  # Near origin
        ]

        grid_size = 1.27

        for i, pos in enumerate(test_positions):
            # Add component at off-grid position
            ref = f"R{i+1}"
            component = sch.components.add("Device:R", ref, "10k", pos)

            # Verify component position is on grid
            actual_pos = component.position

            x_grid_units = actual_pos.x / grid_size
            y_grid_units = actual_pos.y / grid_size

            assert (
                abs(x_grid_units - round(x_grid_units)) < 0.001
            ), f"{ref} X not on grid: {actual_pos.x} = {x_grid_units} grid units"
            assert (
                abs(y_grid_units - round(y_grid_units)) < 0.001
            ), f"{ref} Y not on grid: {actual_pos.y} = {y_grid_units} grid units"

            # Verify it snapped to the nearest grid point
            expected_pos = snap_to_grid(pos, grid_size)
            assert abs(actual_pos.x - expected_pos[0]) < 0.001, f"{ref} X position mismatch"
            assert abs(actual_pos.y - expected_pos[1]) < 0.001, f"{ref} Y position mismatch"

    def test_pin_positions_on_grid(self):
        """Test that calculated pin positions are on grid."""
        sch = ksa.create_schematic("Pin Grid Test")

        # Add component at grid position
        resistor = sch.components.add("Device:R", "R1", "10k", (101.6, 101.6))  # 80 grid units

        # Get pin positions
        pin1_pos = sch.get_component_pin_position("R1", "1")
        pin2_pos = sch.get_component_pin_position("R1", "2")

        assert pin1_pos is not None, "Pin 1 position should be calculable"
        assert pin2_pos is not None, "Pin 2 position should be calculable"

        grid_size = 1.27

        # Verify pin positions are on grid
        for pin_name, pin_pos in [("Pin 1", pin1_pos), ("Pin 2", pin2_pos)]:
            x_grid_units = pin_pos.x / grid_size
            y_grid_units = pin_pos.y / grid_size

            assert (
                abs(x_grid_units - round(x_grid_units)) < 0.001
            ), f"{pin_name} X not on grid: {pin_pos.x} = {x_grid_units} grid units"
            assert (
                abs(y_grid_units - round(y_grid_units)) < 0.001
            ), f"{pin_name} Y not on grid: {pin_pos.y} = {y_grid_units} grid units"

    def test_component_rotation_preserves_grid(self):
        """Test that component rotation maintains grid alignment."""
        sch = ksa.create_schematic("Rotation Grid Test")

        # Add component on grid
        resistor = sch.components.add("Device:R", "R1", "10k", (127, 127))  # 100 grid units

        grid_size = 1.27

        # Test different rotations
        for rotation in [0, 90, 180, 270]:
            resistor.rotation = rotation

            # Get pin positions for this rotation
            pin1_pos = sch.get_component_pin_position("R1", "1")
            pin2_pos = sch.get_component_pin_position("R1", "2")

            # Verify pins remain on grid after rotation
            for pin_name, pin_pos in [("Pin 1", pin1_pos), ("Pin 2", pin2_pos)]:
                x_grid_units = pin_pos.x / grid_size
                y_grid_units = pin_pos.y / grid_size

                assert (
                    abs(x_grid_units - round(x_grid_units)) < 0.001
                ), f"{pin_name} X not on grid at {rotation}°: {pin_pos.x} = {x_grid_units} grid units"
                assert (
                    abs(y_grid_units - round(y_grid_units)) < 0.001
                ), f"{pin_name} Y not on grid at {rotation}°: {pin_pos.y} = {y_grid_units} grid units"

    def test_multiple_components_grid_alignment(self):
        """Test that multiple components maintain proper grid spacing."""
        sch = ksa.create_schematic("Multiple Grid Test")

        # Add components with various spacings
        positions = [
            (50.8, 50.8),  # 40 grid units
            (76.2, 76.2),  # 60 grid units
            (101.6, 101.6),  # 80 grid units
            (127.0, 127.0),  # 100 grid units
        ]

        components = []
        for i, pos in enumerate(positions):
            comp = sch.components.add("Device:R", f"R{i+1}", "10k", pos)
            components.append(comp)

        grid_size = 1.27

        # Verify all components are on grid
        for comp in components:
            x_grid_units = comp.position.x / grid_size
            y_grid_units = comp.position.y / grid_size

            assert (
                abs(x_grid_units - round(x_grid_units)) < 0.001
            ), f"{comp.reference} X not on grid"
            assert (
                abs(y_grid_units - round(y_grid_units)) < 0.001
            ), f"{comp.reference} Y not on grid"

        # Verify reasonable spacing between components
        for i in range(len(components) - 1):
            comp1 = components[i]
            comp2 = components[i + 1]

            # Distance should be a multiple of grid size
            dx = abs(comp2.position.x - comp1.position.x)
            dy = abs(comp2.position.y - comp1.position.y)

            x_grid_diff = dx / grid_size
            y_grid_diff = dy / grid_size

            # Should be whole grid units apart
            assert (
                abs(x_grid_diff - round(x_grid_diff)) < 0.001
            ), f"Components not grid-aligned in X"
            assert (
                abs(y_grid_diff - round(y_grid_diff)) < 0.001
            ), f"Components not grid-aligned in Y"


class TestGridConstants:
    """Test grid size constants and calculations."""

    def test_kicad_grid_size(self):
        """Test that we're using correct KiCAD grid size."""
        grid_size = 1.27  # mm

        # Verify this equals 50 mils
        mils_per_mm = 39.3701  # 1mm = 39.3701 mils
        grid_in_mils = grid_size * mils_per_mm

        assert (
            abs(grid_in_mils - 50.0) < 0.1
        ), f"Grid should be 50 mils, got {grid_in_mils:.2f} mils"

    def test_common_kicad_spacings(self):
        """Test that common KiCAD spacings work with our grid."""
        grid_size = 1.27

        # Common KiCAD spacings (in mm)
        common_spacings = [
            2.54,  # 0.1 inch (2 grid units)
            5.08,  # 0.2 inch (4 grid units)
            7.62,  # 0.3 inch (6 grid units) - resistor pin span
            10.16,  # 0.4 inch (8 grid units)
            12.7,  # 0.5 inch (10 grid units)
            25.4,  # 1.0 inch (20 grid units)
        ]

        for spacing in common_spacings:
            grid_units = spacing / grid_size
            assert (
                abs(grid_units - round(grid_units)) < 0.001
            ), f"Spacing {spacing}mm = {grid_units} grid units (should be whole number)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
