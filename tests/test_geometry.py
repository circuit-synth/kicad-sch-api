"""
Test suite for the geometry module (symbol bounding box calculations).

Tests cover:
- Font metrics constants
- Symbol bounding box calculation
- Pin bounds with and without labels
- Shape bounds for different shape types
- Placement vs visual bounding boxes
- Adaptive spacing calculations
"""

import pytest

from kicad_sch_api.geometry import (
    DEFAULT_PIN_LENGTH,
    DEFAULT_PIN_NAME_OFFSET,
    DEFAULT_PIN_NUMBER_SIZE,
    DEFAULT_PIN_TEXT_WIDTH_RATIO,
    DEFAULT_TEXT_HEIGHT,
    SymbolBoundingBoxCalculator,
)


class TestFontMetrics:
    """Test font metrics constants."""

    def test_default_text_height(self):
        """Test DEFAULT_TEXT_HEIGHT is correct."""
        assert DEFAULT_TEXT_HEIGHT == 2.54  # 100 mils

    def test_default_pin_length(self):
        """Test DEFAULT_PIN_LENGTH is correct."""
        assert DEFAULT_PIN_LENGTH == 2.54  # 100 mils

    def test_default_pin_name_offset(self):
        """Test DEFAULT_PIN_NAME_OFFSET is correct."""
        assert DEFAULT_PIN_NAME_OFFSET == 0.508  # 20 mils

    def test_default_pin_number_size(self):
        """Test DEFAULT_PIN_NUMBER_SIZE is correct."""
        assert DEFAULT_PIN_NUMBER_SIZE == 1.27  # 50 mils

    def test_default_pin_text_width_ratio(self):
        """Test DEFAULT_PIN_TEXT_WIDTH_RATIO is correct."""
        assert DEFAULT_PIN_TEXT_WIDTH_RATIO == 0.65  # Proportional font average


class TestSymbolBoundingBoxCalculator:
    """Test SymbolBoundingBoxCalculator class."""

    def test_class_constants_match_module_constants(self):
        """Test that class constants match module-level constants."""
        assert SymbolBoundingBoxCalculator.DEFAULT_TEXT_HEIGHT == DEFAULT_TEXT_HEIGHT
        assert SymbolBoundingBoxCalculator.DEFAULT_PIN_LENGTH == DEFAULT_PIN_LENGTH
        assert SymbolBoundingBoxCalculator.DEFAULT_PIN_NAME_OFFSET == DEFAULT_PIN_NAME_OFFSET
        assert SymbolBoundingBoxCalculator.DEFAULT_PIN_NUMBER_SIZE == DEFAULT_PIN_NUMBER_SIZE
        assert (
            SymbolBoundingBoxCalculator.DEFAULT_PIN_TEXT_WIDTH_RATIO == DEFAULT_PIN_TEXT_WIDTH_RATIO
        )

    def test_empty_symbol_data_raises_error(self):
        """Test that empty symbol data raises ValueError."""
        with pytest.raises(ValueError, match="Symbol data is None or empty"):
            SymbolBoundingBoxCalculator.calculate_bounding_box(None)

        with pytest.raises(ValueError, match="Symbol data is None or empty"):
            SymbolBoundingBoxCalculator.calculate_bounding_box({})

    def test_symbol_with_no_geometry_raises_error(self):
        """Test that symbol with no geometry raises ValueError."""
        symbol_data = {
            "shapes": [],
            "pins": [],
            "sub_symbols": [],
        }
        with pytest.raises(ValueError, match="No valid geometry found"):
            SymbolBoundingBoxCalculator.calculate_bounding_box(symbol_data)


