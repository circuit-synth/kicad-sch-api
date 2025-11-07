"""
Unit tests for automatic label placement on component pins.

Tests the add_label() pin parameter feature that automatically positions
and rotates labels based on pin location and orientation.
"""

import pytest
import kicad_sch_api as ksa


class TestLabelPinPlacement:
    """Test automatic label placement on component pins."""

    def test_label_on_resistor_0deg_pin1(self):
        """Test label placement on pin 1 of resistor at 0° rotation."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0)

        label_uuid = sch.add_label("VCC", pin=("R1", "1"))

        # Verify label was created
        assert label_uuid is not None
        label = sch._labels.get(label_uuid)
        assert label is not None
        assert label.text == "VCC"

        # Verify position matches pin 1 (top pin at 0° rotation)
        assert label.position.x == pytest.approx(100.33, abs=0.01)
        assert label.position.y == pytest.approx(96.52, abs=0.01)

        # Verify rotation (should face away from component)
        assert label.rotation == pytest.approx(90.0, abs=0.1)

        # Verify justification
        assert label._data.justify_h == "left"
        assert label._data.justify_v == "bottom"

    def test_label_on_resistor_0deg_pin2(self):
        """Test label placement on pin 2 of resistor at 0° rotation."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0)

        label_uuid = sch.add_label("GND", pin=("R1", "2"))

        label = sch._labels.get(label_uuid)
        assert label.text == "GND"

        # Verify position matches pin 2 (bottom pin at 0° rotation)
        assert label.position.x == pytest.approx(100.33, abs=0.01)
        assert label.position.y == pytest.approx(104.14, abs=0.01)

        # Verify rotation
        assert label.rotation == pytest.approx(270.0, abs=0.1)

        # Verify justification
        assert label._data.justify_h == "right"
        assert label._data.justify_v == "bottom"

    def test_label_on_resistor_90deg(self):
        """Test label placement on resistor at 90° rotation."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=90)

        # Pin 1 should be on right side
        label_uuid = sch.add_label("VCC", pin=("R1", "1"))
        label = sch._labels.get(label_uuid)

        assert label.position.x == pytest.approx(104.14, abs=0.01)
        assert label.position.y == pytest.approx(100.33, abs=0.01)
        assert label.rotation == pytest.approx(180.0, abs=0.1)
        assert label._data.justify_h == "left"

    def test_label_on_resistor_180deg(self):
        """Test label placement on resistor at 180° rotation."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=180)

        # Pin 1 should be on bottom
        label_uuid = sch.add_label("VCC", pin=("R1", "1"))
        label = sch._labels.get(label_uuid)

        assert label.position.x == pytest.approx(100.33, abs=0.01)
        assert label.position.y == pytest.approx(104.14, abs=0.01)
        assert label.rotation == pytest.approx(270.0, abs=0.1)
        assert label._data.justify_h == "right"

    def test_label_on_resistor_270deg(self):
        """Test label placement on resistor at 270° rotation."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=270)

        # Pin 1 should be on left side
        label_uuid = sch.add_label("VCC", pin=("R1", "1"))
        label = sch._labels.get(label_uuid)

        assert label.position.x == pytest.approx(96.52, abs=0.01)
        assert label.position.y == pytest.approx(100.33, abs=0.01)
        assert label.rotation == pytest.approx(0.0, abs=0.1)
        assert label._data.justify_h == "right"

    def test_label_with_position_parameter_still_works(self):
        """Test that traditional position-based label placement still works."""
        sch = ksa.create_schematic("Test")

        label_uuid = sch.add_label("TEST", position=(50.0, 50.0), rotation=45.0)

        label = sch._labels.get(label_uuid)
        assert label.text == "TEST"
        assert label.position.x == pytest.approx(50.0)
        assert label.position.y == pytest.approx(50.0)
        assert label.rotation == pytest.approx(45.0)

    def test_label_pin_requires_either_position_or_pin(self):
        """Test that add_label() requires either position or pin parameter."""
        sch = ksa.create_schematic("Test")

        with pytest.raises(ValueError, match="Either position or pin must be provided"):
            sch.add_label("TEST")

    def test_label_pin_cannot_have_both_position_and_pin(self):
        """Test that add_label() cannot have both position and pin."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        with pytest.raises(ValueError, match="Cannot provide both position and pin"):
            sch.add_label("TEST", position=(50.0, 50.0), pin=("R1", "1"))

    def test_label_pin_component_not_found(self):
        """Test error handling when component not found."""
        sch = ksa.create_schematic("Test")

        with pytest.raises(ValueError, match="Component NONEXISTENT not found"):
            sch.add_label("TEST", pin=("NONEXISTENT", "1"))

    def test_label_pin_number_not_found(self):
        """Test error handling when pin number not found."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        with pytest.raises(ValueError, match="Pin 99 not found on component R1"):
            sch.add_label("TEST", pin=("R1", "99"))

    def test_label_pin_custom_rotation_override(self):
        """Test that explicit rotation parameter overrides auto-calculated rotation."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0)

        # Provide explicit rotation - should override auto-calculation
        label_uuid = sch.add_label("VCC", pin=("R1", "1"), rotation=45.0)

        label = sch._labels.get(label_uuid)
        assert label.rotation == pytest.approx(45.0, abs=0.1)

    def test_label_roundtrip_preserves_justification(self):
        """Test that label justification is preserved through save/load cycle."""
        sch = ksa.create_schematic("Test")
        sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0), rotation=0)
        sch.add_label("VCC", pin=("R1", "1"))
        sch.add_label("GND", pin=("R1", "2"))

        # Save and reload
        sch.save("test_label_roundtrip.kicad_sch")
        sch2 = ksa.Schematic.load("test_label_roundtrip.kicad_sch")

        # Find labels
        vcc_labels = [l for l in sch2._labels if l.text == "VCC"]
        gnd_labels = [l for l in sch2._labels if l.text == "GND"]

        assert len(vcc_labels) == 1
        assert len(gnd_labels) == 1

        # Verify justification preserved
        assert vcc_labels[0]._data.justify_h == "left"
        assert vcc_labels[0]._data.justify_v == "bottom"
        assert gnd_labels[0]._data.justify_h == "right"
        assert gnd_labels[0]._data.justify_v == "bottom"
