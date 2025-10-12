#!/usr/bin/env python3
"""
Test removal functionality for wires, labels, and other schematic elements.

Validates that all removal methods work correctly and maintain schematic integrity.
"""

import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa


class TestElementRemoval:
    """Test removal of various schematic elements."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "reference_tests"
        self.reference_dir = self.test_dir / "reference_kicad_projects"

    def test_wire_removal(self):
        """Test wire removal functionality."""
        sch = ksa.create_schematic("test_wire_removal")

        # Add a wire
        wire_uuid = sch.wires.add(start=(100, 100), end=(150, 100))
        assert len(sch.wires) == 1, "Should have 1 wire after adding"

        # Remove the wire
        removed = sch.remove_wire(wire_uuid)
        assert removed, "Wire removal should succeed"
        assert len(sch.wires) == 0, "Should have 0 wires after removal"

        # Try removing non-existent wire
        removed = sch.remove_wire("fake-uuid")
        assert not removed, "Removing non-existent wire should return False"

    def test_label_removal(self):
        """Test label removal functionality."""
        sch = ksa.create_schematic("test_label_removal")

        # Add a label
        label_uuid = sch.add_label("TEST_LABEL", position=(100, 100))
        assert "labels" in sch._data and len(sch._data["labels"]) == 1, "Should have 1 label"

        # Remove the label
        removed = sch.remove_label(label_uuid)
        assert removed, "Label removal should succeed"
        assert "labels" not in sch._data or len(sch._data["labels"]) == 0, "Should have 0 labels"

        # Try removing non-existent label
        removed = sch.remove_label("fake-uuid")
        assert not removed, "Removing non-existent label should return False"

    def test_hierarchical_label_removal(self):
        """Test hierarchical label removal functionality."""
        sch = ksa.create_schematic("test_hier_label_removal")

        # Add a hierarchical label
        label_uuid = sch.add_hierarchical_label("HIER_LABEL", position=(100, 100))
        assert (
            "hierarchical_labels" in sch._data and len(sch._data["hierarchical_labels"]) == 1
        ), "Should have 1 hierarchical label"

        # Remove the hierarchical label
        removed = sch.remove_hierarchical_label(label_uuid)
        assert removed, "Hierarchical label removal should succeed"
        assert (
            "hierarchical_labels" not in sch._data or len(sch._data["hierarchical_labels"]) == 0
        ), "Should have 0 hierarchical labels"

        # Try removing non-existent hierarchical label
        removed = sch.remove_hierarchical_label("fake-uuid")
        assert not removed, "Removing non-existent hierarchical label should return False"

    def test_junction_removal(self):
        """Test junction removal functionality."""
        sch = ksa.create_schematic("test_junction_removal")

        # Add a junction
        junction_uuid = sch.junctions.add(position=(100, 100))
        assert len(sch.junctions) == 1, "Should have 1 junction after adding"

        # Remove the junction
        removed = sch.junctions.remove(junction_uuid)
        assert removed, "Junction removal should succeed"
        assert len(sch.junctions) == 0, "Should have 0 junctions after removal"

        # Try removing non-existent junction
        removed = sch.junctions.remove("fake-uuid")
        assert not removed, "Removing non-existent junction should return False"

    def test_wire_collection_removal(self):
        """Test wire removal via WireCollection."""
        sch = ksa.create_schematic("test_wire_collection_removal")

        # Add a wire
        wire_uuid = sch.wires.add(start=(100, 100), end=(150, 100))
        assert len(sch.wires) == 1, "Should have 1 wire after adding"

        # Remove via collection
        removed = sch.wires.remove(wire_uuid)
        assert removed, "Wire removal via collection should succeed"
        assert len(sch.wires) == 0, "Should have 0 wires after removal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