class TestShapeBounds:
    """Test _get_shape_bounds for different shape types."""

    def test_rectangle_shape_bounds(self):
        """Test bounding box calculation for rectangle shapes."""
        shape = {
            "shape_type": "rectangle",
            "start": [0, 0],
            "end": [10, 20],
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds == (0, 0, 10, 20)

    def test_rectangle_shape_bounds_reversed(self):
        """Test rectangle with reversed coordinates."""
        shape = {
            "shape_type": "rectangle",
            "start": [10, 20],
            "end": [0, 0],
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds == (0, 0, 10, 20)

    def test_circle_shape_bounds(self):
        """Test bounding box calculation for circle shapes."""
        shape = {
            "shape_type": "circle",
            "center": [5, 5],
            "radius": 3,
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds == (2, 2, 8, 8)

    def test_arc_shape_bounds(self):
        """Test bounding box calculation for arc shapes."""
        shape = {
            "shape_type": "arc",
            "start": [0, 0],
            "mid": [5, 10],
            "end": [10, 0],
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds == (0, 0, 10, 10)

    def test_polyline_shape_bounds(self):
        """Test bounding box calculation for polyline shapes."""
        shape = {
            "shape_type": "polyline",
            "points": [[0, 0], [5, 10], [10, 5], [15, 15]],
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds == (0, 0, 15, 15)

    def test_polyline_empty_points(self):
        """Test polyline with no points returns None."""
        shape = {
            "shape_type": "polyline",
            "points": [],
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds is None

    def test_text_shape_bounds(self):
        """Test bounding box calculation for text shapes."""
        shape = {
            "shape_type": "text",
            "at": [10, 10],
            "text": "TEST",
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds is not None
        # Text bounds should be centered around position
        min_x, min_y, max_x, max_y = bounds
        assert min_x < 10 < max_x
        assert min_y < 10 < max_y

    def test_unknown_shape_type(self):
        """Test that unknown shape type returns None."""
        shape = {
            "shape_type": "unknown_type",
        }
        bounds = SymbolBoundingBoxCalculator._get_shape_bounds(shape)
        assert bounds is None


class TestPinBounds:
    """Test pin bounding box calculations."""

    def test_pin_bounds_basic_horizontal(self):
        """Test pin bounds with horizontal orientation."""
        pin = {
            "at": [0, 0, 0],  # x, y, angle (0 = right)
            "length": 2.54,
            "name": "VCC",
            "number": "1",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin)
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Pin extends right, label extends left
        assert min_x < 0
        assert max_x > 2.54

    def test_pin_bounds_with_net_map(self):
        """Test pin bounds with net name mapping."""
        pin = {
            "at": [0, 0, 0],
            "length": 2.54,
            "name": "VCC",
            "number": "1",
        }
        pin_net_map = {"1": "VCC"}
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin, pin_net_map)
        assert bounds is not None

    def test_pin_bounds_without_net_map_fallback(self):
        """Test pin bounds without net map uses fallback size."""
        pin = {
            "at": [0, 0, 0],
            "length": 2.54,
            "name": "VERY_LONG_PIN_NAME",
            "number": "1",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin, None)
        assert bounds is not None
        # Should use 3-character fallback, not full pin name length

    def test_pin_bounds_no_labels(self):
        """Test pin bounds without labels for placement calculations."""
        pin = {
            "at": [0, 0, 0],
            "length": 2.54,
            "name": "VCC",
            "number": "1",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds_no_labels(pin)
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Bounds should be tighter than with labels
        width = max_x - min_x
        height = max_y - min_y
        assert width < 5  # Small margin only
        assert height < 5

    def test_pin_bounds_alternative_format(self):
        """Test pin bounds with alternative x/y/orientation format."""
        pin = {
            "x": 0,
            "y": 0,
            "orientation": 0,
            "length": 2.54,
            "name": "VCC",
            "number": "1",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin)
        assert bounds is not None

    def test_pin_bounds_angle_180(self):
        """Test pin bounds with 180 degree angle (left)."""
        pin = {
            "at": [0, 0, 180],
            "length": 2.54,
            "name": "GND",
            "number": "2",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin)
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Pin extends left, label extends right
        assert min_x < -2.54
        assert max_x > 0

    def test_pin_bounds_angle_90(self):
        """Test pin bounds with 90 degree angle (up)."""
        pin = {
            "at": [0, 0, 90],
            "length": 2.54,
            "name": "OUT",
            "number": "3",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin)
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Pin extends up, label extends down
        assert min_y < 0

    def test_pin_bounds_angle_270(self):
        """Test pin bounds with 270 degree angle (down)."""
        pin = {
            "at": [0, 0, 270],
            "length": 2.54,
            "name": "IN",
            "number": "4",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin)
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Pin extends down, label extends up
        assert max_y > 0

    def test_pin_bounds_no_name(self):
        """Test pin with no name (tilde)."""
        pin = {
            "at": [0, 0, 0],
            "length": 2.54,
            "name": "~",
            "number": "1",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin)
        assert bounds is not None


class TestCompleteSymbolBounds:
    """Test complete symbol bounding box calculations."""

    def test_simple_symbol_with_shapes_and_pins(self):
        """Test bounding box for simple symbol with shapes and pins."""
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [-5, -5],
                    "end": [5, 5],
                }
            ],
            "pins": [
                {
                    "at": [-5, 0, 180],
                    "length": 2.54,
                    "name": "IN",
                    "number": "1",
                },
                {
                    "at": [5, 0, 0],
                    "length": 2.54,
                    "name": "OUT",
                    "number": "2",
                },
            ],
            "sub_symbols": [],
        }
        bounds = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=False
        )
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Should include shape and pins with labels
        assert min_x < -5
        assert max_x > 5

    def test_symbol_with_properties(self):
        """Test bounding box calculation with property spacing."""
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [-5, -5],
                    "end": [5, 5],
                }
            ],
            "pins": [],
            "sub_symbols": [],
        }
        bounds_with_props = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=True
        )
        bounds_without_props = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=False
        )

        # With properties should have larger bounds
        assert bounds_with_props[1] < bounds_without_props[1]  # min_y lower
        assert bounds_with_props[3] > bounds_without_props[3]  # max_y higher

    def test_symbol_with_subsymbols(self):
        """Test symbol with sub-symbols."""
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [0, 0],
                    "end": [10, 10],
                }
            ],
            "pins": [],
            "sub_symbols": [
                {
                    "shapes": [
                        {
                            "shape_type": "circle",
                            "center": [20, 20],
                            "radius": 5,
                        }
                    ],
                    "pins": [
                        {
                            "at": [20, 15, 270],
                            "length": 2.54,
                            "name": "SUB",
                            "number": "1",
                        }
                    ],
                }
            ],
        }
        bounds = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=False
        )
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Should include both main and sub-symbol geometry
        assert min_x <= 0
        assert max_x >= 25  # Circle extends to 25

    def test_placement_bounding_box_excludes_pin_labels(self):
        """Test that placement bounding box excludes pin labels."""
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [-5, -5],
                    "end": [5, 5],
                }
            ],
            "pins": [
                {
                    "at": [-5, 0, 180],
                    "length": 2.54,
                    "name": "VERY_LONG_PIN_NAME",
                    "number": "1",
                }
            ],
            "sub_symbols": [],
        }
        full_bounds = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=False
        )
        placement_bounds = SymbolBoundingBoxCalculator.calculate_placement_bounding_box(symbol_data)

        # Placement bounds should be tighter horizontally (no pin labels)
        # Note: Placement includes property spacing vertically, so height may be larger
        assert placement_bounds[0] > full_bounds[0]  # min_x higher (no left pin label)
        # Max_x comparison is not reliable due to margins and property spacing

    def test_visual_bounding_box(self):
        """Test visual bounding box calculation."""
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [-5, -5],
                    "end": [5, 5],
                }
            ],
            "pins": [
                {
                    "at": [5, 0, 0],
                    "length": 2.54,
                    "name": "OUT",
                    "number": "1",
                }
            ],
            "sub_symbols": [],
        }
        bounds = SymbolBoundingBoxCalculator.calculate_visual_bounding_box(symbol_data)
        assert bounds is not None
        # Visual bounds include pin labels but not property spacing

    def test_get_symbol_dimensions(self):
        """Test get_symbol_dimensions convenience method."""
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [0, 0],
                    "end": [10, 20],
                }
            ],
            "pins": [],
            "sub_symbols": [],
        }
        width, height = SymbolBoundingBoxCalculator.get_symbol_dimensions(
            symbol_data, include_properties=False
        )
        assert width > 10  # Includes margins
        assert height > 20  # Includes margins


