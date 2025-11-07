"""
Unit tests for orthogonal routing functionality.

Tests the core routing algorithms for creating Manhattan-style wire routes
between component pins in KiCAD schematics.
"""

import pytest

from kicad_sch_api.core.types import Point
from kicad_sch_api.geometry import (
    CornerDirection,
    RoutingResult,
    create_orthogonal_routing,
    validate_routing_result,
)


class TestDirectRouting:
    """Test cases for direct routing when points are aligned."""

    def test_horizontal_direct_routing(self):
        """Test direct horizontal routing when Y coordinates are aligned."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 100.0)
        )

        assert result.is_direct
        assert len(result.segments) == 1
        assert result.corner is None

        start, end = result.segments[0]
        assert start.x == 100.0
        assert start.y == 100.0
        assert end.x == 150.0
        assert end.y == 100.0

        # Should validate correctly
        assert validate_routing_result(result)

    def test_vertical_direct_routing(self):
        """Test direct vertical routing when X coordinates are aligned."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(100.0, 150.0)
        )

        assert result.is_direct
        assert len(result.segments) == 1
        assert result.corner is None

        start, end = result.segments[0]
        assert start.x == 100.0
        assert start.y == 100.0
        assert end.x == 100.0
        assert end.y == 150.0

        # Should validate correctly
        assert validate_routing_result(result)

    def test_direct_routing_negative_direction(self):
        """Test direct routing works in negative direction (right-to-left, bottom-to-top)."""
        # Right to left
        result = create_orthogonal_routing(
            Point(150.0, 100.0),
            Point(100.0, 100.0)
        )
        assert result.is_direct
        assert len(result.segments) == 1

        # Bottom to top (remember: lower Y = visually higher in KiCAD!)
        result = create_orthogonal_routing(
            Point(100.0, 150.0),  # Higher Y = visually lower
            Point(100.0, 100.0)   # Lower Y = visually higher
        )
        assert result.is_direct
        assert len(result.segments) == 1

    def test_zero_distance_routing(self):
        """Test routing between same point (zero distance)."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(100.0, 100.0)
        )

        assert result.is_direct
        assert len(result.segments) == 1

        start, end = result.segments[0]
        assert start.x == end.x == 100.0
        assert start.y == end.y == 100.0


class TestLShapedRouting:
    """Test cases for L-shaped routing when points are not aligned."""

    def test_horizontal_first_routing(self):
        """Test L-shaped routing with horizontal-first preference."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 125.0),
            corner_direction=CornerDirection.HORIZONTAL_FIRST
        )

        assert not result.is_direct
        assert len(result.segments) == 2
        assert result.corner is not None

        # Corner should be at destination X, source Y
        assert result.corner.x == 150.0
        assert result.corner.y == 100.0

        # First segment: horizontal (source to corner)
        seg1_start, seg1_end = result.segments[0]
        assert seg1_start.x == 100.0
        assert seg1_start.y == 100.0
        assert seg1_end.x == 150.0
        assert seg1_end.y == 100.0

        # Second segment: vertical (corner to destination)
        seg2_start, seg2_end = result.segments[1]
        assert seg2_start.x == 150.0
        assert seg2_start.y == 100.0
        assert seg2_end.x == 150.0
        assert seg2_end.y == 125.0

        # Should validate correctly
        assert validate_routing_result(result)

    def test_vertical_first_routing(self):
        """Test L-shaped routing with vertical-first preference."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 125.0),
            corner_direction=CornerDirection.VERTICAL_FIRST
        )

        assert not result.is_direct
        assert len(result.segments) == 2
        assert result.corner is not None

        # Corner should be at source X, destination Y
        assert result.corner.x == 100.0
        assert result.corner.y == 125.0

        # First segment: vertical (source to corner)
        seg1_start, seg1_end = result.segments[0]
        assert seg1_start.x == 100.0
        assert seg1_start.y == 100.0
        assert seg1_end.x == 100.0
        assert seg1_end.y == 125.0

        # Second segment: horizontal (corner to destination)
        seg2_start, seg2_end = result.segments[1]
        assert seg2_start.x == 100.0
        assert seg2_start.y == 125.0
        assert seg2_end.x == 150.0
        assert seg2_end.y == 125.0

        # Should validate correctly
        assert validate_routing_result(result)

    def test_auto_routing_horizontal_preference(self):
        """Test AUTO routing prefers horizontal when dx >= dy."""
        # Horizontal distance (50) >= vertical distance (25)
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 125.0),
            corner_direction=CornerDirection.AUTO
        )

        assert not result.is_direct
        assert result.corner is not None

        # Should choose horizontal first (corner at destination X, source Y)
        assert result.corner.x == 150.0
        assert result.corner.y == 100.0

        # First segment should be horizontal
        seg1_start, seg1_end = result.segments[0]
        assert seg1_start.y == seg1_end.y  # Same Y = horizontal

    def test_auto_routing_vertical_preference(self):
        """Test AUTO routing prefers vertical when dy > dx."""
        # Vertical distance (50) > horizontal distance (25)
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(125.0, 150.0),
            corner_direction=CornerDirection.AUTO
        )

        assert not result.is_direct
        assert result.corner is not None

        # Should choose vertical first (corner at source X, destination Y)
        assert result.corner.x == 100.0
        assert result.corner.y == 150.0

        # First segment should be vertical
        seg1_start, seg1_end = result.segments[0]
        assert seg1_start.x == seg1_end.x  # Same X = vertical

    def test_auto_routing_equal_distance(self):
        """Test AUTO routing when distances are equal (should prefer horizontal)."""
        # Equal distances: dx = dy = 50
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 150.0),
            corner_direction=CornerDirection.AUTO
        )

        assert not result.is_direct
        assert result.corner is not None

        # Should choose horizontal first (dx >= dy)
        assert result.corner.x == 150.0
        assert result.corner.y == 100.0


class TestRoutingInvertedYAxis:
    """Test routing with KiCAD's inverted Y-axis in mind."""

    def test_routing_upward_on_screen(self):
        """Test routing upward on screen (lower Y values)."""
        # Remember: Lower Y = visually HIGHER on screen in KiCAD
        result = create_orthogonal_routing(
            Point(100.0, 125.0),  # Starting point (visually lower)
            Point(150.0, 100.0),  # End point (visually higher - lower Y!)
            corner_direction=CornerDirection.HORIZONTAL_FIRST
        )

        assert not result.is_direct
        assert result.corner.x == 150.0
        assert result.corner.y == 125.0

        # First segment: horizontal
        # Second segment: vertical upward (decreasing Y)
        seg2_start, seg2_end = result.segments[1]
        assert seg2_end.y < seg2_start.y  # Moving "up" means decreasing Y

    def test_routing_downward_on_screen(self):
        """Test routing downward on screen (higher Y values)."""
        # Remember: Higher Y = visually LOWER on screen in KiCAD
        result = create_orthogonal_routing(
            Point(100.0, 100.0),  # Starting point (visually higher)
            Point(150.0, 125.0),  # End point (visually lower - higher Y!)
            corner_direction=CornerDirection.HORIZONTAL_FIRST
        )

        assert not result.is_direct
        assert result.corner.x == 150.0
        assert result.corner.y == 100.0

        # Second segment: vertical downward (increasing Y)
        seg2_start, seg2_end = result.segments[1]
        assert seg2_end.y > seg2_start.y  # Moving "down" means increasing Y


