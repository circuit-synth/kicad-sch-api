#!/usr/bin/env python3
"""
Reference tests for junction using manually created KiCad schematics.

These tests verify that our junction handling matches real KiCad format
from manually created schematics with junctions at wire intersections.
"""

import pytest

import kicad_sch_api as ksa


class TestJunctionReference:
    """Test junction against reference KiCad schematics."""

    def test_junction_structure(self):
        """Test junction structure against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/junction/junction.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Verify junctions exist
        assert "junctions" in sch._data, "Schematic should have junctions key"
        junctions = sch._data["junctions"]
        assert isinstance(junctions, list), "Junctions should be a list"
        assert len(junctions) > 0, "Schematic should have at least one junction"

        # Verify structure of each junction
        for i, junction in enumerate(junctions):
            assert "position" in junction, f"Junction {i} should have 'position' field"
            assert "uuid" in junction, f"Junction {i} should have 'uuid' field"

            # Verify position has x and y
            position = junction["position"]
            assert "x" in position, f"Junction {i} position should have 'x'"
            assert "y" in position, f"Junction {i} position should have 'y'"

            # Verify position values are numeric
            assert isinstance(position["x"], (int, float)), f"Junction {i} x should be numeric"
            assert isinstance(position["y"], (int, float)), f"Junction {i} y should be numeric"

    def test_junction_with_wires(self):
        """Verify junction schematic contains both junction and wires."""
        sch_path = "tests/reference_kicad_projects/junction/junction.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        # Get junction position
        junctions = sch._data.get("junctions", [])
        assert len(junctions) > 0, "Should have at least one junction"

        # Get wires
        wires = sch._data.get("wires", [])
        assert len(wires) >= 2, "Should have at least 2 wires for junction test"

        # Verify junction is at expected position
        junction = junctions[0]
        assert junction["position"]["x"] == 100.0
        assert junction["position"]["y"] == 100.0

        # Verify we have wires (junctions only make sense with wires)
        assert len(wires) == 2, "Junction reference should have exactly 2 wires"

    def test_junction_loading(self):
        """Verify junctions can be loaded successfully."""
        sch_path = "tests/reference_kicad_projects/junction/junction.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        assert sch is not None, "Schematic should load successfully"
        assert "junctions" in sch._data, "Schematic should have junctions"

        junctions = sch._data["junctions"]
        assert len(junctions) > 0, "Should have at least one junction"

        # Verify first junction has expected position (from our reference)
        first_junction = junctions[0]
        assert first_junction["position"]["x"] == 100.0
        assert first_junction["position"]["y"] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
