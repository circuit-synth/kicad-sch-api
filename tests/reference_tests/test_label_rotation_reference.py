#!/usr/bin/env python3
"""
Reference tests for label rotation using manually created KiCad schematics.

These tests verify that our label rotation handling matches real KiCad format
from manually created schematics with rotated labels.
"""

import pytest

import kicad_sch_api as ksa


class TestLabelRotationReference:
    """Test label rotation against reference KiCad schematics."""

    def test_label_rotations_reference(self):
        """Test all label rotations against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/label_rotations/label_rotations.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Find all labels in the schematic
        labels = {}
        if "labels" in sch._data:
            for label_data in sch._data["labels"]:
                text = label_data.get("text", "")
                labels[text] = label_data

        # Verify we have all 4 rotation labels
        assert "LABEL_0" in labels, "LABEL_0 should exist in schematic"
        assert "LABEL_90" in labels, "LABEL_90 should exist in schematic"
        assert "LABEL_180" in labels, "LABEL_180 should exist in schematic"
        assert "LABEL_270" in labels, "LABEL_270 should exist in schematic"

        # Extract rotation from label data
        rotation_0 = labels["LABEL_0"].get("rotation", 0)
        rotation_90 = labels["LABEL_90"].get("rotation", 0)
        rotation_180 = labels["LABEL_180"].get("rotation", 0)
        rotation_270 = labels["LABEL_270"].get("rotation", 0)

        assert rotation_0 == 0, f"LABEL_0 should be at 0° rotation: got {rotation_0}"
        assert rotation_90 == 90, f"LABEL_90 should be at 90° rotation: got {rotation_90}"
        assert rotation_180 == 180, f"LABEL_180 should be at 180° rotation: got {rotation_180}"
        assert rotation_270 == 270, f"LABEL_270 should be at 270° rotation: got {rotation_270}"

    @pytest.mark.parametrize(
        "label_name,expected_rotation",
        [
            ("LABEL_0", 0),
            ("LABEL_90", 90),
            ("LABEL_180", 180),
            ("LABEL_270", 270),
        ],
    )
    def test_individual_label_rotations(self, label_name, expected_rotation):
        """Verify each label rotation individually."""
        sch_path = "tests/reference_kicad_projects/label_rotations/label_rotations.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Find the specific label
        label_data = None
        if "labels" in sch._data:
            for label in sch._data["labels"]:
                if label.get("text") == label_name:
                    label_data = label
                    break

        assert label_data is not None, f"{label_name} should exist in schematic"

        # Extract rotation from label data
        rotation = label_data.get("rotation", 0)

        assert (
            rotation == expected_rotation
        ), f"{label_name} should be at {expected_rotation}° rotation: got {rotation}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
