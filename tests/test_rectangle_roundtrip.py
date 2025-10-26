"""
Test rectangle round-trip: create, save, load, verify.
"""

import os
import tempfile

import pytest

from kicad_sch_api import create_schematic, load_schematic


def test_rectangle_roundtrip():
    """Test creating, saving, and loading a schematic with rectangles."""
    # Create a schematic with rectangles
    sch = create_schematic("Rectangle Test")

    # Add multiple rectangles
    rect1_uuid = sch.add_rectangle(
        start=(10.0, 20.0),
        end=(50.0, 60.0),
        stroke_width=0.127,
        stroke_type="solid",
        fill_type="none",
    )

    rect2_uuid = sch.add_rectangle(
        start=(100.0, 100.0),
        end=(200.0, 150.0),
        stroke_width=0.254,
        stroke_type="default",
        fill_type="none",
    )

    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False, mode="w") as f:
        temp_path = f.name

    try:
        sch.save(temp_path)

        # Load the schematic back
        sch_loaded = load_schematic(temp_path)

        # Verify rectangles were preserved
        assert "rectangles" in sch_loaded._data
        assert len(sch_loaded._data["rectangles"]) == 2

        # Verify first rectangle
        rect1 = sch_loaded._data["rectangles"][0]
        assert rect1["uuid"] == rect1_uuid
        assert rect1["start"]["x"] == 10.0
        assert rect1["start"]["y"] == 20.0
        assert rect1["end"]["x"] == 50.0
        assert rect1["end"]["y"] == 60.0
        assert rect1["stroke_width"] == 0.127
        assert rect1["stroke_type"] == "solid"

        # Verify second rectangle
        rect2 = sch_loaded._data["rectangles"][1]
        assert rect2["uuid"] == rect2_uuid
        assert rect2["start"]["x"] == 100.0
        assert rect2["start"]["y"] == 100.0
        assert rect2["stroke_width"] == 0.254

    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_rectangle_format_preservation():
    """Test that rectangle S-expression format matches KiCAD."""
    sch = create_schematic("Format Test")

    # Add rectangle with specific parameters
    sch.add_rectangle(
        start=(91.821, 32.211),
        end=(155.829, 148.049),
        stroke_width=0.127,
        stroke_type="solid",
        fill_type="none",
    )

    # Save to string
    with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False, mode="w") as f:
        temp_path = f.name

    try:
        sch.save(temp_path)

        # Read file content
        with open(temp_path, "r") as f:
            content = f.read()

        # Verify S-expression structure
        assert "(rectangle" in content
        assert "(start 91.821 32.211)" in content
        assert "(end 155.829 148.049)" in content
        assert "(stroke" in content
        assert "(width 0.127)" in content
        assert "(type solid)" in content
        assert "(fill" in content
        assert "(type none)" in content
        assert "(uuid" in content

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
