"""
Unit tests for basic API workflow from user example.

This test file validates the basic workflow that Tom demonstrated,
ensuring all core API features work together correctly.
"""

import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa


class TestBasicAPIWorkflow:
    """Test basic API workflow with component creation, wiring, and saving."""

    def test_create_schematic(self):
        """Test creating a new schematic."""
        sch = ksa.create_schematic("My Circuit")

        assert sch is not None
        assert sch.name == "My Circuit"
        assert len(list(sch.components)) == 0
        assert len(list(sch.wires)) == 0

    def test_add_component_with_all_properties(self):
        """Test adding a component with all properties specified."""
        sch = ksa.create_schematic("My Circuit")

        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )

        assert resistor is not None
        assert resistor.reference == "R1"
        assert resistor.value == "10k"
        assert resistor.lib_id == "Device:R"
        assert resistor.footprint == "Resistor_SMD:R_0603_1608Metric"
        # Position may be grid-aligned, so check it's close to requested position
        assert abs(resistor.position.x - 100.0) < 1.0
        assert abs(resistor.position.y - 100.0) < 1.0

    def test_add_multiple_components(self):
        """Test adding multiple components to schematic."""
        sch = ksa.create_schematic("My Circuit")

        r1 = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100.0, 100.0)
        )

        c1 = sch.components.add(
            lib_id="Device:C", reference="C1", value="100nF", position=(150.0, 100.0)
        )

        components = list(sch.components)
        assert len(components) == 2
        assert r1.reference == "R1"
        assert c1.reference == "C1"

    def test_add_wire_between_points(self):
        """Test adding a simple wire between two points."""
        sch = ksa.create_schematic("My Circuit")

        wire = sch.wires.add(start=(100, 110), end=(150, 110))

        assert wire is not None
        wires = list(sch.wires)
        assert len(wires) == 1

    def test_add_label(self):
        """Test adding a label to the schematic."""
        sch = ksa.create_schematic("My Circuit")

        label_uuid = sch.add_label("VCC", position=(125, 110))

        assert label_uuid is not None
        labels = list(sch.labels)
        assert len(labels) == 1
        assert labels[0].text == "VCC"

    def test_complete_workflow(self, tmp_path):
        """Test complete workflow: create, add components, wire, label, save."""
        # Create schematic
        sch = ksa.create_schematic("My Circuit")

        # Add resistor component
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )

        # Add capacitor component
        capacitor = sch.components.add(
            lib_id="Device:C", reference="C1", value="100nF", position=(150.0, 100.0)
        )

        # Add wire between points
        wire = sch.wires.add(start=(100, 110), end=(150, 110))

        # Add label
        label = sch.add_label("VCC", position=(125, 110))

        # Verify all elements were added
        assert len(list(sch.components)) == 2
        assert len(list(sch.wires)) == 1
        assert len(list(sch.labels)) == 1

        # Save to temporary file
        temp_file = tmp_path / "my_circuit.kicad_sch"
        sch.save(str(temp_file))

        # Verify file was created
        assert temp_file.exists()
        assert temp_file.stat().st_size > 0

    def test_round_trip_save_load(self, tmp_path):
        """Test that schematic can be saved and loaded without data loss."""
        # Create and populate schematic
        sch1 = ksa.create_schematic("My Circuit")

        sch1.components.add(lib_id="Device:R", reference="R1", value="10k", position=(100.0, 100.0))

        sch1.components.add(
            lib_id="Device:C", reference="C1", value="100nF", position=(150.0, 100.0)
        )

        sch1.wires.add(start=(100, 110), end=(150, 110))
        sch1.add_label("VCC", position=(125, 110))

        # Save
        temp_file = tmp_path / "my_circuit.kicad_sch"
        sch1.save(str(temp_file))

        # Load
        sch2 = ksa.Schematic.load(str(temp_file))

        # Verify components
        comps = list(sch2.components)
        assert len(comps) == 2
        assert comps[0].reference == "R1"
        assert comps[0].value == "10k"
        assert comps[1].reference == "C1"
        assert comps[1].value == "100nF"

        # Verify wires
        wires = list(sch2.wires)
        assert len(wires) == 1

        # Verify labels
        labels = list(sch2.labels)
        assert len(labels) == 1
        assert labels[0].text == "VCC"

    def test_api_usage_from_documentation(self):
        """Test the exact API usage pattern from documentation."""
        # This is the workflow from CLAUDE.md examples
        sch = ksa.create_schematic("My Circuit")

        # Add component with all documented parameters
        resistor = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100, 100)
        )

        # Verify basic properties
        assert resistor.reference == "R1"
        assert resistor.value == "10k"

        # Add wires
        sch.wires.add(start=(100, 110), end=(150, 110))

        # Add label
        sch.add_label("VCC", position=(125, 110))

        # Verify everything is present
        assert len(list(sch.components)) == 1
        assert len(list(sch.wires)) == 1
        assert len(list(sch.labels)) == 1


