#!/usr/bin/env python3
"""
Reference tests for text rotation using manually created KiCad schematics.

These tests verify that our text rotation handling matches real KiCad format
from manually created schematics with rotated text elements.
"""

import pytest

import kicad_sch_api as ksa


class TestTextRotationReference:
    """Test text rotation against reference KiCad schematics."""

    def test_text_rotations_reference(self):
        """Test all text rotations against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/text_rotations/text_rotations.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Find all text elements in the schematic
        texts = {}
        if "texts" in sch._data:
            for text_data in sch._data["texts"]:
                text_content = text_data.get("text", "")
                texts[text_content] = text_data

        # Verify we have all 4 rotation text elements
        assert "TEXT_0" in texts, "TEXT_0 should exist in schematic"
        assert "TEXT_90" in texts, "TEXT_90 should exist in schematic"
        assert "TEXT_180" in texts, "TEXT_180 should exist in schematic"
        assert "TEXT_270" in texts, "TEXT_270 should exist in schematic"

        # Extract rotation from text data
        rotation_0 = texts["TEXT_0"].get("rotation", 0)
        rotation_90 = texts["TEXT_90"].get("rotation", 0)
        rotation_180 = texts["TEXT_180"].get("rotation", 0)
        rotation_270 = texts["TEXT_270"].get("rotation", 0)

        assert rotation_0 == 0, f"TEXT_0 should be at 0° rotation: got {rotation_0}"
        assert rotation_90 == 90, f"TEXT_90 should be at 90° rotation: got {rotation_90}"
        assert rotation_180 == 180, f"TEXT_180 should be at 180° rotation: got {rotation_180}"
        assert rotation_270 == 270, f"TEXT_270 should be at 270° rotation: got {rotation_270}"

    @pytest.mark.parametrize(
        "text_name,expected_rotation",
        [
            ("TEXT_0", 0),
            ("TEXT_90", 90),
            ("TEXT_180", 180),
            ("TEXT_270", 270),
        ],
    )
    def test_individual_text_rotations(self, text_name, expected_rotation):
        """Verify each text rotation individually."""
        sch_path = "tests/reference_kicad_projects/text_rotations/text_rotations.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Find the specific text element
        text_data = None
        if "texts" in sch._data:
            for text in sch._data["texts"]:
                if text.get("text") == text_name:
                    text_data = text
                    break

        assert text_data is not None, f"{text_name} should exist in schematic"

        # Extract rotation from text data
        rotation = text_data.get("rotation", 0)

        assert (
            rotation == expected_rotation
        ), f"{text_name} should be at {expected_rotation}° rotation: got {rotation}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
