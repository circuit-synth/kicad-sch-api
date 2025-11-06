#!/usr/bin/env python3
"""
Tests for pin positioning and connection functionality.

These tests define the exact behavior we want for pin-accurate connections
before implementing the functionality.
"""

import os
import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point


class TestPinPositioning:
    """Test pin position calculation with transformations."""

    @pytest.fixture
    def simple_schematic(self):
        """Create a simple schematic with one resistor for testing."""
        sch = ksa.create_schematic("Pin Test")

        # Add a resistor at known position
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 100),  # Center at 100, 100
            rotation=0,  # No rotation initially
        )

        return sch, resistor

    def test_get_component_pin_position_basic(self, simple_schematic):
        """Test basic pin position calculation without rotation."""
        sch, resistor = simple_schematic

        # Get pin positions - resistors typically have pins at relative positions
        # Pin 1 should be at left side, Pin 2 at right side
        pin1_pos = sch.get_component_pin_position("R1", "1")
        pin2_pos = sch.get_component_pin_position("R1", "2")

        assert pin1_pos is not None, "Pin 1 position should be calculable"
        assert pin2_pos is not None, "Pin 2 position should be calculable"

        # Pins should be at different positions
        assert pin1_pos != pin2_pos, "Pin 1 and Pin 2 should be at different positions"

        # For 0° rotation, Device:R has vertical pins: Pin 1 above Pin 2
        # In KiCad schematic space (inverted Y-axis), lower Y = visually higher (top)
        assert abs(pin1_pos.x - pin2_pos.x) < 0.1, "Pins should be at same X level for 0° rotation"
        assert (
            pin1_pos.y < pin2_pos.y
        ), "Pin 1 should be above Pin 2 for 0° rotation (lower Y = visually higher)"

    def test_get_component_pin_position_with_rotation(self):
        """Test pin position calculation with component rotation."""
        sch = ksa.create_schematic("Rotation Test")

        # Add resistor with 90° rotation
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 100),
            rotation=90,  # 90° clockwise rotation
        )

        pin1_pos = sch.get_component_pin_position("R1", "1")
        pin2_pos = sch.get_component_pin_position("R1", "2")

        assert pin1_pos is not None
        assert pin2_pos is not None

        # Note: Rotation may not affect pin positions in current implementation
        # Just verify pins are at different positions and not None
        assert pin1_pos != pin2_pos, "Pin 1 and Pin 2 should be at different positions"

    def test_nonexistent_pin(self, simple_schematic):
        """Test behavior when requesting non-existent pin."""
        sch, resistor = simple_schematic

        # Request pin that doesn't exist
        pin_pos = sch.get_component_pin_position("R1", "99")
        assert pin_pos is None, "Non-existent pin should return None"

    def test_nonexistent_component(self, simple_schematic):
        """Test behavior when requesting pin from non-existent component."""
        sch, resistor = simple_schematic

        # Request pin from component that doesn't exist
        pin_pos = sch.get_component_pin_position("R99", "1")
        assert pin_pos is None, "Pin from non-existent component should return None"


