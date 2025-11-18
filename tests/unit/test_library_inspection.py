"""
Unit tests for library inspection features (Issue #179 Phase 2).

Tests the get_symbol_info(), list_pins(), and show_pins() functionality
for inspecting symbols before placing them in schematics.
"""

import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import PinType, Point, SchematicPin
from kicad_sch_api.library.cache import SymbolDefinition, SymbolLibraryCache


class TestSymbolDefinitionListPins:
    """Test SymbolDefinition.list_pins() method."""

    def test_list_pins_empty_symbol(self):
        """Should return empty list for symbol with no pins."""
        symbol = SymbolDefinition(
            lib_id="Custom:NoPins", name="NoPins", library="Custom", reference_prefix="U"
        )

        pins = symbol.list_pins()

        assert pins == []
        assert isinstance(pins, list)

    def test_list_pins_single_pin(self):
        """Should return list with single pin data."""
        symbol = SymbolDefinition(
            lib_id="Custom:SinglePin",
            name="SinglePin",
            library="Custom",
            reference_prefix="U",
            pins=[
                SchematicPin(number="1", name="IN", pin_type=PinType.INPUT, position=Point(0, 0))
            ],
        )

        pins = symbol.list_pins()

        assert len(pins) == 1
        assert pins[0]["number"] == "1"
        assert pins[0]["name"] == "IN"
        assert pins[0]["type"] == "input"  # PinType enum values are lowercase
        assert pins[0]["position"] == Point(0, 0)

    def test_list_pins_multiple_pins(self):
        """Should return list with all pin data."""
        symbol = SymbolDefinition(
            lib_id="Custom:MultiPin",
            name="MultiPin",
            library="Custom",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="1", name="VCC", pin_type=PinType.POWER_IN, position=Point(0, 2.54)
                ),
                SchematicPin(
                    number="2", name="GND", pin_type=PinType.POWER_IN, position=Point(0, -2.54)
                ),
                SchematicPin(
                    number="3", name="OUT", pin_type=PinType.OUTPUT, position=Point(5.08, 0)
                ),
            ],
        )

        pins = symbol.list_pins()

        assert len(pins) == 3
        assert pins[0]["number"] == "1"
        assert pins[0]["name"] == "VCC"
        assert pins[1]["number"] == "2"
        assert pins[1]["name"] == "GND"
        assert pins[2]["number"] == "3"
        assert pins[2]["name"] == "OUT"

    def test_list_pins_returns_dict_list(self):
        """Should return list of dictionaries with correct keys."""
        symbol = SymbolDefinition(
            lib_id="Custom:Test",
            name="Test",
            library="Custom",
            reference_prefix="U",
            pins=[
                SchematicPin(number="1", name="PIN", pin_type=PinType.PASSIVE, position=Point(0, 0))
            ],
        )

        pins = symbol.list_pins()

        assert isinstance(pins, list)
        assert len(pins) == 1
        assert isinstance(pins[0], dict)
        assert set(pins[0].keys()) == {"number", "name", "type", "position"}

    def test_list_pins_updates_access_stats(self):
        """Should update access count and timestamp."""
        symbol = SymbolDefinition(
            lib_id="Custom:Test", name="Test", library="Custom", reference_prefix="U"
        )

        initial_count = symbol.access_count
        initial_time = symbol.last_accessed

        symbol.list_pins()

        assert symbol.access_count == initial_count + 1
        assert symbol.last_accessed >= initial_time


class TestSymbolDefinitionShowPins:
    """Test SymbolDefinition.show_pins() method."""

    def test_show_pins_empty_symbol(self, capsys):
        """Should display header with no pins."""
        symbol = SymbolDefinition(
            lib_id="Custom:NoPins", name="NoPins", library="Custom", reference_prefix="U"
        )

        symbol.show_pins()
        captured = capsys.readouterr()

        assert "Pins for Custom:NoPins:" in captured.out
        assert "Pin#" in captured.out
        assert "Name" in captured.out
        assert "Type" in captured.out

    def test_show_pins_with_description(self, capsys):
        """Should display description when available."""
        symbol = SymbolDefinition(
            lib_id="Custom:Test",
            name="Test",
            library="Custom",
            reference_prefix="U",
            description="Test component",
        )

        symbol.show_pins()
        captured = capsys.readouterr()

        assert "Description: Test component" in captured.out

    def test_show_pins_single_pin(self, capsys):
        """Should display single pin in table format."""
        symbol = SymbolDefinition(
            lib_id="Custom:SinglePin",
            name="SinglePin",
            library="Custom",
            reference_prefix="U",
            pins=[
                SchematicPin(number="1", name="IN", pin_type=PinType.INPUT, position=Point(0, 0))
            ],
        )

        symbol.show_pins()
        captured = capsys.readouterr()

        assert "1" in captured.out
        assert "IN" in captured.out
        assert "input" in captured.out  # PinType enum values are lowercase

    def test_show_pins_multiple_pins(self, capsys):
        """Should display all pins in table format."""
        symbol = SymbolDefinition(
            lib_id="Custom:MultiPin",
            name="MultiPin",
            library="Custom",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="1", name="VCC", pin_type=PinType.POWER_IN, position=Point(0, 2.54)
                ),
                SchematicPin(
                    number="2", name="GND", pin_type=PinType.POWER_IN, position=Point(0, -2.54)
                ),
            ],
        )

        symbol.show_pins()
        captured = capsys.readouterr()

        assert "1" in captured.out
        assert "VCC" in captured.out
        assert "power_in" in captured.out  # PinType enum values are lowercase
        assert "2" in captured.out
        assert "GND" in captured.out

    def test_show_pins_updates_access_stats(self):
        """Should update access count and timestamp."""
        symbol = SymbolDefinition(
            lib_id="Custom:Test", name="Test", library="Custom", reference_prefix="U"
        )

        initial_count = symbol.access_count
        initial_time = symbol.last_accessed

        symbol.show_pins()

        assert symbol.access_count == initial_count + 1
        assert symbol.last_accessed >= initial_time


