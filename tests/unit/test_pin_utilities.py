"""
Unit tests for pin utility methods (list_pins, show_pins).

Tests the new pin enumeration functionality that makes it easy for users
to discover and inspect component pins without needing to know them in advance.
"""

import io
import sys

import pytest

import kicad_sch_api as ksa


class TestListPinsMethod:
    """Test the list_pins() method."""

    def test_list_pins_returns_list(self):
        """list_pins() should return a list."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        assert isinstance(pins, list)

    def test_list_pins_resistor_has_two_pins(self):
        """Resistor should have exactly 2 pins."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        assert len(pins) == 2

    def test_list_pins_dict_structure(self):
        """Each pin dict should have required keys."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        # Check first pin has all required keys
        pin = pins[0]
        assert "number" in pin
        assert "name" in pin
        assert "type" in pin
        assert "position" in pin

    def test_list_pins_number_is_string(self):
        """Pin number should be a string."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        for pin in pins:
            assert isinstance(pin["number"], str)

    def test_list_pins_name_is_string(self):
        """Pin name should be a string."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        for pin in pins:
            assert isinstance(pin["name"], str)

    def test_list_pins_type_is_string(self):
        """Pin type should be a string."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        for pin in pins:
            assert isinstance(pin["type"], str)

    def test_list_pins_position_is_point(self):
        """Pin position should be a Point object."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        for pin in pins:
            # Should have x and y attributes
            assert hasattr(pin["position"], "x")
            assert hasattr(pin["position"], "y")

    def test_list_pins_resistor_pin_numbers(self):
        """Resistor pins should be numbered 1 and 2."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()
        pin_numbers = {p["number"] for p in pins}

        assert "1" in pin_numbers
        assert "2" in pin_numbers

    def test_list_pins_programmatic_iteration(self):
        """Should be able to programmatically iterate pins."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        # Should be able to filter/process pins
        pin_numbers = [p["number"] for p in pins]
        pin_names = [p["name"] for p in pins]
        pin_types = [p["type"] for p in pins]

        assert len(pin_numbers) == 2
        assert len(pin_names) == 2
        assert len(pin_types) == 2


class TestShowPinsMethod:
    """Test the show_pins() method."""

    def test_show_pins_produces_output(self, capsys):
        """show_pins() should print output."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        r1.show_pins()

        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_show_pins_displays_reference(self, capsys):
        """show_pins() should display component reference."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        r1.show_pins()

        captured = capsys.readouterr()
        assert "R1" in captured.out

    def test_show_pins_displays_lib_id(self, capsys):
        """show_pins() should display lib_id."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        r1.show_pins()

        captured = capsys.readouterr()
        assert "Device:R" in captured.out

    def test_show_pins_has_header(self, capsys):
        """show_pins() should have column headers."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        r1.show_pins()

        captured = capsys.readouterr()
        assert "Pin#" in captured.out
        assert "Name" in captured.out
        assert "Type" in captured.out

    def test_show_pins_displays_pin_numbers(self, capsys):
        """show_pins() should display pin numbers."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        r1.show_pins()

        captured = capsys.readouterr()
        # Resistor should have pins 1 and 2
        assert "1" in captured.out
        assert "2" in captured.out

    def test_show_pins_formatting_has_separator(self, capsys):
        """show_pins() output should have separator line."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        r1.show_pins()

        captured = capsys.readouterr()
        # Should have a separator line with dashes
        assert "-" * 10 in captured.out


class TestRealWorldUsage:
    """Test real-world usage scenarios."""

    def test_discover_pins_without_knowing_in_advance(self):
        """User can discover pins without prior knowledge."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # User doesn't know what pins a resistor has
        pins = r1.list_pins()

        # But can now discover them
        assert len(pins) > 0
        first_pin = pins[0]
        assert first_pin["number"] is not None
        assert first_pin["name"] is not None

    def test_find_specific_pin_type(self):
        """User can filter pins by type."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        # Filter for passive pins
        passive_pins = [p for p in pins if p["type"] == "passive"]

        # Resistor pins should be passive
        assert len(passive_pins) > 0

    def test_check_if_component_has_pin(self):
        """User can check if component has specific pin."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()
        pin_numbers = {p["number"] for p in pins}

        # Check if pin 1 exists
        assert "1" in pin_numbers

        # Check if pin 99 exists (should not)
        assert "99" not in pin_numbers

    def test_get_pin_positions_for_routing(self):
        """User can get pin positions for wire routing."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        pins = r1.list_pins()

        # Get position of first pin for routing
        pin1 = next(p for p in pins if p["number"] == "1")
        pos = pin1["position"]

        # Position should be valid
        assert pos.x is not None
        assert pos.y is not None
        assert isinstance(pos.x, (int, float))
        assert isinstance(pos.y, (int, float))
