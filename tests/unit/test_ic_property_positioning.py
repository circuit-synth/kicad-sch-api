"""
Unit tests for IC component property positioning rules.

Tests verify that the 6 IC components from Issue #176 have correct positioning rules
and no longer fall back to the resistor pattern.

Related:
- Issue #176: Missing IC property positioning rules causes incorrect text placement
- PRD: docs/prd/ic-property-positioning-prd.md
"""

import pytest

from kicad_sch_api.core.property_positioning import (
    POSITIONING_RULES,
    PropertyOffset,
    get_property_position,
)


class TestICPositioningRulesExist:
    """Verify all 6 IC components have positioning rules defined."""

    def test_esp32_wroom_32_rule_exists(self):
        """ESP32-WROOM-32 should have a positioning rule."""
        assert "RF_Module:ESP32-WROOM-32" in POSITIONING_RULES

    def test_74ls245_rule_exists(self):
        """74LS245 should have a positioning rule."""
        assert "74xx:74LS245" in POSITIONING_RULES

    def test_max3485_rule_exists(self):
        """MAX3485 should have a positioning rule."""
        assert "Interface_UART:MAX3485" in POSITIONING_RULES

    def test_ams1117_rule_exists(self):
        """AMS1117-3.3 should have a positioning rule."""
        assert "Regulator_Linear:AMS1117-3.3" in POSITIONING_RULES

    def test_tps54202_rule_exists(self):
        """TPS54202DDC should have a positioning rule."""
        assert "Regulator_Switching:TPS54202DDC" in POSITIONING_RULES

    def test_ao3401a_rule_exists(self):
        """AO3401A should have a positioning rule."""
        assert "Transistor_FET:AO3401A" in POSITIONING_RULES


class TestESP32PropertyPositioning:
    """Test ESP32-WROOM-32 property positioning (large RF module)."""

    def test_esp32_reference_offset(self):
        """Reference should be positioned at (-12.7, 34.29) from component center.

        Large IC (40mm × 86mm) requires properties FAR ABOVE component.
        """
        rule = POSITIONING_RULES["RF_Module:ESP32-WROOM-32"]
        assert rule.reference_offset.x == pytest.approx(-12.7, abs=0.01)
        assert rule.reference_offset.y == pytest.approx(34.29, abs=0.01)
        assert rule.reference_offset.rotation == 0.0

    def test_esp32_value_offset(self):
        """Value should be positioned at (1.27, 34.29) from component center."""
        rule = POSITIONING_RULES["RF_Module:ESP32-WROOM-32"]
        assert rule.value_offset.x == pytest.approx(1.27, abs=0.01)
        assert rule.value_offset.y == pytest.approx(34.29, abs=0.01)
        assert rule.value_offset.rotation == 0.0

    def test_esp32_footprint_offset(self):
        """Footprint should be positioned at (0, -38.1) from component center."""
        rule = POSITIONING_RULES["RF_Module:ESP32-WROOM-32"]
        assert rule.footprint_offset.x == pytest.approx(0, abs=0.01)
        assert rule.footprint_offset.y == pytest.approx(-38.1, abs=0.01)
        assert rule.footprint_offset.rotation == 0.0


class Test74LS245PropertyPositioning:
    """Test 74LS245 property positioning (SOIC-20W level shifter)."""

    def test_74ls245_reference_offset(self):
        """Reference should be positioned LEFT and ABOVE (-7.62, 16.51)."""
        rule = POSITIONING_RULES["74xx:74LS245"]
        assert rule.reference_offset.x == pytest.approx(-7.62, abs=0.01)
        assert rule.reference_offset.y == pytest.approx(16.51, abs=0.01)

    def test_74ls245_value_offset(self):
        """Value should be positioned LEFT and BELOW (-7.62, -16.51)."""
        rule = POSITIONING_RULES["74xx:74LS245"]
        assert rule.value_offset.x == pytest.approx(-7.62, abs=0.01)
        assert rule.value_offset.y == pytest.approx(-16.51, abs=0.01)


class TestMAX3485PropertyPositioning:
    """Test MAX3485 property positioning (SOIC-8 UART transceiver)."""

    def test_max3485_reference_offset(self):
        """Reference should be positioned at (-6.985, 13.97) - LEFT and ABOVE."""
        rule = POSITIONING_RULES["Interface_UART:MAX3485"]
        assert rule.reference_offset.x == pytest.approx(-6.985, abs=0.01)
        assert rule.reference_offset.y == pytest.approx(13.97, abs=0.01)

    def test_max3485_value_offset(self):
        """Value should be positioned at (1.905, 13.97) - RIGHT and ABOVE."""
        rule = POSITIONING_RULES["Interface_UART:MAX3485"]
        assert rule.value_offset.x == pytest.approx(1.905, abs=0.01)
        assert rule.value_offset.y == pytest.approx(13.97, abs=0.01)


