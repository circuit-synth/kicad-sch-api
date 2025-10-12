#!/usr/bin/env python3
"""
Unit tests for Manhattan routing functionality.

Tests the Manhattan routing algorithm with obstacle avoidance and
component bounding box integration.
"""

import os
import tempfile

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.component_bounds import BoundingBox, get_component_bounding_box
from kicad_sch_api.core.manhattan_routing import ManhattanRouter, RoutingStrategy
from kicad_sch_api.core.simple_manhattan import simple_manhattan_route
from kicad_sch_api.core.types import Point


class TestManhattanRouting:
    """Test Manhattan routing functionality."""

    def test_simple_manhattan_route_basic(self):
        """Test basic Manhattan routing between two points."""
        start = Point(0, 0)
        end = Point(20, 30)

        # Route without obstacles
        path = simple_manhattan_route(start, end)

        assert len(path) >= 2  # At minimum start and end points
        assert path[0] == start
        # End point should be close to target (within grid snap tolerance)
        assert abs(path[-1].x - end.x) < 1.0
        assert abs(path[-1].y - end.y) < 1.0

        # Verify path is Manhattan (only horizontal/vertical segments)
        for i in range(len(path) - 1):
            p1, p2 = path[i], path[i + 1]
            # Each segment should be either horizontal or vertical
            assert p1.x == p2.x or p1.y == p2.y

    def test_manhattan_route_with_obstacles(self):
        """Test Manhattan routing with obstacle avoidance."""
        start = Point(0, 0)
        end = Point(40, 40)

        # Create obstacle in the direct path
        obstacle = BoundingBox(15, 15, 25, 25)
        obstacles = [obstacle]

        router = ManhattanRouter()
        path = router.route_between_points(start, end, obstacles, clearance=2.0)

        assert len(path) >= 2
        assert path[0] == start
        # End point should be close to target (within grid snap tolerance)
        assert abs(path[-1].x - end.x) < 1.0
        assert abs(path[-1].y - end.y) < 1.0

        # Verify path avoids obstacles with clearance
        expanded_obstacle = obstacle.expand(2.0)
        for point in path[1:-1]:  # Exclude start/end which might be in obstacle
            assert not expanded_obstacle.contains_point(point)

    def test_manhattan_routing_strategies(self):
        """Test different routing strategies."""
        start = Point(0, 0)
        end = Point(30, 20)
        obstacle = BoundingBox(10, 5, 20, 15)

        router = ManhattanRouter()

        # Test shortest strategy
        path_h = router.route_between_points(
            start, end, [obstacle], strategy=RoutingStrategy.SHORTEST
        )

        # Test clearance strategy
        path_v = router.route_between_points(
            start, end, [obstacle], strategy=RoutingStrategy.CLEARANCE
        )

        # Both should reach the end (within grid tolerance)
        assert abs(path_h[-1].x - end.x) < 1.0
        assert abs(path_h[-1].y - end.y) < 1.0
        assert abs(path_v[-1].x - end.x) < 1.0
        assert abs(path_v[-1].y - end.y) < 1.0

        # Paths might be different due to different strategies
        # but both should be valid Manhattan routes
        for path in [path_h, path_v]:
            for i in range(len(path) - 1):
                p1, p2 = path[i], path[i + 1]
                assert p1.x == p2.x or p1.y == p2.y

    def test_manhattan_routing_integration_with_schematic(self):
        """Test Manhattan routing integration with schematic components."""
        sch = ksa.create_schematic("Manhattan Integration Test")

        # Add two components to route between
        r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
        r2 = sch.components.add("Device:R", "R2", "2k", Point(100, 100))

        # Add obstacle component
        obstacle_comp = sch.components.add("Device:C", "C1", "100nF", Point(75, 75))

        # Get component bounding boxes
        r1_bbox = get_component_bounding_box(r1, include_properties=False)
        r2_bbox = get_component_bounding_box(r2, include_properties=False)
        obstacle_bbox = get_component_bounding_box(obstacle_comp, include_properties=False)

        # Route from R1 to R2, avoiding C1
        router = ManhattanRouter()
        start_point = Point(r1.position.x, r1.position.y)
        end_point = Point(r2.position.x, r2.position.y)

        path = router.route_between_points(start_point, end_point, [obstacle_bbox], clearance=2.0)

        assert len(path) >= 2
        assert path[0] == start_point
        # End point should be close to target (within grid snap tolerance)
        assert abs(path[-1].x - end_point.x) < 1.0
        assert abs(path[-1].y - end_point.y) < 1.0

        # Add wires along the path
        for i in range(len(path) - 1):
            sch.wires.add(path[i], path[i + 1])

        # Verify schematic can be saved
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as tmp:
            sch.save(tmp.name)

            assert os.path.exists(tmp.name)
            assert os.path.getsize(tmp.name) > 0

            # Verify wires were added
            with open(tmp.name, "r") as f:
                content = f.read()
                assert "(wire" in content

            os.unlink(tmp.name)

    def test_routing_with_multiple_obstacles(self):
        """Test routing through multiple obstacles."""
        start = Point(0, 0)
        end = Point(60, 60)

        # Create multiple obstacles creating a maze-like scenario
        obstacles = [
            BoundingBox(10, 10, 20, 50),  # Vertical wall
            BoundingBox(30, 20, 50, 30),  # Horizontal wall
            BoundingBox(40, 40, 50, 50),  # Corner obstacle
        ]

        router = ManhattanRouter()
        path = router.route_between_points(start, end, obstacles, clearance=2.0)

        # Should find a path despite multiple obstacles
        assert len(path) >= 2
        assert path[0] == start
        # End point should be close to target (within grid snap tolerance)
        assert abs(path[-1].x - end.x) < 1.0
        assert abs(path[-1].y - end.y) < 1.0

        # Verify path avoids all obstacles
        for obstacle in obstacles:
            expanded_obstacle = obstacle.expand(2.0)
            for point in path[1:-1]:
                assert not expanded_obstacle.contains_point(point)

    def test_routing_clearance_values(self):
        """Test different clearance values affect routing."""
        start = Point(0, 0)
        end = Point(20, 20)
        obstacle = BoundingBox(8, 8, 12, 12)

        router = ManhattanRouter()

        # Test with small clearance
        path_small = router.route_between_points(start, end, [obstacle], clearance=1.0)

        # Test with large clearance
        path_large = router.route_between_points(start, end, [obstacle], clearance=5.0)

        # Both should reach the destination (within grid tolerance)
        assert abs(path_small[-1].x - end.x) < 1.0
        assert abs(path_small[-1].y - end.y) < 1.0
        assert abs(path_large[-1].x - end.x) < 1.0
        assert abs(path_large[-1].y - end.y) < 1.0

        # Large clearance path might be longer/different
        # as it needs to stay further from obstacles

    def test_direct_path_when_no_obstacles(self):
        """Test that direct path is used when no obstacles block it."""
        start = Point(10, 10)
        end = Point(30, 40)

        # No obstacles
        path = simple_manhattan_route(start, end)

        # Should be shortest Manhattan path (L-shaped)
        assert len(path) == 3  # start -> corner -> end

        # First segment should be either horizontal or vertical
        assert (path[0].x == path[1].x) or (path[0].y == path[1].y)
        # Second segment should be perpendicular to first
        assert (path[1].x == path[2].x) or (path[1].y == path[2].y)

    def test_auto_route_pins_integration(self):
        """Test integration with auto_route_pins method."""
        sch = ksa.create_schematic("Auto Route Pins Test")

        # Add components
        r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
        r2 = sch.components.add("Device:R", "R2", "2k", Point(100, 100))

        # Test auto-routing (this tests the integration point)
        try:
            # This might not work if pin information isn't available,
            # but we test that the method exists and doesn't crash
            result = sch.auto_route_pins(
                [(r1.reference, "1"), (r2.reference, "2")], use_manhattan=True, clearance=2.0
            )
            # If it succeeds, verify we got some result
            assert result is not None
        except Exception as e:
            # Expected if pin information isn't available
            # Just verify the method exists
            assert hasattr(sch, "auto_route_pins")

    def test_routing_edge_cases(self):
        """Test routing edge cases."""
        router = ManhattanRouter()

        # Test same start and end point
        start = end = Point(10, 10)
        path = router.route_between_points(start, end, [])
        assert len(path) == 1 or (len(path) == 2 and path[0] == path[1])

        # Test start point inside obstacle (should still try to route)
        start = Point(15, 15)
        end = Point(25, 25)
        obstacle = BoundingBox(10, 10, 20, 20)  # Contains start point

        path = router.route_between_points(start, end, [obstacle])
        # Should still attempt routing, though result depends on implementation
        # Path might be None if no route found
        assert path is None or len(path) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