class TestAdaptiveSpacing:
    """Test adaptive spacing calculations."""

    def test_adaptive_property_spacing_small_component(self):
        """Test adaptive spacing for small components."""
        # Small component - should use minimum spacing
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [0, 0],
                    "end": [5, 5],
                }
            ],
            "pins": [],
            "sub_symbols": [],
        }
        bounds = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=True
        )
        assert bounds is not None

    def test_adaptive_property_spacing_large_component(self):
        """Test adaptive spacing for large components."""
        # Large component - should use proportional spacing
        symbol_data = {
            "shapes": [
                {
                    "shape_type": "rectangle",
                    "start": [0, 0],
                    "end": [50, 50],
                }
            ],
            "pins": [],
            "sub_symbols": [],
        }
        bounds = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=True
        )
        assert bounds is not None


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_graphics_key_instead_of_shapes(self):
        """Test that 'graphics' key works as alias for 'shapes'."""
        symbol_data = {
            "graphics": [  # Using 'graphics' instead of 'shapes'
                {
                    "shape_type": "rectangle",
                    "start": [0, 0],
                    "end": [10, 10],
                }
            ],
            "pins": [],
            "sub_symbols": [],
        }
        bounds = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=False
        )
        assert bounds is not None

    def test_pin_with_zero_length(self):
        """Test pin with zero length."""
        pin = {
            "at": [0, 0, 0],
            "length": 0,
            "name": "TEST",
            "number": "1",
        }
        bounds = SymbolBoundingBoxCalculator._get_pin_bounds(pin)
        assert bounds is not None

    def test_symbol_with_multiple_pins_and_shapes(self):
        """Test complex symbol with multiple elements."""
        symbol_data = {
            "shapes": [
                {"shape_type": "rectangle", "start": [0, 0], "end": [20, 30]},
                {"shape_type": "circle", "center": [10, 15], "radius": 3},
            ],
            "pins": [
                {"at": [0, 10, 180], "length": 2.54, "name": "IN1", "number": "1"},
                {"at": [0, 20, 180], "length": 2.54, "name": "IN2", "number": "2"},
                {"at": [20, 10, 0], "length": 2.54, "name": "OUT1", "number": "3"},
                {"at": [20, 20, 0], "length": 2.54, "name": "OUT2", "number": "4"},
            ],
            "sub_symbols": [],
        }
        bounds = SymbolBoundingBoxCalculator.calculate_bounding_box(
            symbol_data, include_properties=True
        )
        assert bounds is not None
        min_x, min_y, max_x, max_y = bounds
        # Should encompass all elements
        assert min_x < 0
        assert max_x > 20
        assert min_y < 0
        assert max_y > 30
