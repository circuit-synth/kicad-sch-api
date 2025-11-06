"""
Test pin-to-pin wire drawing functionality.

This module tests the new wire drawing capabilities that connect component pins directly.
"""

import pytest

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point


@pytest.fixture
def test_schematic():
    """Create a test schematic with two resistors."""
    sch = Schematic()

    # Add two resistors
    r1 = sch.components.add(lib_id="Device:R", reference="R1", value="10k", position=(100, 100))

    r2 = sch.components.add(lib_id="Device:R", reference="R2", value="20k", position=(150, 100))

    return sch, r1, r2


class TestPinToPinWiring:
    """Test pin-to-pin wire drawing functionality."""

    def test_get_component_pin_position(self, test_schematic):
        """Test getting pin position from component reference."""
        sch, r1, r2 = test_schematic

        # Test getting pin position by component reference
        pin_pos = sch.get_component_pin_position("R1", "1")
        assert pin_pos is not None, "Should find R1 pin 1 position"
        assert isinstance(pin_pos, Point), "Should return Point object"

        # Test non-existent component
        pin_pos = sch.get_component_pin_position("R999", "1")
        assert pin_pos is None, "Should return None for non-existent component"

        # Test non-existent pin
        pin_pos = sch.get_component_pin_position("R1", "999")
        assert pin_pos is None, "Should return None for non-existent pin"

    def test_add_wire_to_pin(self, test_schematic):
        """Test drawing wire from arbitrary point to component pin."""
        sch, r1, r2 = test_schematic

        # Define start point
        start_point = Point(50, 100)

        # Draw wire to R1 pin 1
        wire_uuid = sch.add_wire_to_pin(start_point, "R1", "1")
        assert wire_uuid is not None, "Should create wire"

        # Verify wire exists in collection
        assert len(sch.wires) == 1, "Should have one wire"
        assert wire_uuid in [wire.uuid for wire in sch.wires], "Wire should be in collection"

        # Verify wire endpoints
        wire = sch.wires.get(wire_uuid)
        assert len(wire.points) == 2, "Wire should have exactly 2 points"

        # First point should be start point
        assert wire.points[0].x == start_point.x, "Start point X should match"
        assert wire.points[0].y == start_point.y, "Start point Y should match"

        # Second point should be pin position
        pin_pos = sch.get_component_pin_position("R1", "1")
        assert wire.points[1].x == pin_pos.x, "End point X should match pin position"
        assert wire.points[1].y == pin_pos.y, "End point Y should match pin position"

    def test_add_wire_to_pin_invalid_component(self, test_schematic):
        """Test drawing wire to non-existent component."""
        sch, r1, r2 = test_schematic

        start_point = Point(50, 100)
        wire_uuid = sch.add_wire_to_pin(start_point, "R999", "1")

        assert wire_uuid is None, "Should return None for non-existent component"
        assert len(sch.wires) == 0, "Should not create any wires"

    def test_add_wire_to_pin_invalid_pin(self, test_schematic):
        """Test drawing wire to non-existent pin."""
        sch, r1, r2 = test_schematic

        start_point = Point(50, 100)
        wire_uuid = sch.add_wire_to_pin(start_point, "R1", "999")

        assert wire_uuid is None, "Should return None for non-existent pin"
        assert len(sch.wires) == 0, "Should not create any wires"

    def test_add_wire_between_pins(self, test_schematic):
        """Test drawing wire between two component pins."""
        sch, r1, r2 = test_schematic

        # Draw wire between R1 pin 2 and R2 pin 1
        wire_uuid = sch.add_wire_between_pins("R1", "2", "R2", "1")
        assert wire_uuid is not None, "Should create wire"

        # Verify wire exists
        assert len(sch.wires) == 1, "Should have one wire"
        wire = sch.wires.get(wire_uuid)
        assert len(wire.points) == 2, "Wire should have exactly 2 points"

        # Verify endpoints match pin positions
        r1_pin2_pos = sch.get_component_pin_position("R1", "2")
        r2_pin1_pos = sch.get_component_pin_position("R2", "1")

        assert wire.points[0].x == r1_pin2_pos.x, "First point should match R1 pin 2"
        assert wire.points[0].y == r1_pin2_pos.y, "First point should match R1 pin 2"
        assert wire.points[1].x == r2_pin1_pos.x, "Second point should match R2 pin 1"
        assert wire.points[1].y == r2_pin1_pos.y, "Second point should match R2 pin 1"

    def test_add_wire_between_pins_invalid_first_component(self, test_schematic):
        """Test drawing wire with invalid first component."""
        sch, r1, r2 = test_schematic

        wire_uuid = sch.add_wire_between_pins("R999", "1", "R2", "1")
        assert wire_uuid is None, "Should return None for invalid first component"
        assert len(sch.wires) == 0, "Should not create any wires"

    def test_add_wire_between_pins_invalid_second_component(self, test_schematic):
        """Test drawing wire with invalid second component."""
        sch, r1, r2 = test_schematic

        wire_uuid = sch.add_wire_between_pins("R1", "1", "R999", "1")
        assert wire_uuid is None, "Should return None for invalid second component"
        assert len(sch.wires) == 0, "Should not create any wires"

    def test_add_wire_between_pins_invalid_first_pin(self, test_schematic):
        """Test drawing wire with invalid first pin."""
        sch, r1, r2 = test_schematic

        wire_uuid = sch.add_wire_between_pins("R1", "999", "R2", "1")
        assert wire_uuid is None, "Should return None for invalid first pin"
        assert len(sch.wires) == 0, "Should not create any wires"

    def test_add_wire_between_pins_invalid_second_pin(self, test_schematic):
        """Test drawing wire with invalid second pin."""
        sch, r1, r2 = test_schematic

        wire_uuid = sch.add_wire_between_pins("R1", "1", "R2", "999")
        assert wire_uuid is None, "Should return None for invalid second pin"
        assert len(sch.wires) == 0, "Should not create any wires"

    def test_multiple_pin_to_pin_wires(self, test_schematic):
        """Test creating multiple pin-to-pin wires."""
        sch, r1, r2 = test_schematic

        # Add a third component
        r3 = sch.components.add(lib_id="Device:R", reference="R3", value="30k", position=(200, 100))

        # Create multiple wires
        wire1_uuid = sch.add_wire_between_pins("R1", "2", "R2", "1")
        wire2_uuid = sch.add_wire_between_pins("R2", "2", "R3", "1")

        assert wire1_uuid is not None, "First wire should be created"
        assert wire2_uuid is not None, "Second wire should be created"
        assert wire1_uuid != wire2_uuid, "Wires should have different UUIDs"

        # Verify both wires exist
        assert len(sch.wires) == 2, "Should have two wires"
        assert wire1_uuid in [wire.uuid for wire in sch.wires], "First wire should exist"
        assert wire2_uuid in [wire.uuid for wire in sch.wires], "Second wire should exist"

    def test_wire_to_pin_with_tuples(self, test_schematic):
        """Test drawing wire using tuple coordinates."""
        sch, r1, r2 = test_schematic

        # Use tuple instead of Point for start position
        wire_uuid = sch.add_wire_to_pin((75, 125), "R1", "1")
        assert wire_uuid is not None, "Should create wire with tuple coordinates"

        # Verify wire exists and has correct start point
        wire = sch.wires.get(wire_uuid)
        assert wire.points[0].x == 75, "Start X coordinate should match tuple"
        assert wire.points[0].y == 125, "Start Y coordinate should match tuple"