class TestRoutingNegativeDirections:
    """Test routing in all directions including negative."""

    def test_routing_left_and_up(self):
        """Test routing left (decreasing X) and up (decreasing Y)."""
        result = create_orthogonal_routing(
            Point(150.0, 125.0),
            Point(100.0, 100.0),
            corner_direction=CornerDirection.HORIZONTAL_FIRST
        )

        assert not result.is_direct

        # Corner at destination X, source Y
        assert result.corner.x == 100.0
        assert result.corner.y == 125.0

        # Validate routing
        assert validate_routing_result(result)

    def test_routing_right_and_down(self):
        """Test routing right (increasing X) and down (increasing Y)."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 125.0),
            corner_direction=CornerDirection.VERTICAL_FIRST
        )

        assert not result.is_direct

        # Corner at source X, destination Y
        assert result.corner.x == 100.0
        assert result.corner.y == 125.0

        # Validate routing
        assert validate_routing_result(result)


class TestRoutingValidation:
    """Test routing validation functionality."""

    def test_validate_direct_routing(self):
        """Test validation passes for direct routing."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 100.0)
        )
        assert validate_routing_result(result)

    def test_validate_l_shaped_routing(self):
        """Test validation passes for L-shaped routing."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(150.0, 125.0)
        )
        assert validate_routing_result(result)

    def test_validate_rejects_diagonal_segment(self):
        """Test validation rejects diagonal (non-orthogonal) segments."""
        # Create invalid routing with diagonal segment
        invalid_result = RoutingResult(
            segments=[(Point(100.0, 100.0), Point(150.0, 125.0))],  # Diagonal!
            corner=None,
            is_direct=True
        )

        with pytest.raises(ValueError, match="not orthogonal"):
            validate_routing_result(invalid_result)

    def test_validate_rejects_disconnected_segments(self):
        """Test validation rejects disconnected segments."""
        # Create invalid routing with gap between segments
        invalid_result = RoutingResult(
            segments=[
                (Point(100.0, 100.0), Point(150.0, 100.0)),  # First segment
                (Point(150.0, 110.0), Point(150.0, 125.0))   # Gap! Not connected
            ],
            corner=Point(150.0, 100.0),
            is_direct=False
        )

        with pytest.raises(ValueError, match="not connected"):
            validate_routing_result(invalid_result)

    def test_validate_rejects_wrong_corner_position(self):
        """Test validation rejects corner at wrong position."""
        # Create invalid routing with corner not matching segment endpoints
        invalid_result = RoutingResult(
            segments=[
                (Point(100.0, 100.0), Point(150.0, 100.0)),
                (Point(150.0, 100.0), Point(150.0, 125.0))
            ],
            corner=Point(140.0, 100.0),  # Wrong X!
            is_direct=False
        )

        with pytest.raises(ValueError, match="does not match segment endpoints"):
            validate_routing_result(invalid_result)

    def test_validate_rejects_empty_segments(self):
        """Test validation rejects empty segment list."""
        invalid_result = RoutingResult(
            segments=[],
            corner=None,
            is_direct=True
        )

        with pytest.raises(ValueError, match="at least one segment"):
            validate_routing_result(invalid_result)


class TestRoutingRealWorldScenarios:
    """Test routing with real-world component positions."""

    def test_resistor_to_resistor_horizontal(self):
        """Test routing between two horizontally placed resistors."""
        # R1 at (127.0, 88.9), R2 at (127.0, 114.3)
        # Both rotated 0 degrees, pins aligned vertically
        r1_pin2 = Point(127.0, 92.71)  # R1 pin 2 (bottom)
        r2_pin1 = Point(127.0, 110.49) # R2 pin 1 (top)

        result = create_orthogonal_routing(r1_pin2, r2_pin1)

        assert result.is_direct  # Vertically aligned
        assert len(result.segments) == 1

    def test_resistor_to_resistor_l_shaped(self):
        """Test L-shaped routing between offset resistors."""
        # R1 at (100, 100), R2 at (150, 125)
        r1_pin2 = Point(100.0, 103.81)
        r2_pin1 = Point(150.0, 121.19)

        result = create_orthogonal_routing(
            r1_pin2,
            r2_pin1,
            corner_direction=CornerDirection.AUTO
        )

        assert not result.is_direct
        assert len(result.segments) == 2
        assert result.corner is not None

        # Validate produces correct routing
        assert validate_routing_result(result)

    def test_voltage_divider_t_junction(self):
        """Test routing for voltage divider with T-junction at output."""
        # R1 bottom pin connects to R2 top pin
        r1_bottom = Point(127.0, 92.71)
        r2_top = Point(127.0, 110.49)

        # Then tap off to output
        output_point = Point(140.0, 101.6)  # Midpoint between resistors

        # First connection: R1 to R2 (direct vertical)
        result1 = create_orthogonal_routing(r1_bottom, r2_top)
        assert result1.is_direct

        # Second connection: junction to output (direct horizontal)
        junction = Point(127.0, 101.6)
        result2 = create_orthogonal_routing(junction, output_point)
        assert result2.is_direct


class TestRoutingEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_routing_with_very_small_distances(self):
        """Test routing with sub-millimeter distances."""
        result = create_orthogonal_routing(
            Point(100.0, 100.0),
            Point(100.1, 100.1)
        )

        assert not result.is_direct
        assert len(result.segments) == 2
        assert validate_routing_result(result)

    def test_routing_with_large_distances(self):
        """Test routing with large distances."""
        result = create_orthogonal_routing(
            Point(0.0, 0.0),
            Point(1000.0, 1000.0)
        )

        assert not result.is_direct
        assert len(result.segments) == 2
        assert validate_routing_result(result)

    def test_routing_with_negative_coordinates(self):
        """Test routing with negative coordinates."""
        result = create_orthogonal_routing(
            Point(-100.0, -100.0),
            Point(100.0, 100.0)
        )

        assert not result.is_direct
        assert len(result.segments) == 2
        assert validate_routing_result(result)
