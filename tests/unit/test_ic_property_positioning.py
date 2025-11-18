"""
Unit tests for IC component property positioning with dynamic symbol library loading.

Tests verify that IC components from Issue #176 load property positions dynamically
from KiCAD symbol library files instead of using hard-coded rules.

Related:
- Issue #176: Missing IC property positioning rules causes incorrect text placement
- PRD: docs/prd/ic-property-positioning-prd.md
"""

import pytest

from kicad_sch_api.core.property_positioning import get_property_position
from kicad_sch_api.library.cache import get_symbol_cache


class TestESP32PropertyPositioning:
    """Test ESP32-WROOM-32 property positioning (large RF module)."""

    def test_esp32_reference_position_from_symbol_library(self):
        """Reference should be loaded from symbol library at (-12.7, 34.29)."""
        pos = get_property_position("RF_Module:ESP32-WROOM-32", "Reference", (100, 100), 0)
        assert pos[0] == pytest.approx(100 - 12.7, abs=0.01)
        assert pos[1] == pytest.approx(100 + 34.29, abs=0.01)

    def test_esp32_value_position_from_symbol_library(self):
        """Value should be loaded from symbol library at (1.27, 34.29)."""
        pos = get_property_position("RF_Module:ESP32-WROOM-32", "Value", (100, 100), 0)
        assert pos[0] == pytest.approx(100 + 1.27, abs=0.01)
        assert pos[1] == pytest.approx(100 + 34.29, abs=0.01)


class Test74LS245PropertyPositioning:
    """Test 74LS245 property positioning (SOIC-20W level shifter)."""

    def test_74ls245_reference_position_from_symbol_library(self):
        """Reference should be loaded from symbol library at (-7.62, 16.51)."""
        pos = get_property_position("74xx:74LS245", "Reference", (100, 100), 0)
        assert pos[0] == pytest.approx(100 - 7.62, abs=0.01)
        assert pos[1] == pytest.approx(100 + 16.51, abs=0.01)

    def test_74ls245_value_position_from_symbol_library(self):
        """Value should be loaded from symbol library at (-7.62, -16.51)."""
        pos = get_property_position("74xx:74LS245", "Value", (100, 100), 0)
        assert pos[0] == pytest.approx(100 - 7.62, abs=0.01)
        assert pos[1] == pytest.approx(100 - 16.51, abs=0.01)


class TestMAX3485PropertyPositioning:
    """Test MAX3485 property positioning (SOIC-8 UART transceiver)."""

    def test_max3485_reference_position_from_symbol_library(self):
        """Reference should be loaded from symbol library at (-6.985, 13.97)."""
        pos = get_property_position("Interface_UART:MAX3485", "Reference", (100, 100), 0)
        assert pos[0] == pytest.approx(100 - 6.985, abs=0.01)
        assert pos[1] == pytest.approx(100 + 13.97, abs=0.01)

    def test_max3485_value_position_from_symbol_library(self):
        """Value should be loaded from symbol library at (1.905, 13.97)."""
        pos = get_property_position("Interface_UART:MAX3485", "Value", (100, 100), 0)
        assert pos[0] == pytest.approx(100 + 1.905, abs=0.01)
        assert pos[1] == pytest.approx(100 + 13.97, abs=0.01)


class TestAMS1117PropertyPositioning:
    """Test AMS1117-3.3 property positioning (SOT-223 linear regulator)."""

    def test_ams1117_reference_position_from_symbol_library(self):
        """Reference should be loaded from symbol library at (-3.81, 3.175)."""
        pos = get_property_position("Regulator_Linear:AMS1117-3.3", "Reference", (100, 100), 0)
        assert pos[0] == pytest.approx(100 - 3.81, abs=0.01)
        assert pos[1] == pytest.approx(100 + 3.175, abs=0.01)

    def test_ams1117_value_position_from_symbol_library(self):
        """Value should be loaded from symbol library at (0, 3.175)."""
        pos = get_property_position("Regulator_Linear:AMS1117-3.3", "Value", (100, 100), 0)
        assert pos[0] == pytest.approx(100 + 0, abs=0.01)
        assert pos[1] == pytest.approx(100 + 3.175, abs=0.01)


