#!/usr/bin/env python3
"""
Integration tests for find_pins_by_name semantic lookup (Issue #201).

Tests complete workflows and performance characteristics.
"""

import logging
import time
import pytest
import kicad_sch_api as ksa


logger = logging.getLogger(__name__)


class TestSemanticPinLookupPerformance:
    """Test performance characteristics of semantic pin lookup."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("perf_test")

    def test_performance_find_pins_by_name_single_component(self, schematic):
        """Test that find_pins_by_name is fast for single component."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        start = time.time()
        pins = schematic.components.find_pins_by_name("R1", "~")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert pins is not None
        assert elapsed < 50, f"find_pins_by_name took {elapsed:.2f}ms (should be <50ms)"

    def test_performance_find_pins_by_type_single_component(self, schematic):
        """Test that find_pins_by_type is fast for single component."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        start = time.time()
        pins = schematic.components.find_pins_by_type("R1", "passive")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert pins is not None
        assert elapsed < 50, f"find_pins_by_type took {elapsed:.2f}ms (should be <50ms)"

    def test_performance_many_lookups(self, schematic):
        """Test performance with many lookups."""
        # Add 10 components
        for i in range(10):
            schematic.components.add("Device:R", f"R{i+1}", f"{10*(i+1)}k", position=(100.0 + i*5, 100.0))

        # Do 50 lookups
        start = time.time()
        for i in range(10):
            pins = schematic.components.find_pins_by_name(f"R{i+1}", "~")
            assert pins is not None
        elapsed = (time.time() - start) * 1000  # Convert to ms

        avg_time = elapsed / 10
        assert avg_time < 50, f"Average lookup took {avg_time:.2f}ms (should be <50ms)"


class TestSemanticPinLookupWorkflows:
    """Test complete workflows using semantic pin lookup."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("workflow_test")

    def test_workflow_find_and_connect_pins(self, schematic):
        """Test workflow: find pins semantically, then work with them."""
        # Add components
        r1 = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        r2 = schematic.components.add("Device:R", "R2", "20k", position=(150.0, 100.0))

        # Step 1: Find pins
        r1_pins = schematic.components.find_pins_by_name("R1", "~")
        r2_pins = schematic.components.find_pins_by_name("R2", "~")

        assert r1_pins is not None and len(r1_pins) > 0
        assert r2_pins is not None and len(r2_pins) > 0

        # Step 2: Verify pins exist
        r1_info = schematic.components.get_pins_info("R1")
        r2_info = schematic.components.get_pins_info("R2")

        assert r1_info is not None
        assert r2_info is not None

        # Step 3: Get positions for connection
        r1_pin_numbers = [p.number for p in r1_info]
        r2_pin_numbers = [p.number for p in r2_info]

        assert len(r1_pin_numbers) > 0
        assert len(r2_pin_numbers) > 0

    def test_workflow_filter_by_type_then_get_info(self, schematic):
        """Test workflow: filter by type, then get detailed pin info."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Step 1: Find all passive pins
        passive_pins = schematic.components.find_pins_by_type("R1", "passive")
        assert passive_pins is not None

        # Step 2: Get detailed info
        all_pins = schematic.components.get_pins_info("R1")
        assert all_pins is not None

        # Step 3: Cross-reference
        pin_numbers = [p.number for p in all_pins]
        assert all(p in pin_numbers for p in passive_pins)

    def test_workflow_mixed_components(self, schematic):
        """Test workflow with different component types."""
        r1 = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
        c1 = schematic.components.add("Device:C", "C1", "100nF", position=(150.0, 100.0))

        # Find passive pins in both
        r1_passive = schematic.components.find_pins_by_type("R1", "passive")
        c1_passive = schematic.components.find_pins_by_type("C1", "passive")

        assert r1_passive is not None and len(r1_passive) > 0
        assert c1_passive is not None and len(c1_passive) > 0

        # Should have same number of pins (both 2-pin passive components)
        assert len(r1_passive) == len(c1_passive)

    def test_workflow_find_specific_pin_names(self, schematic):
        """Test finding pins by specific semantic names."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Resistor pins are named "~" (unnamed)
        pins = schematic.components.find_pins_by_name("R1", "~")

        assert pins is not None

    def test_workflow_pattern_matching_variations(self, schematic):
        """Test different pattern matching scenarios."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        # Test various patterns (even if they don't match for resistor)
        # The point is to verify the pattern matching works

        # Exact match
        exact = schematic.components.find_pins_by_name("R1", "~")
        assert exact is not None

        # Wildcard all
        wildcard_all = schematic.components.find_pins_by_name("R1", "*")
        assert wildcard_all is not None
        assert len(wildcard_all) > 0

        # Wildcard should find same pins as exact for this case
        # (since resistor only has unnamed pins)
        assert len(exact) == len(wildcard_all) or len(exact) == 0


class TestSemanticLookupErrorHandling:
    """Test error handling in semantic lookup."""

    @pytest.fixture
    def schematic(self):
        """Create a fresh schematic for each test."""
        return ksa.create_schematic("error_test")

    def test_error_handling_missing_component(self, schematic):
        """Test graceful error handling for missing components."""
        # find_pins_by_name should return None
        pins = schematic.components.find_pins_by_name("R999", "~")
        assert pins is None

        # find_pins_by_type should return None
        pins = schematic.components.find_pins_by_type("R999", "passive")
        assert pins is None

    def test_error_handling_invalid_type(self, schematic):
        """Test error handling for invalid pin type."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        with pytest.raises(ValueError):
            schematic.components.find_pins_by_type("R1", "invalid_type")

    def test_error_handling_empty_pattern(self, schematic):
        """Test error handling for empty pattern."""
        comp = schematic.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))

        with pytest.raises(ValueError):
            schematic.components.find_pins_by_name("R1", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