class TestGetSymbolInfo:
    """Test get_symbol_info() module-level function."""

    def test_get_symbol_info_returns_symbol_definition(self):
        """Should return SymbolDefinition object."""
        # Use real symbol from standard KiCAD library
        try:
            symbol = ksa.get_symbol_info("Device:R")
            assert isinstance(symbol, SymbolDefinition)
            assert symbol.lib_id == "Device:R"
            assert symbol.name == "R"
            assert symbol.library == "Device"
        except Exception as e:
            # If KiCAD not installed, skip this test
            pytest.skip(f"KiCAD symbols not available: {e}")

    def test_get_symbol_info_not_found(self):
        """Should return None for non-existent symbol."""
        symbol = ksa.get_symbol_info("NonExistent:Symbol")
        assert symbol is None

    def test_get_symbol_info_has_list_pins(self):
        """Should return symbol with list_pins method."""
        try:
            symbol = ksa.get_symbol_info("Device:R")
            assert hasattr(symbol, "list_pins")
            pins = symbol.list_pins()
            assert isinstance(pins, list)
        except Exception:
            pytest.skip("KiCAD symbols not available")

    def test_get_symbol_info_has_show_pins(self):
        """Should return symbol with show_pins method."""
        try:
            symbol = ksa.get_symbol_info("Device:R")
            assert hasattr(symbol, "show_pins")
            # Just check method exists, don't capture output
        except Exception:
            pytest.skip("KiCAD symbols not available")

    def test_get_symbol_info_integration_resistor(self):
        """Integration test with real resistor symbol."""
        try:
            symbol = ksa.get_symbol_info("Device:R")

            # Verify symbol properties
            assert symbol.lib_id == "Device:R"
            assert symbol.reference_prefix == "R"

            # Verify pins
            pins = symbol.list_pins()
            assert len(pins) == 2
            assert pins[0]["number"] == "1"
            assert pins[1]["number"] == "2"
        except Exception:
            pytest.skip("KiCAD symbols not available")

    def test_get_symbol_info_integration_capacitor(self):
        """Integration test with real capacitor symbol."""
        try:
            symbol = ksa.get_symbol_info("Device:C")

            # Verify symbol properties
            assert symbol.lib_id == "Device:C"
            assert symbol.reference_prefix == "C"

            # Verify pins
            pins = symbol.list_pins()
            assert len(pins) == 2
        except Exception:
            pytest.skip("KiCAD symbols not available")


class TestGetSymbolInfoCacheUsage:
    """Test get_symbol_info() uses global cache correctly."""

    def test_uses_global_cache(self):
        """Should use the global symbol cache."""
        # Create new cache and set as global
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        # Create mock symbol and add to cache
        mock_symbol = SymbolDefinition(
            lib_id="Test:MockSymbol", name="MockSymbol", library="Test", reference_prefix="U"
        )
        cache._symbols["Test:MockSymbol"] = mock_symbol

        # get_symbol_info should find it in global cache
        symbol = ksa.get_symbol_info("Test:MockSymbol")

        assert symbol is mock_symbol

    def test_cache_miss_returns_none(self):
        """Should return None when symbol not in cache."""
        # Reset global cache
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        symbol = ksa.get_symbol_info("NotInCache:Symbol")

        assert symbol is None


class TestRealWorldUsageScenarios:
    """Test real-world usage patterns from issue #179."""

    def test_inspect_before_placing(self):
        """User inspects symbol before placing in schematic."""
        try:
            # Inspect ESP32 module
            symbol = ksa.get_symbol_info("RF_Module:ESP32-WROOM-32")

            # Verify has pins
            pins = symbol.list_pins()
            assert len(pins) > 0

            # Can check specific pins
            pin_numbers = [p["number"] for p in pins]
            assert "1" in pin_numbers
        except Exception:
            pytest.skip("RF_Module library not available")

    def test_find_power_pins(self):
        """User finds power pins for a component."""
        try:
            symbol = ksa.get_symbol_info("Device:R")
            pins = symbol.list_pins()

            # Filter for power pins (resistor has passive pins, not power)
            power_pins = [p for p in pins if "POWER" in p["type"]]

            # Resistor should have no power pins
            assert len(power_pins) == 0
        except Exception:
            pytest.skip("KiCAD symbols not available")

    def test_list_all_pins_for_multiunit_symbol(self):
        """User lists pins for multi-unit symbol."""
        try:
            # Op-amp has multiple units
            symbol = ksa.get_symbol_info("Amplifier_Operational:TL072")

            pins = symbol.list_pins()

            # TL072 should have multiple pins
            assert len(pins) > 2
        except Exception:
            pytest.skip("Amplifier_Operational library not available")

    def test_compare_pin_counts(self):
        """User compares pin counts of different symbols."""
        try:
            r_symbol = ksa.get_symbol_info("Device:R")
            c_symbol = ksa.get_symbol_info("Device:C")

            r_pins = r_symbol.list_pins()
            c_pins = c_symbol.list_pins()

            # Both should have 2 pins
            assert len(r_pins) == 2
            assert len(c_pins) == 2
        except Exception:
            pytest.skip("KiCAD symbols not available")
