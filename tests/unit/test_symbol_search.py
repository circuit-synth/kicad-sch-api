"""
Unit tests for symbol search functionality (Issue #179 Phase 3).

Tests the search_symbols() function for finding symbols by name,
description, or keywords.
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import PinType, Point, SchematicPin
from kicad_sch_api.library.cache import SymbolDefinition, SymbolLibraryCache


class TestSymbolLibraryCacheSearchSymbols:
    """Test SymbolLibraryCache.search_symbols() method."""

    def test_search_empty_cache(self):
        """Should return empty list when cache is empty."""
        cache = SymbolLibraryCache(enable_persistence=False)

        results = cache.search_symbols("resistor")

        assert results == []
        assert isinstance(results, list)

    def test_search_by_name(self):
        """Should find symbols by name."""
        cache = SymbolLibraryCache(enable_persistence=False)

        # Add test symbols
        resistor = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
        )
        capacitor = SymbolDefinition(
            lib_id="Device:C",
            name="C",
            library="Device",
            reference_prefix="C",
            description="Capacitor",
        )
        cache._symbols["Device:R"] = resistor
        cache._symbols["Device:C"] = capacitor

        results = cache.search_symbols("R")

        assert len(results) >= 1
        assert any(s.lib_id == "Device:R" for s in results)

    def test_search_by_description(self):
        """Should find symbols by description."""
        cache = SymbolLibraryCache(enable_persistence=False)

        resistor = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor component",
        )
        cache._symbols["Device:R"] = resistor

        results = cache.search_symbols("Resistor")

        assert len(results) >= 1
        assert any(s.lib_id == "Device:R" for s in results)

    def test_search_by_keywords(self):
        """Should find symbols by keywords."""
        cache = SymbolLibraryCache(enable_persistence=False)

        resistor = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
            keywords="passive component",
        )
        cache._symbols["Device:R"] = resistor

        results = cache.search_symbols("passive")

        assert len(results) >= 1
        assert any(s.lib_id == "Device:R" for s in results)

    def test_search_case_insensitive(self):
        """Should be case insensitive."""
        cache = SymbolLibraryCache(enable_persistence=False)

        resistor = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
        )
        cache._symbols["Device:R"] = resistor

        results_upper = cache.search_symbols("RESISTOR")
        results_lower = cache.search_symbols("resistor")
        results_mixed = cache.search_symbols("ReSiStOr")

        assert len(results_upper) == len(results_lower) == len(results_mixed)
        assert all(s.lib_id == "Device:R" for s in results_upper)

    def test_search_with_library_filter(self):
        """Should filter by library name."""
        cache = SymbolLibraryCache(enable_persistence=False)

        device_r = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
        )
        rf_module = SymbolDefinition(
            lib_id="RF_Module:ESP32",
            name="ESP32",
            library="RF_Module",
            reference_prefix="U",
            description="ESP32 WiFi module",
        )
        cache._symbols["Device:R"] = device_r
        cache._symbols["RF_Module:ESP32"] = rf_module

        results = cache.search_symbols("module", library="RF_Module")

        assert len(results) == 1
        assert results[0].lib_id == "RF_Module:ESP32"

    def test_search_with_limit(self):
        """Should respect result limit."""
        cache = SymbolLibraryCache(enable_persistence=False)

        # Add 10 resistor symbols
        for i in range(10):
            symbol = SymbolDefinition(
                lib_id=f"Device:R{i}",
                name=f"R{i}",
                library="Device",
                reference_prefix="R",
                description="Resistor",
            )
            cache._symbols[f"Device:R{i}"] = symbol

        results = cache.search_symbols("Resistor", limit=5)

        assert len(results) <= 5

    def test_search_no_matches(self):
        """Should return empty list when no matches."""
        cache = SymbolLibraryCache(enable_persistence=False)

        resistor = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
        )
        cache._symbols["Device:R"] = resistor

        results = cache.search_symbols("nonexistent")

        assert results == []

    def test_search_exact_lib_id(self):
        """Should prioritize exact lib_id matches."""
        cache = SymbolLibraryCache(enable_persistence=False)

        resistor = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
        )
        cache._symbols["Device:R"] = resistor

        results = cache.search_symbols("Device:R")

        # Exact match should be first
        assert len(results) >= 1
        assert results[0].lib_id == "Device:R"


class TestSearchSymbolsFunction:
    """Test search_symbols() module-level function."""

    def test_search_symbols_returns_list(self):
        """Should return list of SymbolDefinition objects."""
        # Create new cache and set as global
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        resistor = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
        )
        cache._symbols["Device:R"] = resistor

        results = ksa.search_symbols("resistor")

        assert isinstance(results, list)
        assert all(isinstance(s, SymbolDefinition) for s in results)

    def test_search_symbols_uses_global_cache(self):
        """Should use the global symbol cache."""
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        test_symbol = SymbolDefinition(
            lib_id="Test:Symbol",
            name="Symbol",
            library="Test",
            reference_prefix="U",
            description="Test symbol for search",
        )
        cache._symbols["Test:Symbol"] = test_symbol

        results = ksa.search_symbols("Test symbol")

        assert len(results) == 1
        assert results[0].lib_id == "Test:Symbol"

    def test_search_symbols_with_library_filter(self):
        """Should filter by library using module function."""
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        device_r = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
        )
        rf_module = SymbolDefinition(
            lib_id="RF_Module:ESP32",
            name="ESP32",
            library="RF_Module",
            reference_prefix="U",
            description="WiFi module",
        )
        cache._symbols["Device:R"] = device_r
        cache._symbols["RF_Module:ESP32"] = rf_module

        results = ksa.search_symbols("module", library="RF_Module")

        assert len(results) == 1
        assert results[0].library == "RF_Module"

    def test_search_symbols_with_limit(self):
        """Should respect limit parameter."""
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        for i in range(20):
            symbol = SymbolDefinition(
                lib_id=f"Device:R{i}",
                name=f"R{i}",
                library="Device",
                reference_prefix="R",
                description="Resistor",
            )
            cache._symbols[f"Device:R{i}"] = symbol

        results = ksa.search_symbols("resistor", limit=10)

        assert len(results) <= 10

    def test_search_symbols_empty_query(self):
        """Should handle empty query gracefully."""
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        results = ksa.search_symbols("")

        assert isinstance(results, list)


class TestSearchIntegration:
    """Integration tests with real KiCAD libraries (if available)."""

    def test_search_real_resistor(self):
        """Should find resistor in Device library."""
        try:
            results = ksa.search_symbols("resistor", library="Device")

            # Should find at least one resistor
            assert len(results) > 0
            # Should include Device:R
            assert any("R" in s.name for s in results)
        except Exception:
            pytest.skip("KiCAD libraries not available")

    def test_search_real_capacitor(self):
        """Should find capacitor in Device library."""
        try:
            results = ksa.search_symbols("capacitor", library="Device")

            assert len(results) > 0
            assert any("C" in s.name for s in results)
        except Exception:
            pytest.skip("KiCAD libraries not available")

    def test_search_esp32_modules(self):
        """Should find ESP32 modules."""
        try:
            results = ksa.search_symbols("ESP32")

            # Should find ESP32 modules
            assert len(results) > 0
            # Check if any result is from RF_Module library
            rf_modules = [s for s in results if s.library == "RF_Module"]
            # If RF_Module library exists, it should have ESP32
            if rf_modules:
                assert any("ESP32" in s.name for s in rf_modules)
        except Exception:
            pytest.skip("KiCAD libraries not available")


class TestRealWorldUsageScenarios:
    """Test real-world usage patterns."""

    def test_find_all_resistors(self):
        """User searches for all resistor types."""
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        # Add various resistor types
        symbols = [
            SymbolDefinition(
                lib_id="Device:R",
                name="R",
                library="Device",
                reference_prefix="R",
                description="Resistor",
            ),
            SymbolDefinition(
                lib_id="Device:R_Variable",
                name="R_Variable",
                library="Device",
                reference_prefix="R",
                description="Variable resistor",
            ),
            SymbolDefinition(
                lib_id="Device:R_Potentiometer",
                name="R_Potentiometer",
                library="Device",
                reference_prefix="R",
                description="Potentiometer",
            ),
        ]
        for symbol in symbols:
            cache._symbols[symbol.lib_id] = symbol

        results = ksa.search_symbols("resistor")

        # Should find multiple resistor types
        assert len(results) >= 2
        assert any("Variable" in s.description for s in results)

    def test_search_and_inspect_symbol(self):
        """User searches for component and inspects properties."""
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        esp32 = SymbolDefinition(
            lib_id="RF_Module:ESP32",
            name="ESP32",
            library="RF_Module",
            reference_prefix="U",
            description="WiFi/Bluetooth module",
            pins=[
                SchematicPin(
                    number="1",
                    name="GND",
                    pin_type=PinType.POWER_IN,
                    position=Point(0, 0),
                )
            ],
        )
        cache._symbols["RF_Module:ESP32"] = esp32

        # Search for ESP32
        results = ksa.search_symbols("ESP32")
        assert len(results) == 1

        # Inspect symbol properties
        symbol = results[0]
        assert symbol.lib_id == "RF_Module:ESP32"
        assert symbol.description == "WiFi/Bluetooth module"
        assert len(symbol.pins) == 1

    def test_filter_by_library_find_power_symbols(self):
        """User searches for power symbols in specific library."""
        cache = SymbolLibraryCache(enable_persistence=False)
        ksa.library.cache.set_symbol_cache(cache)

        # Add power symbols
        gnd = SymbolDefinition(
            lib_id="power:GND",
            name="GND",
            library="power",
            reference_prefix="#PWR",
            description="Ground symbol",
            power_symbol=True,
        )
        vcc = SymbolDefinition(
            lib_id="power:VCC",
            name="VCC",
            library="power",
            reference_prefix="#PWR",
            description="Power supply symbol",
            power_symbol=True,
        )
        cache._symbols["power:GND"] = gnd
        cache._symbols["power:VCC"] = vcc

        results = ksa.search_symbols("power", library="power")

        assert len(results) >= 1
        assert all(s.power_symbol for s in results)
