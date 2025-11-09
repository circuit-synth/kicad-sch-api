#!/usr/bin/env python3
"""
Reference tests for rectangles using manually created KiCad schematics.

These tests verify that our rectangle handling matches real KiCad format
from manually created schematics with rectangles.
"""

import pytest

import kicad_sch_api as ksa


class TestRectanglesReference:
    """Test rectangles against reference KiCad schematics."""

    def test_rectangles_structure(self):
        """Test rectangle structure against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/rectangles/rectangles.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Verify rectangles exist
        assert "rectangles" in sch._data, "Schematic should have rectangles key"
        rectangles = sch._data["rectangles"]
        assert isinstance(rectangles, list), "Rectangles should be a list"
        assert len(rectangles) == 3, "Should have exactly 3 rectangles"

        # Verify structure of each rectangle
        for i, rect in enumerate(rectangles):
            assert "start" in rect, f"Rectangle {i} should have 'start' field"
            assert "end" in rect, f"Rectangle {i} should have 'end' field"
            assert "stroke_width" in rect, f"Rectangle {i} should have 'stroke_width' field"
            assert "stroke_type" in rect, f"Rectangle {i} should have 'stroke_type' field"
            assert "fill_type" in rect, f"Rectangle {i} should have 'fill_type' field"
            assert "uuid" in rect, f"Rectangle {i} should have 'uuid' field"

            # Verify start/end have x and y
            assert "x" in rect["start"], f"Rectangle {i} start should have 'x'"
            assert "y" in rect["start"], f"Rectangle {i} start should have 'y'"
            assert "x" in rect["end"], f"Rectangle {i} end should have 'x'"
            assert "y" in rect["end"], f"Rectangle {i} end should have 'y'"

    def test_rectangle_stroke_types(self):
        """Verify different stroke types are handled correctly."""
        sch_path = "tests/reference_kicad_projects/rectangles/rectangles.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        rectangles = sch._data["rectangles"]

        # Extract stroke types from all rectangles
        stroke_types = [rect["stroke_type"] for rect in rectangles]

        # Should have solid and dash stroke types
        assert "solid" in stroke_types, "Should have at least one solid rectangle"
        assert "dash" in stroke_types, "Should have at least one dashed rectangle"

    def test_rectangle_fill_types(self):
        """Verify different fill types are handled correctly."""
        sch_path = "tests/reference_kicad_projects/rectangles/rectangles.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        rectangles = sch._data["rectangles"]

        # Extract fill types from all rectangles
        fill_types = [rect["fill_type"] for rect in rectangles]

        # Should have both none and background fill types
        assert "none" in fill_types, "Should have at least one unfilled rectangle"
        assert "background" in fill_types, "Should have at least one filled rectangle"

    def test_rectangle_coordinates(self):
        """Verify rectangle coordinates are loaded correctly."""
        sch_path = "tests/reference_kicad_projects/rectangles/rectangles.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        rectangles = sch._data["rectangles"]

        # Verify first rectangle has expected coordinates
        rect0 = rectangles[0]
        assert rect0["start"]["x"] == 100.0
        assert rect0["start"]["y"] == 100.0
        assert rect0["end"]["x"] == 150.0
        assert rect0["end"]["y"] == 130.0

    def test_rectangle_loading(self):
        """Verify rectangles can be loaded successfully."""
        sch_path = "tests/reference_kicad_projects/rectangles/rectangles.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        assert sch is not None, "Schematic should load successfully"
        assert "rectangles" in sch._data, "Schematic should have rectangles"

        rectangles = sch._data["rectangles"]
        assert len(rectangles) == 3, "Should have exactly 3 rectangles"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
