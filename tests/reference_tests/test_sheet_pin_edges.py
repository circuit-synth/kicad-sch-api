"""
Reference test for sheet pin edges against manually created KiCAD schematic.

This test verifies that our programmatic sheet pin creation produces output
that exactly matches KiCAD's format when manually creating sheet pins.
"""

from pathlib import Path

import pytest

import kicad_sch_api as ksa


class TestSheetPinEdgesReference:
    """Test sheet pin edge positioning against KiCAD reference."""

    @pytest.fixture
    def reference_dir(self):
        """Get reference project directory."""
        return Path(__file__).parent / "reference_kicad_projects" / "sheet_pin_edges"

    @pytest.fixture
    def reference_schematic(self, reference_dir):
        """Load the manually created reference schematic."""
        ref_path = reference_dir / "sheet_pin_edges.kicad_sch"
        return ksa.Schematic.load(str(ref_path))

    def test_reference_sheet_exists(self, reference_schematic):
        """Verify reference schematic has a sheet with pins."""
        sheets = reference_schematic._data.get("sheets", [])
        assert len(sheets) == 1, "Reference should have exactly one sheet"

        sheet = sheets[0]
        assert sheet["name"] == "SubSheet"
        assert sheet["position"]["x"] == 100
        assert sheet["position"]["y"] == 100
        assert sheet["size"]["width"] == 50
        assert sheet["size"]["height"] == 40

        # Should have 4 pins
        pins = sheet.get("pins", [])
        assert len(pins) == 4, "Reference sheet should have 4 pins"

    def test_right_edge_pin_matches_reference(self, reference_schematic):
        """Verify right edge pin matches KiCAD reference format."""
        sheets = reference_schematic._data.get("sheets", [])
        sheet = sheets[0]
        pins = sheet.get("pins", [])

        # Find PIN_RIGHT
        right_pin = [p for p in pins if p["name"] == "PIN_RIGHT"][0]

        # Verify all attributes match KiCAD format
        assert right_pin["pin_type"] == "input"
        assert right_pin["position"]["x"] == 150  # Right edge
        assert right_pin["position"]["y"] == 118.11  # Position along edge
        assert right_pin["rotation"] == 0  # Faces right
        assert right_pin["justify"] == "right"
        assert right_pin["size"] == 1.27

    def test_bottom_edge_pin_matches_reference(self, reference_schematic):
        """Verify bottom edge pin matches KiCAD reference format."""
        sheets = reference_schematic._data.get("sheets", [])
        sheet = sheets[0]
        pins = sheet.get("pins", [])

        # Find PIN_BOTTOM
        bottom_pin = [p for p in pins if p["name"] == "PIN_BOTTOM"][0]

        # Verify all attributes match KiCAD format
        assert bottom_pin["pin_type"] == "output"
        assert bottom_pin["position"]["x"] == 127  # Position along edge
        assert bottom_pin["position"]["y"] == 140  # Bottom edge
        assert bottom_pin["rotation"] == 270  # Faces down
        assert bottom_pin["justify"] == "left"
        assert bottom_pin["size"] == 1.27

    def test_left_edge_pin_matches_reference(self, reference_schematic):
        """Verify left edge pin matches KiCAD reference format."""
        sheets = reference_schematic._data.get("sheets", [])
        sheet = sheets[0]
        pins = sheet.get("pins", [])

        # Find PIN_LEFT
        left_pin = [p for p in pins if p["name"] == "PIN_LEFT"][0]

        # Verify all attributes match KiCAD format
        assert left_pin["pin_type"] == "input"
        assert left_pin["position"]["x"] == 100  # Left edge
        assert left_pin["position"]["y"] == 118.11  # Position along edge
        assert left_pin["rotation"] == 180  # Faces left
        assert left_pin["justify"] == "left"
        assert left_pin["size"] == 1.27

    def test_top_edge_pin_matches_reference(self, reference_schematic):
        """Verify top edge pin matches KiCAD reference format."""
        sheets = reference_schematic._data.get("sheets", [])
        sheet = sheets[0]
        pins = sheet.get("pins", [])

        # Find PIN_TOP
        top_pin = [p for p in pins if p["name"] == "PIN_TOP"][0]

        # Verify all attributes match KiCAD format
        assert top_pin["pin_type"] == "output"
        assert top_pin["position"]["x"] == 127  # Position along edge
        assert top_pin["position"]["y"] == 100  # Top edge
        assert top_pin["rotation"] == 90  # Faces up
        assert top_pin["justify"] == "right"
        assert top_pin["size"] == 1.27

    def test_programmatic_generation_matches_reference(self, reference_schematic, tmp_path):
        """Test that programmatically generated sheet pins match reference."""
        # Create new schematic with same sheet setup
        sch = ksa.create_schematic("Sheet Pin Edges Test")
        sheet_uuid = sch.add_sheet(
            name="SubSheet",
            filename="subsheet.kicad_sch",
            position=(100, 100),
            size=(50, 40),
        )

        # Add pins using edge-based API (matching reference positions)
        # RIGHT: position_along_edge = 118.11 - 100 = 18.11
        sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_RIGHT",
            pin_type="input",
            edge="right",
            position_along_edge=18.11,
        )

        # BOTTOM: position_along_edge = 127 - 100 = 27
        sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_BOTTOM",
            pin_type="output",
            edge="bottom",
            position_along_edge=27,
        )

        # LEFT: position_along_edge = 140 - 118.11 = 21.89
        sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_LEFT",
            pin_type="input",
            edge="left",
            position_along_edge=21.89,
        )

        # TOP: position_along_edge = 127 - 100 = 27
        sch.add_sheet_pin(
            sheet_uuid=sheet_uuid,
            name="PIN_TOP",
            pin_type="output",
            edge="top",
            position_along_edge=27,
        )

        # Get generated sheet
        generated_sheets = sch._data.get("sheets", [])
        generated_sheet = generated_sheets[0]
        generated_pins = generated_sheet.get("pins", [])

        # Get reference sheet
        reference_sheets = reference_schematic._data.get("sheets", [])
        reference_sheet = reference_sheets[0]
        reference_pins = reference_sheet.get("pins", [])

        # Compare pin count
        assert len(generated_pins) == len(reference_pins) == 4

        # Compare each pin
        for ref_pin in reference_pins:
            pin_name = ref_pin["name"]
            gen_pin = [p for p in generated_pins if p["name"] == pin_name][0]

            # Compare all attributes
            assert gen_pin["pin_type"] == ref_pin["pin_type"], f"{pin_name}: type mismatch"
            assert gen_pin["position"]["x"] == pytest.approx(
                ref_pin["position"]["x"], abs=0.01
            ), f"{pin_name}: X position mismatch"
            assert gen_pin["position"]["y"] == pytest.approx(
                ref_pin["position"]["y"], abs=0.01
            ), f"{pin_name}: Y position mismatch"
            assert gen_pin["rotation"] == ref_pin["rotation"], f"{pin_name}: rotation mismatch"
            assert gen_pin["justify"] == ref_pin["justify"], f"{pin_name}: justify mismatch"
            assert gen_pin["size"] == ref_pin["size"], f"{pin_name}: size mismatch"

    def test_edge_calculation_from_reference(self, reference_schematic):
        """Verify our edge calculation logic matches reference positions."""
        sheets = reference_schematic._data.get("sheets", [])
        sheet = sheets[0]

        sheet_x = sheet["position"]["x"]  # 100
        sheet_y = sheet["position"]["y"]  # 100
        sheet_width = sheet["size"]["width"]  # 50
        sheet_height = sheet["size"]["height"]  # 40

        pins = sheet.get("pins", [])

        # Test RIGHT edge calculation
        right_pin = [p for p in pins if p["name"] == "PIN_RIGHT"][0]
        # position_along_edge = y - sheet_y = 118.11 - 100 = 18.11
        expected_x = sheet_x + sheet_width  # 150
        expected_y = sheet_y + 18.11  # 118.11
        assert right_pin["position"]["x"] == expected_x
        assert right_pin["position"]["y"] == pytest.approx(expected_y, abs=0.01)

        # Test BOTTOM edge calculation
        bottom_pin = [p for p in pins if p["name"] == "PIN_BOTTOM"][0]
        # position_along_edge = x - sheet_x = 127 - 100 = 27
        expected_x = sheet_x + 27  # 127
        expected_y = sheet_y + sheet_height  # 140
        assert bottom_pin["position"]["x"] == expected_x
        assert bottom_pin["position"]["y"] == expected_y

        # Test LEFT edge calculation
        left_pin = [p for p in pins if p["name"] == "PIN_LEFT"][0]
        # position_along_edge = (sheet_y + sheet_height) - y = 140 - 118.11 = 21.89
        expected_x = sheet_x  # 100
        expected_y = sheet_y + sheet_height - 21.89  # 118.11
        assert left_pin["position"]["x"] == expected_x
        assert left_pin["position"]["y"] == pytest.approx(expected_y, abs=0.01)

        # Test TOP edge calculation
        top_pin = [p for p in pins if p["name"] == "PIN_TOP"][0]
        # position_along_edge = x - sheet_x = 127 - 100 = 27
        expected_x = sheet_x + 27  # 127
        expected_y = sheet_y  # 100
        assert top_pin["position"]["x"] == expected_x
        assert top_pin["position"]["y"] == expected_y


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
