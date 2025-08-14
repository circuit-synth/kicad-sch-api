"""
Tests for enhanced component management system.
"""

import tempfile
from pathlib import Path

import pytest

from kicad_sch_api.core.components import Component, ComponentCollection
from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point, SchematicSymbol
from kicad_sch_api.utils.validation import ValidationError


class TestComponentManagement:
    """Test enhanced component management features."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sch = Schematic.create("Component Test")

    def test_component_creation_and_access(self):
        """Test creating components and accessing them."""
        # Add component
        comp = self.sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 50),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )

        # Test component properties
        assert comp.reference == "R1"
        assert comp.lib_id == "Device:R"
        assert comp.value == "10k"
        assert comp.position.x == 100
        assert comp.position.y == 50
        assert comp.footprint == "Resistor_SMD:R_0603_1608Metric"

        # Test collection access
        assert len(self.sch.components) == 1
        assert self.sch.components.get("R1") == comp
        assert self.sch.components["R1"] == comp  # Alternative access
        assert "R1" in self.sch.components

    def test_auto_reference_generation(self):
        """Test automatic reference generation."""
        # Add components without specifying reference
        r1 = self.sch.components.add("Device:R", value="10k")
        r2 = self.sch.components.add("Device:R", value="22k")
        c1 = self.sch.components.add("Device:C", value="0.1uF")

        # Should auto-generate appropriate references
        assert r1.reference.startswith("R")
        assert r2.reference.startswith("R")
        assert c1.reference.startswith("C")

        # Should be unique
        refs = {r1.reference, r2.reference, c1.reference}
        assert len(refs) == 3  # All unique

    def test_component_property_management(self):
        """Test component property operations."""
        comp = self.sch.components.add("Device:R", "R1", "10k")

        # Set properties
        comp.set_property("MPN", "RC0603FR-0710KL")
        comp.set_property("Datasheet", "https://example.com/datasheet.pdf")
        comp.set_property("Tolerance", "1%")

        # Get properties
        assert comp.get_property("MPN") == "RC0603FR-0710KL"
        assert comp.get_property("Datasheet") == "https://example.com/datasheet.pdf"
        assert comp.get_property("Tolerance") == "1%"
        assert comp.get_property("NonExistent") is None
        assert comp.get_property("NonExistent", "default") == "default"

        # Properties dictionary access
        assert comp.properties["MPN"] == "RC0603FR-0710KL"
        assert len(comp.properties) == 3

        # Remove property
        success = comp.remove_property("Tolerance")
        assert success is True
        assert comp.get_property("Tolerance") is None
        assert len(comp.properties) == 2

    def test_component_position_and_movement(self):
        """Test component positioning and movement operations."""
        comp = self.sch.components.add("Device:R", "R1", "10k", (100, 50))

        # Test initial position
        assert comp.position == Point(100, 50)

        # Test position update with Point
        comp.position = Point(200, 100)
        assert comp.position.x == 200
        assert comp.position.y == 100

        # Test position update with tuple
        comp.position = (300, 150)
        assert comp.position.x == 300
        assert comp.position.y == 150

        # Test move method
        comp.move(400, 200)
        assert comp.position.x == 400
        assert comp.position.y == 200

        # Test translate method
        comp.translate(50, 25)
        assert comp.position.x == 450
        assert comp.position.y == 225

    def test_component_rotation(self):
        """Test component rotation operations."""
        comp = self.sch.components.add("Device:R", "R1", "10k")

        # Test initial rotation
        assert comp.rotation == 0

        # Test rotation setting
        comp.rotation = 90
        assert comp.rotation == 90

        # Test rotation method
        comp.rotate(45)
        assert comp.rotation == 135

        # Test rotation wrapping
        comp.rotation = 350
        comp.rotate(30)
        assert comp.rotation == 20  # 380 % 360 = 20

    def test_component_collection_filtering(self):
        """Test component collection filtering capabilities."""
        # Add diverse components
        components = [
            ("Device:R", "R1", "10k", (100, 50)),
            ("Device:R", "R2", "22k", (150, 50)),
            ("Device:R", "R3", "1k", (200, 50)),
            ("Device:C", "C1", "0.1uF", (100, 100)),
            ("Device:C", "C2", "1uF", (150, 100)),
            ("Device:L", "L1", "10uH", (200, 100)),
        ]

        for lib_id, ref, value, pos in components:
            self.sch.components.add(lib_id, ref, value, pos)

        # Test lib_id filtering
        resistors = self.sch.components.filter(lib_id="Device:R")
        assert len(resistors) == 3
        assert all(comp.lib_id == "Device:R" for comp in resistors)

        # Test value filtering
        exact_10k = self.sch.components.filter(value="10k")
        assert len(exact_10k) == 1
        assert exact_10k[0].reference == "R1"

        # Test value pattern filtering
        k_values = self.sch.components.filter(value_pattern="k")
        assert len(k_values) == 4  # R1, R2, R3, L1 (10k, 22k, 1k, 10uH)

        # Test reference pattern filtering
        r_components = self.sch.components.filter(reference_pattern=r"R\d+")
        assert len(r_components) == 3

        # Test area filtering
        top_components = self.sch.components.in_area(90, 40, 210, 60)
        expected_top = {"R1", "R2", "R3"}
        actual_top = {comp.reference for comp in top_components}
        assert actual_top == expected_top

        # Test proximity filtering
        near_r1 = self.sch.components.near_point((100, 50), radius=30)
        assert len(near_r1) >= 1
        assert any(comp.reference == "R1" for comp in near_r1)

    def test_bulk_operations(self):
        """Test bulk update operations."""
        # Add many resistors
        for i in range(10):
            self.sch.components.add("Device:R", f"R{i+1}", "10k", (i * 20, 50))

        # Bulk update all resistors
        updated_count = self.sch.components.bulk_update(
            criteria={"lib_id": "Device:R"},
            updates={
                "footprint": "Resistor_SMD:R_0603_1608Metric",
                "properties": {"Tolerance": "1%", "Power": "0.1W"},
            },
        )

        assert updated_count == 10

        # Verify updates were applied
        for comp in self.sch.components.filter(lib_id="Device:R"):
            assert comp.footprint == "Resistor_SMD:R_0603_1608Metric"
            assert comp.get_property("Tolerance") == "1%"
            assert comp.get_property("Power") == "0.1W"

    def test_component_collection_iteration(self):
        """Test iterating over component collection."""
        # Add components
        refs = ["R1", "R2", "C1", "L1"]
        for ref in refs:
            self.sch.components.add("Device:R", ref, "10k")

        # Test iteration
        collected_refs = []
        for comp in self.sch.components:
            collected_refs.append(comp.reference)

        assert len(collected_refs) == 4
        assert set(collected_refs) == set(refs)

        # Test list-like access
        first_comp = self.sch.components[0]
        assert isinstance(first_comp, Component)

        # Test length
        assert len(self.sch.components) == 4

    def test_component_validation(self):
        """Test component-level validation."""
        comp = self.sch.components.add("Device:R", "R1", "10k")

        # Valid component should have no issues
        issues = comp.validate()
        errors = [issue for issue in issues if issue.level.value in ("error", "critical")]
        assert len(errors) == 0

    def test_component_dictionary_representation(self):
        """Test component dictionary conversion."""
        comp = self.sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 50),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )
        comp.set_property("MPN", "RC0603FR-0710KL")

        comp_dict = comp.to_dict()

        # Verify dictionary structure
        expected_keys = {
            "reference",
            "lib_id",
            "value",
            "footprint",
            "position",
            "rotation",
            "properties",
            "in_bom",
            "on_board",
            "pin_count",
        }
        assert set(comp_dict.keys()) == expected_keys

        # Verify values
        assert comp_dict["reference"] == "R1"
        assert comp_dict["lib_id"] == "Device:R"
        assert comp_dict["value"] == "10k"
        assert comp_dict["position"] == {"x": 100, "y": 50}
        assert comp_dict["properties"]["MPN"] == "RC0603FR-0710KL"

    def test_component_string_representations(self):
        """Test component string and repr methods."""
        comp = self.sch.components.add("Device:R", "R1", "10k", (100, 50))

        # Test __str__
        str_repr = str(comp)
        assert "R1" in str_repr
        assert "Device:R" in str_repr
        assert "10k" in str_repr

        # Test __repr__
        repr_str = repr(comp)
        assert "Component" in repr_str
        assert "R1" in repr_str
        assert "Device:R" in repr_str

    def test_collection_statistics(self):
        """Test component collection statistics."""
        # Add diverse components
        self.sch.components.add("Device:R", "R1", "10k")
        self.sch.components.add("Device:R", "R2", "10k")  # Same value
        self.sch.components.add("Device:R", "R3", "22k")
        self.sch.components.add("Device:C", "C1", "0.1uF")

        stats = self.sch.components.get_statistics()

        # Verify statistics
        assert stats["total_components"] == 4
        assert stats["unique_references"] == 4
        assert stats["libraries_used"] == 2  # Device for R and C

        # Check library breakdown
        lib_breakdown = stats["library_breakdown"]
        assert lib_breakdown["Device"] == 4  # All from Device library

        # Check most common values
        common_values = stats["most_common_values"]
        assert len(common_values) > 0
        # Should have (value, count) tuples
        assert common_values[0][0] == "10k"  # Most common value
        assert common_values[0][1] == 2  # Appears twice
