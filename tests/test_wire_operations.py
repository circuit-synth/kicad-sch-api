#!/usr/bin/env python3
"""
Comprehensive Wire Operations Test Suite

Tests wire functionality including:
- Creation and parsing
- Position modification
- Round-trip preservation
- Multiple wire segments
"""

import sys
import tempfile
import uuid
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kicad_sch_api.core.parser import SExpressionParser


class TestWireOperations:
    """Test suite for wire creation, reading, modification, and preservation."""

    def test_create_single_wire(self):
        """Test creating a single wire segment."""
        parser = SExpressionParser()

        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [
                {
                    "points": [{"x": 50, "y": 50}, {"x": 100, "y": 50}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "uuid": str(uuid.uuid4()),
                }
            ],
            "sheet_instances": [{"path": "/", "page": "1"}],
            "embedded_fonts": "no",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Write schematic
            parser.write_file(schematic_data, temp_file)

            # Read it back
            read_data = parser.parse_file(temp_file)

            # Verify wire was preserved
            assert "wires" in read_data, "Wires field missing in parsed data"
            assert len(read_data["wires"]) == 1, f"Expected 1 wire, got {len(read_data['wires'])}"

            wire = read_data["wires"][0]
            assert len(wire["points"]) == 2, "Wire should have 2 points"
            assert wire["points"][0]["x"] == 50
            assert wire["points"][0]["y"] == 50
            assert wire["points"][1]["x"] == 100
            assert wire["points"][1]["y"] == 50

        finally:
            temp_file.unlink()

    def test_create_multiple_wires(self):
        """Test creating multiple connected wire segments."""
        parser = SExpressionParser()

        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [
                {
                    "points": [{"x": 50, "y": 50}, {"x": 100, "y": 50}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "uuid": str(uuid.uuid4()),
                },
                {
                    "points": [{"x": 100, "y": 50}, {"x": 100, "y": 100}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "uuid": str(uuid.uuid4()),
                },
                {
                    "points": [{"x": 100, "y": 100}, {"x": 150, "y": 100}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "uuid": str(uuid.uuid4()),
                },
            ],
            "sheet_instances": [{"path": "/", "page": "1"}],
            "embedded_fonts": "no",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Write schematic
            parser.write_file(schematic_data, temp_file)

            # Read it back
            read_data = parser.parse_file(temp_file)

            # Verify all wires were preserved
            assert "wires" in read_data
            assert len(read_data["wires"]) == 3, f"Expected 3 wires, got {len(read_data['wires'])}"

            # Verify wire 1 (horizontal)
            assert read_data["wires"][0]["points"][0]["x"] == 50
            assert read_data["wires"][0]["points"][0]["y"] == 50
            assert read_data["wires"][0]["points"][1]["x"] == 100
            assert read_data["wires"][0]["points"][1]["y"] == 50

            # Verify wire 2 (vertical)
            assert read_data["wires"][1]["points"][0]["x"] == 100
            assert read_data["wires"][1]["points"][0]["y"] == 50
            assert read_data["wires"][1]["points"][1]["x"] == 100
            assert read_data["wires"][1]["points"][1]["y"] == 100

            # Verify wire 3 (horizontal)
            assert read_data["wires"][2]["points"][0]["x"] == 100
            assert read_data["wires"][2]["points"][0]["y"] == 100
            assert read_data["wires"][2]["points"][1]["x"] == 150
            assert read_data["wires"][2]["points"][1]["y"] == 100

        finally:
            temp_file.unlink()

    def test_modify_wire_positions(self):
        """Test modifying wire positions (round-trip with modification)."""
        parser = SExpressionParser()

        # Create initial schematic
        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [
                {
                    "points": [{"x": 50, "y": 50}, {"x": 100, "y": 50}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "uuid": str(uuid.uuid4()),
                }
            ],
            "sheet_instances": [{"path": "/", "page": "1"}],
            "embedded_fonts": "no",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Write initial schematic
            parser.write_file(schematic_data, temp_file)

            # Read it back
            read_data = parser.parse_file(temp_file)

            # Modify wire position (move +50 in X, +30 in Y)
            read_data["wires"][0]["points"][0]["x"] = 100
            read_data["wires"][0]["points"][0]["y"] = 80
            read_data["wires"][0]["points"][1]["x"] = 150
            read_data["wires"][0]["points"][1]["y"] = 80

            # Write modified schematic
            parser.write_file(read_data, temp_file)

            # Read again to verify modification persisted
            final_data = parser.parse_file(temp_file)

            # Verify modified positions
            assert final_data["wires"][0]["points"][0]["x"] == 100
            assert final_data["wires"][0]["points"][0]["y"] == 80
            assert final_data["wires"][0]["points"][1]["x"] == 150
            assert final_data["wires"][0]["points"][1]["y"] == 80

        finally:
            temp_file.unlink()

    def test_wire_uuid_preservation(self):
        """Test that wire UUIDs are preserved during round-trip."""
        parser = SExpressionParser()

        wire_uuid = str(uuid.uuid4())

        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [
                {
                    "points": [{"x": 50, "y": 50}, {"x": 100, "y": 50}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "uuid": wire_uuid,
                }
            ],
            "sheet_instances": [{"path": "/", "page": "1"}],
            "embedded_fonts": "no",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Write schematic
            parser.write_file(schematic_data, temp_file)

            # Read it back
            read_data = parser.parse_file(temp_file)

            # Verify UUID is preserved
            assert "uuid" in read_data["wires"][0], "Wire UUID not preserved"
            assert (
                read_data["wires"][0]["uuid"] == wire_uuid
            ), f"Wire UUID changed: {read_data['wires'][0]['uuid']} != {wire_uuid}"

        finally:
            temp_file.unlink()

    def test_wire_stroke_properties(self):
        """Test that wire stroke properties are preserved."""
        parser = SExpressionParser()

        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [
                {
                    "points": [{"x": 50, "y": 50}, {"x": 100, "y": 50}],
                    "stroke_width": 0.5,
                    "stroke_type": "dash",
                    "uuid": str(uuid.uuid4()),
                }
            ],
            "sheet_instances": [{"path": "/", "page": "1"}],
            "embedded_fonts": "no",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Write schematic
            parser.write_file(schematic_data, temp_file)

            # Read it back
            read_data = parser.parse_file(temp_file)

            # Verify stroke properties
            wire = read_data["wires"][0]
            assert (
                wire["stroke_width"] == 0.5
            ), f"Stroke width not preserved: {wire['stroke_width']}"
            assert (
                wire["stroke_type"] == "dash"
            ), f"Stroke type not preserved: {wire['stroke_type']}"

        finally:
            temp_file.unlink()

    def test_empty_wires_list(self):
        """Test schematic with no wires."""
        parser = SExpressionParser()

        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [],
            "sheet_instances": [{"path": "/", "page": "1"}],
            "embedded_fonts": "no",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Write schematic
            parser.write_file(schematic_data, temp_file)

            # Read it back
            read_data = parser.parse_file(temp_file)

            # Verify wires list exists but is empty
            assert "wires" in read_data, "Wires field missing"
            assert len(read_data["wires"]) == 0, "Expected empty wires list"

        finally:
            temp_file.unlink()

    def test_wire_with_decimal_coordinates(self):
        """Test wires with decimal/floating-point coordinates."""
        parser = SExpressionParser()

        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [
                {
                    "points": [{"x": 50.5, "y": 50.25}, {"x": 100.75, "y": 50.125}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "uuid": str(uuid.uuid4()),
                }
            ],
            "sheet_instances": [{"path": "/", "page": "1"}],
            "embedded_fonts": "no",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_file = Path(f.name)

        try:
            # Write schematic
            parser.write_file(schematic_data, temp_file)

            # Read it back
            read_data = parser.parse_file(temp_file)

            # Verify decimal coordinates are preserved
            wire = read_data["wires"][0]
            assert abs(wire["points"][0]["x"] - 50.5) < 0.001
            assert abs(wire["points"][0]["y"] - 50.25) < 0.001
            assert abs(wire["points"][1]["x"] - 100.75) < 0.001
            assert abs(wire["points"][1]["y"] - 50.125) < 0.001

        finally:
            temp_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