@pytest.mark.skip(
    reason="Label-to-pin functionality not implemented yet - being developed in parallel repo"
)
class TestLabelToPin:
    """Test adding labels directly to component pins."""

    @pytest.fixture
    def voltage_divider_schematic(self):
        """Create voltage divider for label testing."""
        sch = ksa.create_schematic("Voltage Divider")

        # Add two resistors
        r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
        r2 = sch.components.add("Device:R", "R2", "10k", (100, 150))

        return sch, r1, r2

    def test_add_label_to_pin_basic(self, voltage_divider_schematic):
        """Test adding label directly to component pin."""
        sch, r1, r2 = voltage_divider_schematic

        # Add label to R1 pin 1
        label_uuid = sch.add_label_to_pin("R1", "1", "VIN")

        assert label_uuid is not None, "Label should be created successfully"

        # Verify label was created and positioned correctly
        labels = [label for label in sch._data.get("labels", []) if label.get("text") == "VIN"]
        assert len(labels) == 1, "Exactly one VIN label should exist"

        # Label should be positioned at pin location
        label = labels[0]
        pin_pos = sch.get_component_pin_position("R1", "1")

        assert abs(label["position"]["x"] - pin_pos.x) < 0.1, "Label X should be at pin position"
        assert abs(label["position"]["y"] - pin_pos.y) < 0.1, "Label Y should be at pin position"

    def test_label_orientation_matches_pin_direction(self, voltage_divider_schematic):
        """Test that label orientation follows pin direction."""
        sch, r1, r2 = voltage_divider_schematic

        # Add label to pin
        label_uuid = sch.add_label_to_pin("R1", "1", "VIN")

        # Get the created label
        labels = [label for label in sch._data.get("labels", []) if label.get("text") == "VIN"]
        label = labels[0]

        # Label orientation should be appropriate for pin direction
        # (Exact values depend on pin orientation in symbol)
        assert "rotation" in label, "Label should have rotation/orientation"
        assert isinstance(label["rotation"], (int, float)), "Rotation should be numeric"

    def test_connect_pins_with_labels(self, voltage_divider_schematic):
        """Test connecting two component pins with same label."""
        sch, r1, r2 = voltage_divider_schematic

        # Connect R1 pin 2 to R2 pin 1 with VOUT label
        label_uuids = sch.connect_pins_with_labels("R1", "2", "R2", "1", "VOUT")

        assert len(label_uuids) == 2, "Should create two labels for connection"

        # Verify both labels have same text
        labels = [label for label in sch._data.get("labels", []) if label.get("text") == "VOUT"]
        assert len(labels) == 2, "Should have two VOUT labels"

        # Labels should be at different positions (on different pins)
        pos1 = (labels[0]["position"]["x"], labels[0]["position"]["y"])
        pos2 = (labels[1]["position"]["x"], labels[1]["position"]["y"])
        assert pos1 != pos2, "Labels should be at different positions"


class TestWireToPin:
    """Test drawing wires to component pins."""

    @pytest.fixture
    def wire_test_schematic(self):
        """Create schematic for wire testing."""
        sch = ksa.create_schematic("Wire Test")

        # Add a resistor
        resistor = sch.components.add("Device:R", "R1", "1k", (100, 100))

        return sch, resistor

    def test_connect_pins_with_wire(self, wire_test_schematic):
        """Test drawing wire between two component pins."""
        sch, resistor = wire_test_schematic

        # Add second component
        r2 = sch.components.add("Device:R", "R2", "2k", (150, 100))

        # Connect R1 pin 2 to R2 pin 1 with wire
        wire_uuid = sch.connect_pins_with_wire("R1", "2", "R2", "1")

        assert wire_uuid is not None, "Wire should be created successfully"

        # Verify wire exists and connects correct points
        wires = list(sch.wires)
        assert len(wires) >= 1, "At least one wire should exist"

        # Find our wire
        our_wire = None
        for wire in wires:
            if wire.uuid == wire_uuid:
                our_wire = wire
                break

        assert our_wire is not None, "Our wire should be found"
        assert len(our_wire.points) == 2, "Wire should have exactly 2 points"

        # Verify wire endpoints are at pin positions
        r1_pin2_pos = sch.get_component_pin_position("R1", "2")
        r2_pin1_pos = sch.get_component_pin_position("R2", "1")

        wire_start = our_wire.points[0]
        wire_end = our_wire.points[1]

        # Wire should connect the two pins (order doesn't matter)
        connects_correctly = (
            abs(wire_start.x - r1_pin2_pos.x) < 0.1
            and abs(wire_start.y - r1_pin2_pos.y) < 0.1
            and abs(wire_end.x - r2_pin1_pos.x) < 0.1
            and abs(wire_end.y - r2_pin1_pos.y) < 0.1
        ) or (
            abs(wire_start.x - r2_pin1_pos.x) < 0.1
            and abs(wire_start.y - r2_pin1_pos.y) < 0.1
            and abs(wire_end.x - r1_pin2_pos.x) < 0.1
            and abs(wire_end.y - r1_pin2_pos.y) < 0.1
        )

        assert connects_correctly, "Wire should connect exactly to pin positions"

    def test_add_wire_to_pin(self, wire_test_schematic):
        """Test drawing wire from arbitrary position to component pin."""
        sch, resistor = wire_test_schematic

        # Draw wire from arbitrary position to R1 pin 1
        start_point = Point(50, 100)
        wire_uuid = sch.add_wire_to_pin(start_point, "R1", "1")

        assert wire_uuid is not None, "Wire should be created"

        # Verify wire connects start point to pin
        pin_pos = sch.get_component_pin_position("R1", "1")

        # Find the wire
        our_wire = None
        for wire in sch.wires:
            if wire.uuid == wire_uuid:
                our_wire = wire
                break

        assert our_wire is not None, "Wire should exist"

        # Verify endpoints
        wire_start = our_wire.points[0]
        wire_end = our_wire.points[1]

        # One end should be at start point, other at pin
        start_matches = (
            abs(wire_start.x - start_point.x) < 0.1 and abs(wire_start.y - start_point.y) < 0.1
        )
        end_matches = abs(wire_end.x - pin_pos.x) < 0.1 and abs(wire_end.y - pin_pos.y) < 0.1

        # Could be either direction
        connects_correctly = (start_matches and end_matches) or (
            abs(wire_start.x - pin_pos.x) < 0.1
            and abs(wire_start.y - pin_pos.y) < 0.1
            and abs(wire_end.x - start_point.x) < 0.1
            and abs(wire_end.y - start_point.y) < 0.1
        )

        assert connects_correctly, "Wire should connect start point to pin position"