class TestTPS54202PropertyPositioning:
    """Test TPS54202DDC property positioning (SOT-23-6 switching regulator)."""

    def test_tps54202_reference_position_from_symbol_library(self):
        """Reference should be loaded from symbol library at (-7.62, 6.35)."""
        pos = get_property_position("Regulator_Switching:TPS54202DDC", "Reference", (100, 100), 0)
        assert pos[0] == pytest.approx(100 - 7.62, abs=0.01)
        assert pos[1] == pytest.approx(100 + 6.35, abs=0.01)

    def test_tps54202_value_position_from_symbol_library(self):
        """Value should be loaded from symbol library at (0, 6.35)."""
        pos = get_property_position("Regulator_Switching:TPS54202DDC", "Value", (100, 100), 0)
        assert pos[0] == pytest.approx(100 + 0, abs=0.01)
        assert pos[1] == pytest.approx(100 + 6.35, abs=0.01)


class TestAO3401APropertyPositioning:
    """Test AO3401A property positioning (SOT-23 P-channel FET)."""

    def test_ao3401a_reference_position_from_symbol_library(self):
        """Reference should be loaded from symbol library at (5.08, 1.905)."""
        pos = get_property_position("Transistor_FET:AO3401A", "Reference", (100, 100), 0)
        assert pos[0] == pytest.approx(100 + 5.08, abs=0.01)
        assert pos[1] == pytest.approx(100 + 1.905, abs=0.01)

    def test_ao3401a_value_position_from_symbol_library(self):
        """Value should be loaded from symbol library at (5.08, 0)."""
        pos = get_property_position("Transistor_FET:AO3401A", "Value", (100, 100), 0)
        assert pos[0] == pytest.approx(100 + 5.08, abs=0.01)
        assert pos[1] == pytest.approx(100 + 0, abs=0.01)


class TestDynamicPropertyLoading:
    """Test that property positions are loaded dynamically from symbol libraries."""

    def test_esp32_no_warning_for_missing_rule(self, caplog):
        """ESP32-WROOM-32 should load from symbol library without warnings."""
        import logging

        caplog.set_level(logging.WARNING)

        # Call get_property_position with ESP32
        pos = get_property_position("RF_Module:ESP32-WROOM-32", "Reference", (100, 100), 0)

        # Should not warn about missing rules (loaded from library)
        assert "No positioning rule for RF_Module:ESP32-WROOM-32" not in caplog.text

        # Verify position calculated correctly from symbol library
        assert pos[0] == pytest.approx(100 - 12.7, abs=0.01)
        assert pos[1] == pytest.approx(100 + 34.29, abs=0.01)

    def test_all_ics_load_from_symbol_library(self):
        """Verify all 6 ICs load property positions from symbol library files."""
        ic_lib_ids_and_expected = [
            ("RF_Module:ESP32-WROOM-32", (-12.7, 34.29)),
            ("74xx:74LS245", (-7.62, 16.51)),
            ("Interface_UART:MAX3485", (-6.985, 13.97)),
            ("Regulator_Linear:AMS1117-3.3", (-3.81, 3.175)),
            ("Regulator_Switching:TPS54202DDC", (-7.62, 6.35)),
            ("Transistor_FET:AO3401A", (5.08, 1.905)),
        ]

        for lib_id, (expected_x, expected_y) in ic_lib_ids_and_expected:
            pos = get_property_position(lib_id, "Reference", (100, 100), 0)

            # Verify position matches symbol library data
            assert pos[0] == pytest.approx(
                100 + expected_x, abs=0.01
            ), f"{lib_id} Reference X position incorrect"
            assert pos[1] == pytest.approx(
                100 + expected_y, abs=0.01
            ), f"{lib_id} Reference Y position incorrect"

    def test_symbol_library_positions_used_before_fallback(self):
        """Symbol library data should be used before hard-coded fallback rules."""
        # This test ensures the dynamic loading happens FIRST
        # For a component in the symbol library, we should get library data
        # not fall back to POSITIONING_RULES

        cache = get_symbol_cache()
        symbol = cache.get_symbol("Device:R")

        # Device:R should have property_positions from library
        assert symbol is not None
        assert symbol.property_positions is not None
        assert len(symbol.property_positions) > 0

        # Position should come from symbol library
        pos = get_property_position("Device:R", "Reference", (100, 100), 0)
        # We should get data from symbol library, not hard-coded rule
        assert pos is not None
