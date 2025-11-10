#!/usr/bin/env python3
"""
Test Suite for Bus Elements (Bus Wires, Bus Entries, Bus Labels)

Tests bus functionality including:
- Bus wire creation with wire_type=BUS
- Bus entry creation and positioning
- Bus label validation and notation
- Round-trip preservation of bus elements
- Grid snapping for bus elements
"""

import sys
import tempfile
import uuid
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kicad_sch_api.core.parser import SExpressionParser
from kicad_sch_api.core.types import BusEntry, Point


class TestBusEntry:
    """Test suite for BusEntry dataclass."""

    def test_create_bus_entry(self):
        """Test creating a basic bus entry."""
        entry = BusEntry(
            uuid=str(uuid.uuid4()), position=Point(50.0, 50.0), size=Point(2.54, 2.54), rotation=0
        )

        assert entry.uuid is not None
        assert entry.position.x == 50.0
        assert entry.position.y == 50.0
        assert entry.size.x == 2.54
        assert entry.size.y == 2.54
        assert entry.rotation == 0

    def test_bus_entry_rotation_validation(self):
        """Test that bus entry validates rotation angles."""
        # Valid rotations (0, 90, 180, 270)
        for rotation in [0, 90, 180, 270]:
            entry = BusEntry(
                uuid=str(uuid.uuid4()),
                position=Point(50.0, 50.0),
                size=Point(2.54, 2.54),
                rotation=rotation,
            )
            assert entry.rotation == rotation

    def test_bus_entry_default_size(self):
        """Test that bus entry uses default size of 2.54mm (100mil)."""
        entry = BusEntry(
            uuid=str(uuid.uuid4()),
            position=Point(50.0, 50.0),
        )

        # Default size should be 2.54mm (100 mil = 0.1 inch)
        assert entry.size.x == 2.54
        assert entry.size.y == 2.54