class TestAMS1117PropertyPositioning:
    """Test AMS1117-3.3 property positioning (SOT-223 linear regulator)."""

    def test_ams1117_reference_offset(self):
        """Reference should be positioned LEFT and ABOVE (-3.81, 3.175)."""
        rule = POSITIONING_RULES["Regulator_Linear:AMS1117-3.3"]
        assert rule.reference_offset.x == pytest.approx(-3.81, abs=0.01)
        assert rule.reference_offset.y == pytest.approx(3.175, abs=0.01)

    def test_ams1117_value_offset(self):
        """Value should be positioned CENTERED ABOVE (0, 3.175)."""
        rule = POSITIONING_RULES["Regulator_Linear:AMS1117-3.3"]
        assert rule.value_offset.x == pytest.approx(0, abs=0.01)
        assert rule.value_offset.y == pytest.approx(3.175, abs=0.01)


class TestTPS54202PropertyPositioning:
    """Test TPS54202DDC property positioning (SOT-23-6 switching regulator)."""

    def test_tps54202_reference_offset(self):
        """Reference should be positioned LEFT and ABOVE (-7.62, 6.35)."""
        rule = POSITIONING_RULES["Regulator_Switching:TPS54202DDC"]
        assert rule.reference_offset.x == pytest.approx(-7.62, abs=0.01)
        assert rule.reference_offset.y == pytest.approx(6.35, abs=0.01)

    def test_tps54202_value_offset(self):
        """Value should be positioned CENTERED ABOVE (0, 6.35)."""
        rule = POSITIONING_RULES["Regulator_Switching:TPS54202DDC"]
        assert rule.value_offset.x == pytest.approx(0, abs=0.01)
        assert rule.value_offset.y == pytest.approx(6.35, abs=0.01)


class TestAO3401APropertyPositioning:
    """Test AO3401A property positioning (SOT-23 P-channel FET)."""

    def test_ao3401a_reference_offset(self):
        """Reference should be positioned RIGHT (5.08, 1.905)."""
        rule = POSITIONING_RULES["Transistor_FET:AO3401A"]
        assert rule.reference_offset.x == pytest.approx(5.08, abs=0.01)
        assert rule.reference_offset.y == pytest.approx(1.905, abs=0.01)

    def test_ao3401a_value_offset(self):
        """Value should be positioned RIGHT and CENTERED (5.08, 0)."""
        rule = POSITIONING_RULES["Transistor_FET:AO3401A"]
        assert rule.value_offset.x == pytest.approx(5.08, abs=0.01)
        assert rule.value_offset.y == pytest.approx(0, abs=0.01)


class TestICPropertyPositionCalculation:
    """Test that get_property_position() uses IC rules correctly."""

    def test_esp32_no_warning_for_missing_rule(self, caplog):
        """ESP32-WROOM-32 should NOT trigger 'No positioning rule' warning."""
        import logging

        caplog.set_level(logging.WARNING)

        # Call get_property_position with ESP32
        pos = get_property_position("RF_Module:ESP32-WROOM-32", "Reference", (100, 100), 0)

        # Verify no warning logged
        assert "No positioning rule" not in caplog.text
        assert "ESP32-WROOM-32" not in caplog.text

        # Verify position calculated correctly
        assert pos[0] == pytest.approx(100 - 12.7, abs=0.01)  # x = 100 + (-12.7)
        assert pos[1] == pytest.approx(100 + 34.29, abs=0.01)  # y = 100 + 34.29

    def test_74ls245_property_position(self):
        """74LS245 Reference should be at correct position."""
        pos = get_property_position("74xx:74LS245", "Reference", (100, 100), 0)

        # Reference offset: (-7.62, 16.51)
        assert pos[0] == pytest.approx(100 - 7.62, abs=0.01)
        assert pos[1] == pytest.approx(100 + 16.51, abs=0.01)
        assert pos[2] == 0.0  # No text rotation

    def test_max3485_value_position(self):
        """MAX3485 Value should be at correct position."""
        pos = get_property_position("Interface_UART:MAX3485", "Value", (100, 100), 0)

        # Value offset: (1.905, 13.97)
        assert pos[0] == pytest.approx(100 + 1.905, abs=0.01)
        assert pos[1] == pytest.approx(100 + 13.97, abs=0.01)
        assert pos[2] == 0.0

    def test_all_ics_have_non_resistor_offsets(self):
        """Verify all 6 ICs use different offsets than resistor pattern.

        Resistor pattern: Reference (+2.54, -1.2701), Value (+2.54, +1.2699)
        All ICs should have different offsets to avoid text overlap.
        """
        resistor_ref_offset = POSITIONING_RULES["Device:R"].reference_offset
        ic_lib_ids = [
            "RF_Module:ESP32-WROOM-32",
            "74xx:74LS245",
            "Interface_UART:MAX3485",
            "Regulator_Linear:AMS1117-3.3",
            "Regulator_Switching:TPS54202DDC",
            "Transistor_FET:AO3401A",
        ]

        for lib_id in ic_lib_ids:
            rule = POSITIONING_RULES[lib_id]
            ref_offset = rule.reference_offset

            # IC offset should differ from resistor offset
            # Either X is different OR Y is different (or both)
            assert (
                abs(ref_offset.x - resistor_ref_offset.x) > 0.01
                or abs(ref_offset.y - resistor_ref_offset.y) > 0.01
            ), f"{lib_id} using resistor pattern!"
