"""
Test parsing rectangles from the reference RP2040 schematic.
"""

import pytest

from kicad_sch_api import load_schematic

REFERENCE_SCHEMATIC = "/Users/shanemattner/Desktop/circuit-synth-examples/pcbs/rp2040-minimal/RP2040_Minimal/RP2040_Minimal.kicad_sch"


def test_parse_reference_schematic_rectangles():
    """Test that we can parse rectangles from the reference schematic."""
    try:
        sch = load_schematic(REFERENCE_SCHEMATIC)

        # The reference schematic may or may not have rectangles
        assert "rectangles" in sch._data
        rectangles = sch._data["rectangles"]

        # If the reference schematic doesn't have rectangles, skip the test
        if len(rectangles) == 0:
            pytest.skip(f"Reference schematic has no rectangles: {REFERENCE_SCHEMATIC}")

        # Verify rectangle structure if rectangles exist
        rect = rectangles[0]
        assert "start" in rect
        assert "end" in rect
        assert "x" in rect["start"]
        assert "y" in rect["start"]
        assert "x" in rect["end"]
        assert "y" in rect["end"]
        assert "uuid" in rect

        # Verify stroke and fill
        assert "stroke_width" in rect
        assert "stroke_type" in rect
        assert "fill_type" in rect

        print(f"Successfully parsed {len(rectangles)} rectangles from reference schematic")
        print(
            f"First rectangle: start=({rect['start']['x']}, {rect['start']['y']}), "
            f"end=({rect['end']['x']}, {rect['end']['y']})"
        )

    except FileNotFoundError:
        pytest.skip(f"Reference schematic not found: {REFERENCE_SCHEMATIC}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
