"""
Test rectangle functionality in kicad-sch-api.
"""

import pytest

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point


def test_add_rectangle():
    """Test adding a rectangle to a schematic."""
    # Create a new schematic
    sch = Schematic()

    # Add a rectangle
    rect_uuid = sch.add_rectangle(
        start=(10.0, 20.0),
        end=(50.0, 60.0),
        stroke_width=0.127,
        stroke_type="solid",
        fill_type="none",
    )

    # Verify UUID was returned
    assert rect_uuid is not None
    assert isinstance(rect_uuid, str)

    # Verify rectangle was added to internal data
    assert "rectangles" in sch._data
    assert len(sch._data["rectangles"]) == 1

    # Verify rectangle properties
    rect = sch._data["rectangles"][0]
    assert rect["uuid"] == rect_uuid
    assert rect["start"]["x"] == 10.0
    assert rect["start"]["y"] == 20.0
    assert rect["end"]["x"] == 50.0
    assert rect["end"]["y"] == 60.0
    assert rect["stroke_width"] == 0.127
    assert rect["stroke_type"] == "solid"
    assert rect["fill_type"] == "none"


def test_add_rectangle_with_point_objects():
    """Test adding rectangle using Point objects."""
    sch = Schematic()

    start = Point(100.0, 200.0)
    end = Point(150.0, 250.0)

    rect_uuid = sch.add_rectangle(start=start, end=end, stroke_width=0.254)

    assert rect_uuid is not None
    rect = sch._data["rectangles"][0]
    assert rect["start"]["x"] == 100.0
    assert rect["start"]["y"] == 200.0


def test_add_multiple_rectangles():
    """Test adding multiple rectangle."""
    sch = Schematic()

    rect1_uuid = sch.add_rectangle((0, 0), (10, 10))
    rect2_uuid = sch.add_rectangle((20, 20), (30, 30))
    rect3_uuid = sch.add_rectangle((40, 40), (50, 50))

    assert len(sch._data["rectangles"]) == 3
    assert rect1_uuid != rect2_uuid != rect3_uuid


def test_rectangle_default_values():
    """Test rectangle default parameter values."""
    sch = Schematic()

    rect_uuid = sch.add_rectangle((0, 0), (10, 10))

    rect = sch._data["rectangles"][0]
    assert rect["stroke_width"] == 0.127  # Our default value
    assert rect["stroke_type"] == "solid"  # Our default value
    assert rect["fill_type"] == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