class TestComponentCreationVariants:
    """Test various ways to create and configure components."""

    def test_component_with_minimal_params(self):
        """Test component creation with only required parameters."""
        sch = ksa.create_schematic("Test")

        comp = sch.components.add(lib_id="Device:R", value="10k")

        assert comp is not None
        assert comp.value == "10k"
        assert comp.lib_id == "Device:R"

    def test_component_auto_positioning(self):
        """Test that components can be created without explicit position."""
        sch = ksa.create_schematic("Test")

        comp = sch.components.add(lib_id="Device:C", reference="C1", value="100nF")

        # Should have some position assigned
        assert comp.position is not None
        assert isinstance(comp.position.x, (int, float))
        assert isinstance(comp.position.y, (int, float))

    def test_component_auto_reference(self):
        """Test that component references are auto-generated if not provided."""
        sch = ksa.create_schematic("Test")

        comp = sch.components.add(lib_id="Device:R", value="10k")

        # Should have auto-generated reference
        assert comp.reference is not None
        # Reference should be a valid identifier (may start with any letter or U for generic)
        assert len(comp.reference) > 0
        assert comp.reference[0].isalpha()


class TestWiringVariants:
    """Test various wiring scenarios."""

    def test_horizontal_wire(self):
        """Test creating a horizontal wire."""
        sch = ksa.create_schematic("Test")

        wire = sch.wires.add(start=(100, 100), end=(200, 100))

        assert wire is not None
        assert len(list(sch.wires)) == 1

    def test_vertical_wire(self):
        """Test creating a vertical wire."""
        sch = ksa.create_schematic("Test")

        wire = sch.wires.add(start=(100, 100), end=(100, 200))

        assert wire is not None
        assert len(list(sch.wires)) == 1

    def test_diagonal_wire(self):
        """Test creating a diagonal wire."""
        sch = ksa.create_schematic("Test")

        wire = sch.wires.add(start=(100, 100), end=(200, 200))

        assert wire is not None
        assert len(list(sch.wires)) == 1

    def test_multiple_wires(self):
        """Test creating multiple wires."""
        sch = ksa.create_schematic("Test")

        wire1 = sch.wires.add(start=(100, 100), end=(200, 100))
        wire2 = sch.wires.add(start=(200, 100), end=(200, 200))
        wire3 = sch.wires.add(start=(200, 200), end=(100, 200))

        wires = list(sch.wires)
        assert len(wires) == 3


class TestLabelsVariants:
    """Test various label scenarios."""

    def test_simple_label(self):
        """Test creating a simple label."""
        sch = ksa.create_schematic("Test")

        label_uuid = sch.add_label("VCC", position=(100, 100))

        assert label_uuid is not None
        labels = list(sch.labels)
        assert len(labels) == 1
        assert labels[0].text == "VCC"

    def test_multiple_labels(self):
        """Test creating multiple labels."""
        sch = ksa.create_schematic("Test")

        label1 = sch.add_label("VCC", position=(100, 100))
        label2 = sch.add_label("GND", position=(100, 200))
        label3 = sch.add_label("DATA", position=(200, 100))

        labels = list(sch.labels)
        assert len(labels) == 3

    def test_label_text_variations(self):
        """Test labels with various text content."""
        sch = ksa.create_schematic("Test")

        test_texts = ["VCC", "GND", "CLK", "DATA[0]", "ADDR[15:0]"]

        for i, text in enumerate(test_texts):
            label_uuid = sch.add_label(text, position=(100 + i * 50, 100))
            assert label_uuid is not None

        labels = list(sch.labels)
        assert len(labels) == len(test_texts)
        # Verify all expected text values are present
        label_texts = {label.text for label in labels}
        assert label_texts == set(test_texts)