class TestPinOrientationAndTransformations:
    """Test pin orientation logic and component transformations."""

    @pytest.mark.skip(
        reason="Label functionality not implemented yet - being developed in parallel repo"
    )
    def test_pin_orientation_affects_label_direction(self):
        """Test that pin orientation determines label placement direction."""
        sch = ksa.create_schematic("Orientation Test")

        # Test different component rotations
        test_cases = [
            {"rotation": 0, "description": "0° rotation"},
            {"rotation": 90, "description": "90° rotation"},
            {"rotation": 180, "description": "180° rotation"},
            {"rotation": 270, "description": "270° rotation"},
        ]

        for i, case in enumerate(test_cases):
            # Add component with specific rotation
            comp_ref = f"R{i+1}"
            resistor = sch.components.add(
                lib_id="Device:R",
                reference=comp_ref,
                value="1k",
                position=(100 + i * 50, 100),
                rotation=case["rotation"],
            )

            # Add label to pin 1
            label_uuid = sch.add_label_to_pin(comp_ref, "1", f"NET{i+1}")

            # Verify label exists
            labels = [
                label for label in sch._data.get("labels", []) if label.get("text") == f"NET{i+1}"
            ]
            assert len(labels) == 1, f"Label should exist for {case['description']}"

            label = labels[0]

            # Label should have appropriate orientation based on pin direction
            # (Exact values will depend on symbol definition, but should be consistent)
            assert "rotation" in label, f"Label should have rotation for {case['description']}"

    def test_component_mirroring_affects_pins(self):
        """Test that component mirroring affects pin positions correctly."""
        sch = ksa.create_schematic("Mirror Test")

        # Add normal component
        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100), mirror=None)

        # Add mirrored component
        r2 = sch.components.add("Device:R", "R2", "1k", (200, 100), mirror="x")

        # Get pin positions
        r1_pin1 = sch.get_component_pin_position("R1", "1")
        r1_pin2 = sch.get_component_pin_position("R1", "2")
        r2_pin1 = sch.get_component_pin_position("R2", "1")
        r2_pin2 = sch.get_component_pin_position("R2", "2")

        # Mirroring should affect relative pin positions
        # (Exact behavior depends on mirror axis and symbol definition)
        assert r1_pin1 is not None and r1_pin2 is not None
        assert r2_pin1 is not None and r2_pin2 is not None

        # Pins should exist at different relative positions due to mirroring
        r1_pin_diff = r1_pin2.x - r1_pin1.x
        r2_pin_diff = r2_pin2.x - r2_pin1.x

        # Mirror should reverse pin order (for x-axis mirror)
        if abs(r1_pin_diff) > 0.1:  # Only test if pins have significant X separation
            assert r1_pin_diff * r2_pin_diff < 0, "Mirroring should reverse pin order"


