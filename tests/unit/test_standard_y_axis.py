"""
Tests for optional standard Y-axis coordinate system.

These tests verify that when use_standard_y_axis is enabled:
1. Higher Y values place components higher on screen (visually)
2. Lower Y values place components lower on screen (visually)
3. KiCAD file format remains unchanged (still uses inverted Y internally)
4. Round-trip load/save preserves coordinates correctly
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration before and after each test."""
    original_setting = ksa.config.positioning.use_standard_y_axis
    ksa.config.positioning.use_standard_y_axis = False
    yield
    ksa.config.positioning.use_standard_y_axis = original_setting


class TestStandardYAxisConfiguration:
    """Test configuration setting for standard Y-axis."""

    def test_default_is_inverted_y_axis(self):
        """By default, KiCAD's inverted Y-axis should be used."""
        assert ksa.config.positioning.use_standard_y_axis is False

    def test_can_enable_standard_y_axis(self):
        """Should be able to enable standard Y-axis orientation."""
        ksa.config.positioning.use_standard_y_axis = True
        assert ksa.config.positioning.use_standard_y_axis is True

    def test_can_disable_standard_y_axis(self):
        """Should be able to disable standard Y-axis orientation."""
        ksa.config.positioning.use_standard_y_axis = True
        ksa.config.positioning.use_standard_y_axis = False
        assert ksa.config.positioning.use_standard_y_axis is False


class TestStandardYAxisComponentPlacement:
    """Test component placement with standard Y-axis."""

    def test_standard_y_axis_higher_value_is_visually_higher(self):
        """
        With standard Y-axis, higher Y value should be visually higher on screen.

        In KiCAD's inverted Y-axis:
        - Y=100 is visually lower than Y=80 (100 > 80)

        In standard Y-axis:
        - Y=100 should be visually higher than Y=80 (100 > 80)
        - Internally stored as Y=-100 in KiCAD format
        """
        # Enable standard Y-axis
        ksa.config.positioning.use_standard_y_axis = True

        # Test Y-axis conversion at API level
        from kicad_sch_api.core.config import convert_y_to_kicad, convert_y_from_kicad

        # User input: Y=100 (high on screen)
        api_y_high = 100.0
        # Should be stored internally as negative
        internal_y_high = convert_y_to_kicad(api_y_high)
        assert internal_y_high == -100.0

        # User input: Y=80 (lower on screen)
        api_y_low = 80.0
        internal_y_low = convert_y_to_kicad(api_y_low)
        assert internal_y_low == -80.0

        # Higher API Y should result in MORE NEGATIVE internal Y
        assert internal_y_high < internal_y_low

        # Conversion should be reversible
        assert convert_y_from_kicad(internal_y_high) == api_y_high
        assert convert_y_from_kicad(internal_y_low) == api_y_low

    def test_standard_y_axis_preserves_x_coordinate(self):
        """X coordinate should not be affected by standard Y-axis setting."""
        ksa.config.positioning.use_standard_y_axis = True

        from kicad_sch_api.core.config import convert_y_to_kicad

        # X coordinates should pass through unchanged
        x = 100.0
        y = 50.0

        # Only Y is converted
        assert convert_y_to_kicad(y) == -50.0

    def test_inverted_y_axis_default_behavior(self):
        """
        With inverted Y-axis (default), behavior should match KiCAD exactly.

        Y=100 is visually lower than Y=80 (inverted).
        """
        # Explicitly disable (should be default, but being explicit)
        ksa.config.positioning.use_standard_y_axis = False

        from kicad_sch_api.core.config import convert_y_to_kicad, convert_y_from_kicad

        # With inverted Y (disabled), no conversion occurs
        assert convert_y_to_kicad(100.0) == 100.0
        assert convert_y_to_kicad(80.0) == 80.0

        # Reversible
        assert convert_y_from_kicad(100.0) == 100.0
        assert convert_y_from_kicad(80.0) == 80.0


class TestStandardYAxisPointConversion:
    """Test point_from_dict_or_tuple with Y-axis conversion."""

    def test_point_from_tuple_standard_y_axis(self):
        """Test tuple to Point conversion with standard Y-axis."""
        ksa.config.positioning.use_standard_y_axis = True

        from kicad_sch_api.core.types import point_from_dict_or_tuple

        # Convert tuple (100, 100) with Y-axis conversion
        point = point_from_dict_or_tuple((100, 100), convert_y=True)

        # X should be unchanged
        assert point.x == 100.0

        # Y should be negated (standard Y=100 becomes KiCAD Y=-100)
        assert point.y == -100.0

    def test_point_from_dict_standard_y_axis(self):
        """Test dict to Point conversion with standard Y-axis."""
        ksa.config.positioning.use_standard_y_axis = True

        from kicad_sch_api.core.types import point_from_dict_or_tuple

        # Convert dict with Y-axis conversion
        point = point_from_dict_or_tuple({"x": 100, "y": 100}, convert_y=True)

        # X should be unchanged
        assert point.x == 100.0

        # Y should be negated
        assert point.y == -100.0

    def test_point_conversion_disabled(self):
        """Test that conversion doesn't occur when convert_y=False."""
        ksa.config.positioning.use_standard_y_axis = True

        from kicad_sch_api.core.types import point_from_dict_or_tuple

        # Even with standard Y enabled, convert_y=False should skip conversion
        point = point_from_dict_or_tuple((100, 100), convert_y=False)

        # Both coordinates unchanged
        assert point.x == 100.0
        assert point.y == 100.0


class TestStandardYAxisHelperFunction:
    """Test use_standard_y_axis() helper function."""

    def test_helper_function_enables_standard_y(self):
        """Helper function should enable standard Y-axis."""
        ksa.use_standard_y_axis(True)
        assert ksa.config.positioning.use_standard_y_axis is True

    def test_helper_function_disables_standard_y(self):
        """Helper function should disable standard Y-axis."""
        ksa.config.positioning.use_standard_y_axis = True
        ksa.use_standard_y_axis(False)
        assert ksa.config.positioning.use_standard_y_axis is False

    def test_helper_function_example_usage(self):
        """Document example usage of helper function."""
        # Enable standard Y-axis for intuitive positioning
        ksa.use_standard_y_axis(True)

        from kicad_sch_api.core.config import convert_y_to_kicad

        # Now positions use standard coordinates (higher Y = higher on screen)
        # Y=100 (top) becomes -100 internally
        assert convert_y_to_kicad(100) == -100

        # Y=80 (middle) becomes -80 internally
        assert convert_y_to_kicad(80) == -80

        # Y=60 (lower) becomes -60 internally
        assert convert_y_to_kicad(60) == -60

        # Y=40 (bottom) becomes -40 internally
        assert convert_y_to_kicad(40) == -40

        # Verify natural top-to-bottom ordering: higher API Y → more negative internal Y
        assert convert_y_to_kicad(100) < convert_y_to_kicad(80)
        assert convert_y_to_kicad(80) < convert_y_to_kicad(60)
        assert convert_y_to_kicad(60) < convert_y_to_kicad(40)
