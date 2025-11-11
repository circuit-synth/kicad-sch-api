"""
Integration tests for add_wire_between_pins with non-unique references (Issue #171).

Tests the exact user scenario that exposed the bug where ComponentCollection.get()
failed to handle list returns from IndexRegistry for non-unique reference indexes.

The bug manifested when users tried to wire components together:
    sch.add_wire_between_pins("R1", "2", "C1", "1")

This internally calls:
    get_component_pin_position() → components.get("R1") → IndexRegistry.get()

IndexRegistry returns [0] (list), but get() expected int → TypeError.
"""

import pytest

import kicad_sch_api as ksa


class TestWireBetweenPinsIntegration:
    """Test wire routing with components that may have non-unique references."""

    def test_wire_between_pins_basic_workflow(self):
        """Test the exact scenario from Issue #171.

        This is the user's failing code that exposed the bug:
            sch.add_wire_between_pins("R1", "2", "C1", "1")
        """
        sch = ksa.create_schematic("My Circuit")

        # Add components
        sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )

        sch.components.add(
            lib_id="Device:C",
            reference="C1",
            value="100nF",
            position=(150.0, 100.0),
            footprint="Capacitor_SMD:C_0603_1608Metric",
        )

        # This internally calls get_component_pin_position() → components.get()
        # which was failing with TypeError: list indices must be integers
        wire_uuid = sch.add_wire_between_pins("R1", "2", "C1", "1")

        assert wire_uuid is not None
        wires = list(sch.wires)
        assert len(wires) > 0

    def test_wire_between_pins_with_labels(self):
        """Test the complete example from documentation."""
        sch = ksa.create_schematic("My Circuit")

        # Add components
        sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )

        sch.components.add(
            lib_id="Device:C",
            reference="C1",
            value="100nF",
            position=(150.0, 100.0),
            footprint="Capacitor_SMD:C_0603_1608Metric",
        )

        # Add wires for connectivity
        sch.wires.add(start=(100, 110), end=(150, 110))

        # Pin-to-pin wiring
        wire_uuid = sch.add_wire_between_pins("R1", "2", "C1", "1")
        assert wire_uuid is not None

        # Add labels for nets
        sch.add_label("VCC", position=(125, 110))

        # Verify schematic is valid
        assert len(list(sch.components)) == 2
        assert len(list(sch.wires)) >= 1
        assert len(list(sch.labels)) == 1

    def test_wire_between_multi_unit_components(self):
        """Test wiring when multi-unit components exist.

        Multi-unit components have multiple SchematicSymbols with the same
        reference (e.g., U1A and U1B both have reference "U1"). This tests
        that wire routing works correctly with non-unique references.
        """
        sch = ksa.create_schematic("Multi-Unit Test")

        # Add multi-unit op-amp (TL072 has 3 units)
        # Note: Each unit is a separate SchematicSymbol with same reference
        sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            unit=1,
        )

        sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(150, 100),
            unit=2,
        )

        # Add resistor
        sch.components.add(
            "Device:R",
            reference="R1",
            value="10k",
            position=(200, 100),
        )

        # Wire from U1 (first unit) to R1
        # This tests that get() returns the first unit when multiple exist
        wire_uuid = sch.add_wire_between_pins("U1", "1", "R1", "1")
        assert wire_uuid is not None

    def test_multiple_wires_between_components(self):
        """Test creating multiple wires between different component pairs."""
        sch = ksa.create_schematic("Multiple Wires")

        # Add three resistors
        sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))
        sch.components.add("Device:R", reference="R2", value="20k", position=(150, 100))
        sch.components.add("Device:R", reference="R3", value="30k", position=(200, 100))

        # Create multiple wires
        wire1 = sch.add_wire_between_pins("R1", "2", "R2", "1")
        wire2 = sch.add_wire_between_pins("R2", "2", "R3", "1")

        assert wire1 is not None
        assert wire2 is not None
        assert wire1 != wire2  # Different wires

    def test_wire_to_component_after_removal(self):
        """Test that wiring works after removing a component.

        This tests that the index is correctly rebuilt after component
        removal and subsequent get() calls work.
        """
        sch = ksa.create_schematic("Test Removal")

        # Add three components
        sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))
        sch.components.add("Device:R", reference="R2", value="20k", position=(150, 100))
        sch.components.add("Device:R", reference="R3", value="30k", position=(200, 100))

        # Remove R2
        sch.components.remove("R2")

        # Wire R1 to R3 (should still work)
        wire_uuid = sch.add_wire_between_pins("R1", "2", "R3", "1")
        assert wire_uuid is not None


class TestGetComponentPinPosition:
    """Test get_component_pin_position which internally uses components.get()."""

    def test_get_pin_position_single_component(self):
        """Test getting pin position for component with unique reference."""
        sch = ksa.create_schematic("Pin Position Test")

        sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))

        # This calls components.get("R1") internally
        pin_pos = sch.get_component_pin_position("R1", "1")
        assert pin_pos is not None
        assert hasattr(pin_pos, "x")
        assert hasattr(pin_pos, "y")

    def test_get_pin_position_multi_unit_component(self):
        """Test getting pin position for multi-unit component.

        Should return pin position from first unit when multiple units
        share the same reference.
        """
        sch = ksa.create_schematic("Multi-Unit Pin Position")

        # Add two units with same reference
        sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            unit=1,
        )

        sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(150, 100),
            unit=2,
        )

        # Should get pin position from first unit
        pin_pos = sch.get_component_pin_position("U1", "1")
        assert pin_pos is not None

    def test_get_pin_position_nonexistent_component(self):
        """Test getting pin position for non-existent component returns None."""
        sch = ksa.create_schematic("Test")

        # Returns None for non-existent component (doesn't raise)
        pin_pos = sch.get_component_pin_position("NonExistent", "1")
        assert pin_pos is None


class TestConnectPinsWithWire:
    """Test connect_pins_with_wire() method with non-unique references."""

    def test_connect_pins_basic(self):
        """Test connecting two components with unique references."""
        sch = ksa.create_schematic("Connect Test")

        sch.components.add("Device:R", reference="R1", value="10k", position=(100, 100))
        sch.components.add("Device:C", reference="C1", value="100nF", position=(150, 100))

        # Connect using connect_pins_with_wire (alias for add_wire_between_pins)
        wire_uuid = sch.connect_pins_with_wire("R1", "2", "C1", "1")

        assert wire_uuid is not None
        assert len(list(sch.wires)) > 0

    def test_connect_multi_unit_to_regular_component(self):
        """Test connecting multi-unit component to regular component."""
        sch = ksa.create_schematic("Connect Multi-Unit")

        # Multi-unit op-amp
        sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            unit=1,
        )

        sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(150, 100),
            unit=2,
        )

        # Regular resistor
        sch.components.add("Device:R", reference="R1", value="10k", position=(200, 100))

        # Connect U1 (first unit) to R1
        wire_uuid = sch.connect_pins_with_wire("U1", "1", "R1", "1")
        assert wire_uuid is not None
        assert len(list(sch.wires)) > 0