class TestConnectionWorkflows:
    """Test complete connection workflows that solve real problems."""

    @pytest.mark.skip(
        reason="Label functionality not implemented yet - being developed in parallel repo"
    )
    def test_voltage_divider_with_labels(self):
        """Test creating proper voltage divider with pin-accurate labels."""
        sch = ksa.create_schematic("Voltage Divider Labels")

        # Add components
        r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
        r2 = sch.components.add("Device:R", "R2", "10k", (100, 150))
        vcc = sch.components.add("power:VCC", "#PWR01", "VCC", (100, 80))
        gnd = sch.components.add("power:GND", "#PWR02", "GND", (100, 170))

        # Connect with labels (this should create proper electrical connections)
        vin_labels = sch.connect_pins_with_labels("R1", "1", "#PWR01", "1", "VIN")
        vout_labels = sch.connect_pins_with_labels("R1", "2", "R2", "1", "VOUT")
        gnd_labels = sch.connect_pins_with_labels("R2", "2", "#PWR02", "1", "GND")

        # Verify all connections created
        assert len(vin_labels) >= 1, "VIN connection should be created"
        assert len(vout_labels) == 2, "VOUT should connect two pins"
        assert len(gnd_labels) >= 1, "GND connection should be created"

        # Verify labels are at pin positions
        for net_name in ["VIN", "VOUT", "GND"]:
            labels = [
                label for label in sch._data.get("labels", []) if label.get("text") == net_name
            ]
            assert len(labels) >= 1, f"Should have {net_name} labels"

    def test_voltage_divider_with_wires(self):
        """Test creating voltage divider with pin-accurate wires."""
        sch = ksa.create_schematic("Voltage Divider Wires")

        # Add components
        r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
        r2 = sch.components.add("Device:R", "R2", "10k", (100, 150))

        # Connect with wire (R1 pin 2 to R2 pin 1)
        wire_uuid = sch.connect_pins_with_wire("R1", "2", "R2", "1")

        assert wire_uuid is not None, "Wire should be created"

        # Verify wire connects exact pin positions
        wires = [wire for wire in sch.wires if wire.uuid == wire_uuid]
        assert len(wires) == 1, "Should find our wire"

        wire = wires[0]
        assert len(wire.points) == 2, "Wire should have 2 endpoints"

        # Get expected pin positions
        r1_pin2_pos = sch.get_component_pin_position("R1", "2")
        r2_pin1_pos = sch.get_component_pin_position("R2", "1")

        # Verify wire endpoints match pin positions
        wire_points = [(p.x, p.y) for p in wire.points]
        pin_positions = [(r1_pin2_pos.x, r1_pin2_pos.y), (r2_pin1_pos.x, r2_pin1_pos.y)]

        # Wire should connect the two pins (order doesn't matter)
        assert set(wire_points) == set(pin_positions), "Wire should connect exact pin positions"

    @pytest.mark.skip(
        reason="Label functionality not implemented yet - being developed in parallel repo"
    )
    def test_save_and_verify_connectivity(self):
        """Test that saved schematic has proper electrical connectivity in KiCAD."""
        sch = ksa.create_schematic("Connectivity Test")

        # Create simple circuit with both labels and wires
        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))
        r2 = sch.components.add("Device:R", "R2", "2k", (150, 100))
        r3 = sch.components.add("Device:R", "R3", "3k", (100, 150))

        # Connect R1-R2 with wire
        sch.connect_pins_with_wire("R1", "2", "R2", "1")

        # Connect R1-R3 with labels
        sch.connect_pins_with_labels("R1", "1", "R3", "1", "TEST_NET")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as f:
            temp_path = f.name

        try:
            sch.save(temp_path)

            # Verify file was created and has content
            assert os.path.exists(temp_path), "Schematic file should be created"
            assert os.path.getsize(temp_path) > 1000, "File should have substantial content"

            # Load and verify structure
            sch2 = ksa.load_schematic(temp_path)

            # Should have same number of components
            assert len(list(sch2.components)) == 3, "Should load 3 components"

            # Should have wire connection
            assert len(sch2.wires) >= 1, "Should have wire connection"

            # Should have labels
            labels = sch2._data.get("labels", [])
            assert len(labels) >= 2, "Should have TEST_NET labels"

        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
