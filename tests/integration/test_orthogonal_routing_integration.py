"""
Integration tests for orthogonal routing with real schematics.

Tests the routing functionality in realistic scenarios with actual
schematic files, components, and wire connections.
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.geometry import (
    CornerDirection,
    create_orthogonal_routing,
    validate_routing_result,
)


class TestRoutingWithRealComponents:
    """Test routing with actual schematic components."""

    def test_routing_between_resistor_pins(self):
        """Test routing between pins of real resistors."""
        sch = ksa.create_schematic("Resistor Routing Test")

        # Add two resistors
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0)
        r2 = sch.components.add("Device:R", "R2", "10k", position=(150.0, 125.0), rotation=0)

        # Get pin positions
        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")

        # Route from R1 pin 2 to R2 pin 1
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        result = create_orthogonal_routing(
            r1_pin2.position,
            r2_pin1.position,
            corner_direction=CornerDirection.AUTO
        )

        # Should create L-shaped routing
        assert not result.is_direct
        assert len(result.segments) == 2
        assert result.corner is not None

        # Validate routing
        validate_routing_result(result)

    def test_routing_with_rotated_components(self):
        """Test routing with components at different rotations."""
        sch = ksa.create_schematic("Rotated Components Test")

        # Add resistors with different rotations
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0)
        r2 = sch.components.add("Device:R", "R2", "10k", position=(100.0, 125.0), rotation=90)

        # Get pin positions
        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")

        # Route between corresponding pins
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        result = create_orthogonal_routing(
            r1_pin2.position,
            r2_pin1.position
        )

        # Should have valid routing
        validate_routing_result(result)
        assert len(result.segments) >= 1

    def test_voltage_divider_circuit_routing(self):
        """Test routing for a complete voltage divider circuit."""
        sch = ksa.create_schematic("Voltage Divider")

        # Create voltage divider: R1 and R2 in series
        r1 = sch.components.add("Device:R", "R1", "10k", position=(127.0, 88.9), rotation=0)
        r2 = sch.components.add("Device:R", "R2", "10k", position=(127.0, 114.3), rotation=0)

        # Get pin positions
        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")

        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        # Route R1 to R2 (should be direct vertical)
        result = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)

        assert result.is_direct  # Vertically aligned
        assert len(result.segments) == 1
        validate_routing_result(result)

        # Calculate midpoint for output tap
        midpoint_y = (r1_pin2.position.y + r2_pin1.position.y) / 2
        midpoint = Point(127.0, midpoint_y)
        output = Point(160.0, midpoint_y)

        # Route from midpoint to output (should be direct horizontal)
        result2 = create_orthogonal_routing(midpoint, output)

        assert result2.is_direct  # Horizontally aligned
        assert len(result2.segments) == 1
        validate_routing_result(result2)


class TestRoutingWithWireAddition:
    """Test routing integrated with wire addition."""

    def test_add_routed_wires_to_schematic(self):
        """Test adding routing result as actual wires to schematic."""
        sch = ksa.create_schematic("Wire Addition Test")

        # Add two resistors
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = sch.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

        # Get pin positions
        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        # Create routing
        result = create_orthogonal_routing(
            r1_pin2.position,
            r2_pin1.position,
            corner_direction=CornerDirection.HORIZONTAL_FIRST
        )

        # Add wires to schematic (returns UUIDs)
        wire_uuids = []
        for start, end in result.segments:
            wire_uuid = sch.wires.add(start=start, end=end)
            wire_uuids.append(wire_uuid)

        # Verify wires were added
        assert len(wire_uuids) == len(result.segments)
        assert len(list(sch.wires)) >= len(result.segments)

        # Verify wire UUIDs are valid
        for wire_uuid in wire_uuids:
            assert isinstance(wire_uuid, str)
            assert len(wire_uuid) > 0

    def test_add_wires_with_corner_position(self):
        """Test adding wires and tracking corner position for L-shaped routing."""
        sch = ksa.create_schematic("Corner Position Test")

        # Add two offset resistors
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = sch.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

        # Get pin positions
        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        # Create L-shaped routing
        result = create_orthogonal_routing(
            r1_pin2.position,
            r2_pin1.position
        )

        # Add wires
        wire_uuids = []
        for start, end in result.segments:
            uuid = sch.wires.add(start=start, end=end)
            wire_uuids.append(uuid)

        # Verify corner position is available for future junction addition
        if result.corner:
            # Corner position should be at the junction of two segments
            assert result.segments[0][1] == result.corner
            assert result.segments[1][0] == result.corner

            # Note: Junction addition would be done via MCP server tool
            # or direct schematic manipulation in Phase 2


class TestRoutingPerformance:
    """Test routing performance with multiple connections."""

    def test_routing_many_connections(self):
        """Test routing performance with many connections."""
        sch = ksa.create_schematic("Performance Test")

        # Add a chain of resistors
        num_resistors = 10
        resistors = []
        for i in range(num_resistors):
            r = sch.components.add(
                "Device:R",
                f"R{i+1}",
                "10k",
                position=(100.0 + i * 25.0, 100.0 + (i % 2) * 25.0)
            )
            resistors.append(r)

        # Route between consecutive resistors
        routings = []
        for i in range(len(resistors) - 1):
            r1_pins = sch.components.get_pins_info(resistors[i].reference)
            r2_pins = sch.components.get_pins_info(resistors[i + 1].reference)

            r1_pin2 = next(p for p in r1_pins if p.number == "2")
            r2_pin1 = next(p for p in r2_pins if p.number == "1")

            result = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)
            validate_routing_result(result)
            routings.append(result)

        # Verify all routings are valid
        assert len(routings) == num_resistors - 1
        for result in routings:
            assert len(result.segments) >= 1


class TestRoutingEdgeCasesIntegration:
    """Test routing edge cases with real components."""

    def test_routing_overlapping_components(self):
        """Test routing when component positions overlap."""
        sch = ksa.create_schematic("Overlapping Test")

        # Add components at very close positions
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = sch.components.add("Device:R", "R2", "10k", position=(105.0, 100.0))

        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        # Should still produce valid routing
        result = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)
        validate_routing_result(result)

    def test_routing_with_grid_aligned_positions(self):
        """Test routing with KiCAD grid-aligned positions."""
        sch = ksa.create_schematic("Grid Alignment Test")

        # Use grid-aligned positions (1.27mm grid)
        r1 = sch.components.add("Device:R", "R1", "10k", position=(101.6, 101.6))
        r2 = sch.components.add("Device:R", "R2", "10k", position=(127.0, 127.0))

        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        result = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)
        validate_routing_result(result)

        # Verify routing endpoints match pin positions exactly
        assert result.segments[0][0].x == r1_pin2.position.x
        assert result.segments[0][0].y == r1_pin2.position.y
        assert result.segments[-1][1].x == r2_pin1.position.x
        assert result.segments[-1][1].y == r2_pin1.position.y


class TestRoutingSaveLoad:
    """Test routing with save/load operations."""

    def test_routing_roundtrip(self, tmp_path):
        """Test routing survives save/load roundtrip."""
        # Create schematic with routed connections
        sch = ksa.create_schematic("Roundtrip Test")

        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = sch.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        # Create and add routing
        result = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)
        original_segments = [(s.x, s.y, e.x, e.y) for s, e in result.segments]

        for start, end in result.segments:
            sch.wires.add(start=start, end=end)

        # Save schematic
        output_path = tmp_path / "routed.kicad_sch"
        sch.save(str(output_path))

        # Load schematic
        loaded_sch = ksa.Schematic.load(str(output_path))

        # Verify wires were preserved
        loaded_wires = list(loaded_sch.wires)
        assert len(loaded_wires) >= len(result.segments)

        # Verify at least some wires match our routing
        loaded_segments = [(w.start.x, w.start.y, w.end.x, w.end.y) for w in loaded_wires]
        for orig_seg in original_segments:
            # Check if this segment exists in loaded wires
            found = any(
                abs(ls[0] - orig_seg[0]) < 0.01 and
                abs(ls[1] - orig_seg[1]) < 0.01 and
                abs(ls[2] - orig_seg[2]) < 0.01 and
                abs(ls[3] - orig_seg[3]) < 0.01
                for ls in loaded_segments
            )
            assert found, f"Segment {orig_seg} not found in loaded schematic"


class TestRoutingDirectionModes:
    """Test different routing direction modes with real components."""

    def test_all_direction_modes_produce_valid_routing(self):
        """Test that all direction modes produce valid routing."""
        sch = ksa.create_schematic("Direction Modes Test")

        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = sch.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        # Test all direction modes
        for direction in [
            CornerDirection.AUTO,
            CornerDirection.HORIZONTAL_FIRST,
            CornerDirection.VERTICAL_FIRST
        ]:
            result = create_orthogonal_routing(
                r1_pin2.position,
                r2_pin1.position,
                corner_direction=direction
            )

            # All should produce valid routing
            validate_routing_result(result)
            assert len(result.segments) >= 1

            # Verify start and end positions match pins
            assert result.segments[0][0].x == r1_pin2.position.x
            assert result.segments[0][0].y == r1_pin2.position.y
            assert result.segments[-1][1].x == r2_pin1.position.x
            assert result.segments[-1][1].y == r2_pin1.position.y

    def test_direction_modes_produce_different_corners(self):
        """Test that different direction modes produce different corner positions."""
        sch = ksa.create_schematic("Corner Comparison Test")

        r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = sch.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

        r1_pins = sch.components.get_pins_info("R1")
        r2_pins = sch.components.get_pins_info("R2")
        r1_pin2 = next(p for p in r1_pins if p.number == "2")
        r2_pin1 = next(p for p in r2_pins if p.number == "1")

        # Get routing with different directions
        result_h_first = create_orthogonal_routing(
            r1_pin2.position,
            r2_pin1.position,
            corner_direction=CornerDirection.HORIZONTAL_FIRST
        )

        result_v_first = create_orthogonal_routing(
            r1_pin2.position,
            r2_pin1.position,
            corner_direction=CornerDirection.VERTICAL_FIRST
        )

        # If not direct routing, corners should be different
        if not result_h_first.is_direct and not result_v_first.is_direct:
            assert result_h_first.corner != result_v_first.corner
