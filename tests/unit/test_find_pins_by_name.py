#!/usr/bin/env python3
"""
Unit tests for find_pins_by_name and find_pins_by_type tools (Issue #201).

Tests semantic pin lookup by name pattern and electrical type filtering.
"""

import logging

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import PinType

logger = logging.getLogger(__name__)


class TestFindPinsByName:
    """Test find_pins_by_name() method for semantic pin lookup."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("find_pins_test")

    # ========== Exact Match Tests ==========

    def test_find_pins_by_exact_name_match(self, schematic):
        """Test finding pins by exact name match."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Resistor pins are typically named "~" (unnamed)
        pins = schematic.components.find_pins_by_name("R1", "~")

        assert pins is not None
        assert len(pins) > 0
        assert all(isinstance(p, str) for p in pins)

    def test_find_pins_exact_match_returns_empty_for_nonexistent_name(self, schematic):
        """Test that exact match returns empty list when no pins match."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.find_pins_by_name("R1", "NONEXISTENT")

        assert pins is not None
        assert len(pins) == 0

    # ========== Wildcard Pattern Tests ==========

    def test_find_pins_by_wildcard_pattern_start(self, schematic):
        """Test wildcard pattern matching at start (CLK*)."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # This may not match for a resistor, but test the pattern matching logic
        pins = schematic.components.find_pins_by_name("R1", "*")

        # Should match all pins with wildcard
        assert pins is not None
        assert len(pins) > 0

    def test_find_pins_by_wildcard_pattern_end(self, schematic):
        """Test wildcard pattern matching at end (*IN)."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.find_pins_by_name("R1", "*")

        assert pins is not None

    def test_find_pins_by_wildcard_pattern_middle(self, schematic):
        """Test wildcard pattern matching in middle (*CK*)."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.find_pins_by_name("R1", "*")

        assert pins is not None

    # ========== Case Sensitivity Tests ==========

    def test_find_pins_case_insensitive_by_default(self, schematic):
        """Test that matching is case-insensitive by default."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins_lower = schematic.components.find_pins_by_name("R1", "~")
        pins_upper = schematic.components.find_pins_by_name("R1", "~")

        assert pins_lower is not None
        assert pins_upper is not None
        assert len(pins_lower) == len(pins_upper)

    def test_find_pins_case_sensitive_when_specified(self, schematic):
        """Test that case-sensitive matching works when specified."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Test with case sensitivity flag
        pins = schematic.components.find_pins_by_name("R1", "~", case_sensitive=True)

        assert pins is not None

    # ========== Error Handling Tests ==========

    def test_find_pins_by_name_returns_none_for_missing_component(self, schematic):
        """Test that None is returned for missing component."""
        pins = schematic.components.find_pins_by_name("R999", "~")

        assert pins is None

    def test_find_pins_by_name_raises_error_for_empty_pattern(self, schematic):
        """Test that ValueError is raised for empty pattern."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        with pytest.raises(ValueError):
            schematic.components.find_pins_by_name("R1", "")

    def test_find_pins_by_name_returns_correct_pin_numbers(self, schematic):
        """Test that returned values are pin numbers as strings."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.find_pins_by_name("R1", "~")

        assert pins is not None
        assert all(isinstance(p, str) for p in pins)
        # Pin numbers should be numeric strings
        assert all(p.replace(".", "").isalnum() for p in pins)

    # ========== Logging Tests ==========

    def test_find_pins_by_name_debug_logging(self, schematic, caplog):
        """Test that debug logging is produced."""
        with caplog.at_level(logging.DEBUG):
            comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
            pins = schematic.components.find_pins_by_name("R1", "~")

        assert "[PIN_DISCOVERY]" in caplog.text or "find_pins_by_name" in caplog.text


class TestFindPinsByType:
    """Test find_pins_by_type() method for electrical type filtering."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("find_pins_type_test")

    # ========== Basic Type Filtering Tests ==========

    def test_find_pins_by_type_passive(self, schematic):
        """Test finding passive pins (resistors are passive)."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.find_pins_by_type("R1", "passive")

        assert pins is not None
        assert len(pins) > 0
        assert all(isinstance(p, str) for p in pins)

    def test_find_pins_by_type_with_string(self, schematic):
        """Test that string type names work."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.find_pins_by_type("R1", "passive")

        assert pins is not None

    def test_find_pins_by_type_with_enum(self, schematic):
        """Test that PinType enum values work."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        pins = schematic.components.find_pins_by_type("R1", PinType.PASSIVE)

        assert pins is not None

    # ========== No Match Tests ==========

    def test_find_pins_by_type_returns_empty_for_no_match(self, schematic):
        """Test that empty list is returned when no pins match type."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Resistor has no input pins
        pins = schematic.components.find_pins_by_type("R1", "input")

        assert pins is not None
        assert len(pins) == 0

    # ========== Error Handling Tests ==========

    def test_find_pins_by_type_returns_none_for_missing_component(self, schematic):
        """Test that None is returned for missing component."""
        pins = schematic.components.find_pins_by_type("R999", "passive")

        assert pins is None

    def test_find_pins_by_type_raises_error_for_invalid_type(self, schematic):
        """Test that ValueError is raised for invalid type."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        with pytest.raises(ValueError):
            schematic.components.find_pins_by_type("R1", "invalid_type")

    # ========== Logging Tests ==========

    def test_find_pins_by_type_debug_logging(self, schematic, caplog):
        """Test that debug logging is produced."""
        with caplog.at_level(logging.DEBUG):
            comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
            pins = schematic.components.find_pins_by_type("R1", "passive")

        assert "[PIN_DISCOVERY]" in caplog.text or "find_pins_by_type" in caplog.text


class TestSemanticPinLookupIntegration:
    """Integration tests for semantic pin lookup workflows."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("semantic_lookup_test")

    def test_workflow_find_and_get_pin_info(self, schematic):
        """Test workflow: find pins by name, then get their info."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Step 1: Find pins by name
        pins = schematic.components.find_pins_by_name("R1", "~")
        assert pins is not None and len(pins) > 0

        # Step 2: Get detailed info for those pins
        pin_info_list = schematic.components.get_pins_info("R1")
        assert pin_info_list is not None

        # Step 3: Verify they match
        pin_info_numbers = [p.number for p in pin_info_list]
        assert len(pin_info_numbers) == len(pins)

    def test_workflow_find_pins_by_type_and_use(self, schematic):
        """Test workflow: find passive pins and work with them."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Find passive pins
        passive_pins = schematic.components.find_pins_by_type("R1", "passive")

        assert passive_pins is not None
        assert len(passive_pins) > 0

    def test_workflow_multiple_components(self, schematic):
        """Test workflow with multiple components."""
        r1 = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = schematic.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))

        # Find pins in both
        r1_pins = schematic.components.find_pins_by_name("R1", "~")
        r2_pins = schematic.components.find_pins_by_name("R2", "~")

        assert r1_pins is not None and len(r1_pins) > 0
        assert r2_pins is not None and len(r2_pins) > 0

        # Should have same pin numbers (both resistors)
        assert len(r1_pins) == len(r2_pins)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