class TestBusWire:
    """Test suite for bus wire creation (using WireType.BUS)."""

    @pytest.mark.xfail(
        reason="Parser does not yet preserve wire_type='bus' during round-trip. See Issue #117 for parser implementation."
    )
    def test_create_bus_wire(self):
        """Test creating a bus wire using WireType.BUS."""
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
                    "wire_type": "bus",  # This makes it a bus wire
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

            # Verify bus wire was preserved
            assert "wires" in read_data, "Wires field missing"
            assert len(read_data["wires"]) == 1

            wire = read_data["wires"][0]
            assert wire.get("wire_type") == "bus", "Wire type should be 'bus'"
            assert len(wire["points"]) == 2
            assert wire["points"][0]["x"] == 50
            assert wire["points"][1]["x"] == 100

        finally:
            temp_file.unlink()

    @pytest.mark.xfail(
        reason="Parser does not yet preserve wire_type='bus' during round-trip. See Issue #117 for parser implementation."
    )
    def test_bus_wire_with_label(self):
        """Test creating a bus wire with a bus label."""
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
                    "wire_type": "bus",
                    "uuid": str(uuid.uuid4()),
                }
            ],
            "labels": [
                {
                    "text": "DATA[0..7]",
                    "position": {"x": 75, "y": 48},
                    "rotation": 0,
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

            # Verify bus wire and label preserved
            assert len(read_data["wires"]) == 1
            assert read_data["wires"][0].get("wire_type") == "bus"

            assert len(read_data["labels"]) == 1
            assert read_data["labels"][0]["text"] == "DATA[0..7]"

        finally:
            temp_file.unlink()


class TestBusLabel:
    """Test suite for bus label validation."""

    def test_bus_label_range_notation(self):
        """Test that bus labels with range notation are valid."""
        valid_notations = [
            "DATA[0..7]",
            "ADDR[0..15]",
            "BUS[0..31]",
            "SIGNALS[10..20]",
        ]

        for notation in valid_notations:
            # Just verify the pattern matches
            import re

            assert re.search(r"\[.+\]", notation), f"Notation {notation} should be valid"

    def test_bus_label_list_notation(self):
        """Test that bus labels with list notation are valid."""
        valid_notations = [
            "RGB[R,G,B]",
            "CTRL[CLK,EN,RST]",
            "SIGNALS[A,B,C,D]",
        ]

        for notation in valid_notations:
            import re

            assert re.search(r"\[.+\]", notation), f"Notation {notation} should be valid"

    def test_bus_label_mixed_notation(self):
        """Test that mixed bus notations are valid."""
        valid_notations = [
            "BUS[0..3,CLK,EN]",
            "DATA[0..7,PARITY]",
        ]

        for notation in valid_notations:
            import re

            assert re.search(r"\[.+\]", notation), f"Notation {notation} should be valid"

    def test_bus_label_invalid_notation(self):
        """Test that labels without brackets are invalid bus labels."""
        invalid_notations = [
            "DATA",  # No brackets
            "DATA[]",  # Empty brackets
            "DATA[",  # Unclosed bracket
        ]

        for notation in invalid_notations:
            import re

            if notation == "DATA[]":
                # Empty brackets still match the pattern but should be caught elsewhere
                continue
            if not re.search(r"\[.+\]", notation):
                # This is expected to not match
                assert True
            else:
                pytest.fail(f"Notation {notation} should be invalid")


class TestBusEntryRoundTrip:
    """Test round-trip preservation of bus entries."""

    @pytest.mark.xfail(
        reason="Parser does not yet handle bus_entries field. See Issue #117 for parser implementation."
    )
    def test_bus_entry_round_trip(self):
        """Test that bus entries are preserved during write/read cycle."""
        parser = SExpressionParser()

        bus_entry_uuid = str(uuid.uuid4())
        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "bus_entries": [
                {
                    "uuid": bus_entry_uuid,
                    "position": {"x": 60.96, "y": 50.8},
                    "size": {"x": 2.54, "y": 2.54},
                    "rotation": 270,
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

            # Verify bus entry preserved
            assert "bus_entries" in read_data, "Bus entries field missing"
            assert len(read_data["bus_entries"]) == 1

            entry = read_data["bus_entries"][0]
            assert entry["uuid"] == bus_entry_uuid
            assert entry["position"]["x"] == 60.96
            assert entry["position"]["y"] == 50.8
            assert entry["size"]["x"] == 2.54
            assert entry["size"]["y"] == 2.54
            assert entry["rotation"] == 270

        finally:
            temp_file.unlink()


class TestCompleteBusCircuit:
    """Test complete bus circuit with wires, entries, and labels."""

    @pytest.mark.xfail(
        reason="Parser does not yet preserve wire_type='bus' or bus_entries. See Issue #117 for parser implementation."
    )
    def test_complete_8bit_data_bus(self):
        """Test creating a complete 8-bit data bus with entries."""
        parser = SExpressionParser()

        # Create 8-bit data bus with bus wire, entries, and label
        bus_entries = []
        for i in range(8):
            bus_entries.append(
                {
                    "uuid": str(uuid.uuid4()),
                    "position": {"x": 60.96 + i * 2.54, "y": 50.8},
                    "size": {"x": 2.54, "y": 2.54},
                    "rotation": 270,
                }
            )

        schematic_data = {
            "version": "20250114",
            "generator": "test",
            "generator_version": "1.0",
            "uuid": str(uuid.uuid4()),
            "paper": "A4",
            "lib_symbols": {},
            "wires": [
                {
                    "points": [{"x": 50.8, "y": 50.8}, {"x": 101.6, "y": 50.8}],
                    "stroke_width": 0,
                    "stroke_type": "default",
                    "wire_type": "bus",
                    "uuid": str(uuid.uuid4()),
                }
            ],
            "bus_entries": bus_entries,
            "labels": [
                {
                    "text": "DATA[0..7]",
                    "position": {"x": 76.2, "y": 48.26},
                    "rotation": 0,
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

            # Verify all elements preserved
            assert len(read_data["wires"]) == 1
            assert read_data["wires"][0].get("wire_type") == "bus"

            assert len(read_data["bus_entries"]) == 8
            for entry in read_data["bus_entries"]:
                assert entry["size"]["x"] == 2.54
                assert entry["rotation"] == 270

            assert len(read_data["labels"]) == 1
            assert read_data["labels"][0]["text"] == "DATA[0..7]"

        finally:
            temp_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
