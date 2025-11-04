#!/usr/bin/env python3
"""
Unit tests for rotation-aware component property positioning.

Tests that Reference and Value text fields are positioned correctly
at all rotation angles (0°, 90°, 180°, 270°).
"""

import pytest
import math
from kicad_sch_api.core.config import config


class TestRotationAwarePositioning:
    """Test property position calculation with component rotation."""

    @pytest.fixture
    def component_pos(self):
        """Standard component position for testing."""
        return (100.0, 100.0)

    def test_reference_position_at_0_degrees(self, component_pos):
        """Test Reference positioning at 0° rotation."""
        x, y, rotation = config.get_property_position(
            "Reference", component_pos, offset_index=0, component_rotation=0
        )

        # At 0°, should use base offsets directly
        expected_x = component_pos[0] + config.properties.reference_x
        expected_y = component_pos[1] + config.properties.reference_y

        assert abs(x - expected_x) < 0.01, f"X position mismatch at 0°: {x} vs {expected_x}"
        assert abs(y - expected_y) < 0.01, f"Y position mismatch at 0°: {y} vs {expected_y}"
        assert rotation == 0, "Text rotation should be 0° (readable)"

    def test_reference_position_at_90_degrees(self, component_pos):
        """Test Reference positioning at 90° rotation."""
        x, y, rotation = config.get_property_position(
            "Reference", component_pos, offset_index=0, component_rotation=90
        )

        # At 90°, offsets should be rotated clockwise
        # Original offset: (2.54, -1.27)
        # After 90° clockwise: (1.27, 2.54)
        base_dx = config.properties.reference_x
        base_dy = config.properties.reference_y
        rotation_rad = math.radians(-90)  # Clockwise
        expected_dx = base_dx * math.cos(rotation_rad) - base_dy * math.sin(rotation_rad)
        expected_dy = base_dx * math.sin(rotation_rad) + base_dy * math.cos(rotation_rad)
        expected_x = component_pos[0] + expected_dx
        expected_y = component_pos[1] + expected_dy

        assert abs(x - expected_x) < 0.01, f"X position mismatch at 90°: {x} vs {expected_x}"
        assert abs(y - expected_y) < 0.01, f"Y position mismatch at 90°: {y} vs {expected_y}"
        assert rotation == 0, "Text rotation should be 0° (readable)"

    def test_reference_position_at_180_degrees(self, component_pos):
        """Test Reference positioning at 180° rotation."""
        x, y, rotation = config.get_property_position(
            "Reference", component_pos, offset_index=0, component_rotation=180
        )

        # At 180°, offsets should be rotated 180°
        # Original offset: (2.54, -1.27)
        # After 180°: (-2.54, 1.27)
        base_dx = config.properties.reference_x
        base_dy = config.properties.reference_y
        rotation_rad = math.radians(-180)  # Clockwise
        expected_dx = base_dx * math.cos(rotation_rad) - base_dy * math.sin(rotation_rad)
        expected_dy = base_dx * math.sin(rotation_rad) + base_dy * math.cos(rotation_rad)
        expected_x = component_pos[0] + expected_dx
        expected_y = component_pos[1] + expected_dy

        assert abs(x - expected_x) < 0.01, f"X position mismatch at 180°: {x} vs {expected_x}"
        assert abs(y - expected_y) < 0.01, f"Y position mismatch at 180°: {y} vs {expected_y}"
        assert rotation == 0, "Text rotation should be 0° (readable)"

    def test_reference_position_at_270_degrees(self, component_pos):
        """Test Reference positioning at 270° rotation."""
        x, y, rotation = config.get_property_position(
            "Reference", component_pos, offset_index=0, component_rotation=270
        )

        # At 270°, offsets should be rotated 270° clockwise
        # Original offset: (2.54, -1.27)
        # After 270° clockwise: (-1.27, -2.54)
        base_dx = config.properties.reference_x
        base_dy = config.properties.reference_y
        rotation_rad = math.radians(-270)  # Clockwise
        expected_dx = base_dx * math.cos(rotation_rad) - base_dy * math.sin(rotation_rad)
        expected_dy = base_dx * math.sin(rotation_rad) + base_dy * math.cos(rotation_rad)
        expected_x = component_pos[0] + expected_dx
        expected_y = component_pos[1] + expected_dy

        assert abs(x - expected_x) < 0.01, f"X position mismatch at 270°: {x} vs {expected_x}"
        assert abs(y - expected_y) < 0.01, f"Y position mismatch at 270°: {y} vs {expected_y}"
        assert rotation == 0, "Text rotation should be 0° (readable)"

    def test_value_position_at_0_degrees(self, component_pos):
        """Test Value positioning at 0° rotation."""
        x, y, rotation = config.get_property_position(
            "Value", component_pos, offset_index=0, component_rotation=0
        )

        # At 0°, should use base offsets directly
        expected_x = component_pos[0] + config.properties.value_x
        expected_y = component_pos[1] + config.properties.value_y

        assert abs(x - expected_x) < 0.01, f"X position mismatch at 0°: {x} vs {expected_x}"
        assert abs(y - expected_y) < 0.01, f"Y position mismatch at 0°: {y} vs {expected_y}"
        assert rotation == 0, "Text rotation should be 0° (readable)"

    def test_value_position_at_90_degrees(self, component_pos):
        """Test Value positioning at 90° rotation."""
        x, y, rotation = config.get_property_position(
            "Value", component_pos, offset_index=0, component_rotation=90
        )

        # At 90°, offsets should be rotated clockwise
        base_dx = config.properties.value_x
        base_dy = config.properties.value_y
        rotation_rad = math.radians(-90)  # Clockwise
        expected_dx = base_dx * math.cos(rotation_rad) - base_dy * math.sin(rotation_rad)
        expected_dy = base_dx * math.sin(rotation_rad) + base_dy * math.cos(rotation_rad)
        expected_x = component_pos[0] + expected_dx
        expected_y = component_pos[1] + expected_dy

        assert abs(x - expected_x) < 0.01, f"X position mismatch at 90°: {x} vs {expected_x}"
        assert abs(y - expected_y) < 0.01, f"Y position mismatch at 90°: {y} vs {expected_y}"
        assert rotation == 0, "Text rotation should be 0° (readable)"

    @pytest.mark.parametrize("angle", [0, 90, 180, 270])
    def test_text_always_readable(self, component_pos, angle):
        """Test that text rotation is always 0° (readable) regardless of component rotation."""
        _, _, text_rotation = config.get_property_position(
            "Reference", component_pos, offset_index=0, component_rotation=angle
        )
        assert text_rotation == 0, f"Text should be readable (0°) at component rotation {angle}°"

    @pytest.mark.parametrize("angle", [0, 90, 180, 270])
    def test_position_uniqueness(self, component_pos, angle):
        """Test that each rotation produces a unique position."""
        positions = []
        for rotation_angle in [0, 90, 180, 270]:
            x, y, _ = config.get_property_position(
                "Reference", component_pos, offset_index=0, component_rotation=rotation_angle
            )
            positions.append((round(x, 2), round(y, 2)))

        # All 4 positions should be unique
        assert len(set(positions)) == 4, f"Positions should be unique for each rotation: {positions}"

    def test_footprint_position_unaffected_by_rotation(self, component_pos):
        """Test that Footprint property positioning is not affected by component rotation.

        Footprint uses its own rotation (90°) and shouldn't change based on component rotation.
        """
        # Footprint should have same position at all component rotations
        for angle in [0, 90, 180, 270]:
            x, y, rot = config.get_property_position(
                "Footprint", component_pos, offset_index=0, component_rotation=angle
            )
            # Footprint always at same offset from component
            assert abs(x - (component_pos[0] - 1.778)) < 0.01
            assert abs(y - component_pos[1]) < 0.01
            assert rot == config.properties.footprint_rotation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
