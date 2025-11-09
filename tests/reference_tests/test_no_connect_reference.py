#!/usr/bin/env python3
"""
Reference tests for no-connect marker using manually created KiCad schematics.

These tests verify that our no-connect marker handling matches real KiCad format
from manually created schematics with no-connect markers.
"""

import pytest

import kicad_sch_api as ksa


class TestNoConnectReference:
    """Test no-connect marker against reference KiCad schematics."""

    def test_no_connect_structure(self):
        """Test no-connect structure against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/no_connect/no_connect.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Verify no_connects exist
        assert "no_connects" in sch._data, "Schematic should have no_connects key"
        no_connects = sch._data["no_connects"]
        assert isinstance(no_connects, list), "No-connects should be a list"
        assert len(no_connects) > 0, "Schematic should have at least one no-connect"

        # Verify structure of each no-connect
        for i, no_connect in enumerate(no_connects):
            assert "position" in no_connect, f"No-connect {i} should have 'position' field"
            assert "uuid" in no_connect, f"No-connect {i} should have 'uuid' field"

            # Verify position has x and y
            position = no_connect["position"]
            assert "x" in position, f"No-connect {i} position should have 'x'"
            assert "y" in position, f"No-connect {i} position should have 'y'"

            # Verify position values are numeric
            assert isinstance(position["x"], (int, float)), f"No-connect {i} x should be numeric"
            assert isinstance(position["y"], (int, float)), f"No-connect {i} y should be numeric"

    def test_no_connect_loading(self):
        """Verify no-connects can be loaded successfully."""
        sch_path = "tests/reference_kicad_projects/no_connect/no_connect.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        assert sch is not None, "Schematic should load successfully"
        assert "no_connects" in sch._data, "Schematic should have no_connects"

        no_connects = sch._data["no_connects"]
        assert len(no_connects) > 0, "Should have at least one no-connect"

        # Verify first no-connect has expected position (from our reference)
        first_no_connect = no_connects[0]
        assert first_no_connect["position"]["x"] == 100.0
        assert first_no_connect["position"]["y"] == 100.0

    def test_no_connect_minimal_structure(self):
        """Verify no-connects have minimal required structure."""
        sch_path = "tests/reference_kicad_projects/no_connect/no_connect.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        no_connects = sch._data.get("no_connects", [])
        assert len(no_connects) > 0, "Should have at least one no-connect"

        # No-connects are simple markers with just position and UUID
        for no_connect in no_connects:
            # Should have exactly these fields (plus UUID)
            assert "position" in no_connect
            assert "uuid" in no_connect

            # Position should be a simple x, y coordinate
            position = no_connect["position"]
            assert len(position) == 2, "Position should have exactly x and y"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
