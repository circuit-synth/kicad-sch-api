#!/usr/bin/env python3
"""
Reference tests for hierarchical label rotation using manually created KiCad schematics.

These tests verify that our hierarchical label rotation handling matches real KiCad format
from manually created schematics with hierarchical labels.
"""

import pytest

import kicad_sch_api as ksa


class TestHierarchicalLabelRotationReference:
    """Test hierarchical label rotation against reference KiCad schematics."""

    def test_hierarchical_label_structure(self):
        """Test hierarchical label structure against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/hierarchical_label_rotations/hierarchical_label_rotations.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Find all hierarchical labels in the schematic
        hierarchical_labels = {}
        if "hierarchical_labels" in sch._data:
            for hlabel_data in sch._data["hierarchical_labels"]:
                text = hlabel_data.get("text", "")
                hierarchical_labels[text] = hlabel_data

        # Verify we have at least one hierarchical label
        assert len(hierarchical_labels) > 0, "Schematic should have at least one hierarchical label"

        # Verify structure of each hierarchical label
        for text, hlabel in hierarchical_labels.items():
            assert "text" in hlabel, f"Hierarchical label '{text}' should have 'text' field"
            assert "shape" in hlabel, f"Hierarchical label '{text}' should have 'shape' field"
            assert "position" in hlabel, f"Hierarchical label '{text}' should have 'position' field"
            assert "rotation" in hlabel, f"Hierarchical label '{text}' should have 'rotation' field"
            assert "size" in hlabel, f"Hierarchical label '{text}' should have 'size' field"
            assert "uuid" in hlabel, f"Hierarchical label '{text}' should have 'uuid' field"

            # Verify rotation is a valid numeric value
            rotation = hlabel.get("rotation", 0)
            assert isinstance(
                rotation, (int, float)
            ), f"Hierarchical label '{text}' rotation should be numeric: got {rotation}"
            assert (
                0 <= rotation < 360
            ), f"Hierarchical label '{text}' rotation should be 0-359°: got {rotation}"

    def test_hierarchical_label_loading(self):
        """Verify hierarchical labels can be loaded successfully."""
        sch_path = "tests/reference_kicad_projects/hierarchical_label_rotations/hierarchical_label_rotations.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        assert sch is not None, "Schematic should load successfully"
        assert "hierarchical_labels" in sch._data, "Schematic should have hierarchical_labels key"

        hierarchical_labels = sch._data["hierarchical_labels"]
        assert isinstance(hierarchical_labels, list), "Hierarchical labels should be a list"
        assert len(hierarchical_labels) > 0, "Schematic should have at least one hierarchical label"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
