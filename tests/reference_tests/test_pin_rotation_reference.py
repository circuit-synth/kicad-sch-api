#!/usr/bin/env python3
"""
Reference tests for pin rotation using manually created KiCad schematics.

These tests verify that our pin position calculations match real KiCad wire endpoints
from manually created schematics with rotated components.
"""

import math

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.library.cache import get_symbol_cache


class TestPinRotationReference:
    """Test pin rotation against reference KiCad schematics."""

    @staticmethod
    def get_component_by_reference(sch, reference):
        """Helper to get component by reference with pins populated."""
        for comp in sch.components:
            if comp.reference == reference:
                # Populate pins from symbol library (needed for loaded schematics)
                cache = get_symbol_cache()
                symbol_def = cache.get_symbol(comp.lib_id)
                if symbol_def and not comp.pins:
                    comp._data.pins = symbol_def.pins.copy()
                return comp
        return None

    def test_pin_rotation_0_degrees_reference(self):
        """Test 0° rotation against manual KiCad reference."""
        sch_path = (
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )
        sch = ksa.Schematic.load(sch_path)

        # Get the resistor component
        r1 = self.get_component_by_reference(sch, "R1")
        assert r1 is not None, "R1 should exist in schematic"
        assert r1.rotation == 0.0, "R1 should be at 0° rotation"

        # Get calculated pin positions
        pin1_pos = r1.get_pin_position("1")
        pin2_pos = r1.get_pin_position("2")

        assert pin1_pos is not None
        assert pin2_pos is not None

        # Reference wire endpoints from manually created KiCad file:
        # Pin 1 wire connects at: (96.52, 104.14)
        # Pin 2 wire connects at: (96.52, 96.52)
        assert math.isclose(
            pin1_pos.x, 96.52, abs_tol=0.01
        ), f"Pin 1 X position should match KiCad wire endpoint: {pin1_pos.x} vs 96.52"
        assert math.isclose(
            pin1_pos.y, 104.14, abs_tol=0.01
        ), f"Pin 1 Y position should match KiCad wire endpoint: {pin1_pos.y} vs 104.14"

        assert math.isclose(
            pin2_pos.x, 96.52, abs_tol=0.01
        ), f"Pin 2 X position should match KiCad wire endpoint: {pin2_pos.x} vs 96.52"
        assert math.isclose(
            pin2_pos.y, 96.52, abs_tol=0.01
        ), f"Pin 2 Y position should match KiCad wire endpoint: {pin2_pos.y} vs 96.52"

    def test_pin_rotation_90_degrees_reference(self):
        """Test 90° rotation against manual KiCad reference."""
        sch_path = (
            "tests/reference_kicad_projects/rotated_resistor_90deg/rotated_resistor_90deg.kicad_sch"
        )
        sch = ksa.Schematic.load(sch_path)

        r1 = self.get_component_by_reference(sch, "R1")
        assert r1 is not None
        assert r1.rotation == 90.0, "R1 should be at 90° rotation"

        pin1_pos = r1.get_pin_position("1")
        pin2_pos = r1.get_pin_position("2")

        # Reference wire endpoints from KiCad file:
        # Pin 1 wire connects at: (94.615, 102.235)
        # Pin 2 wire connects at: (102.235, 102.235)
        assert math.isclose(
            pin1_pos.x, 94.615, abs_tol=0.01
        ), f"Pin 1 X at 90° should match KiCad: {pin1_pos.x} vs 94.615"
        assert math.isclose(
            pin1_pos.y, 102.235, abs_tol=0.01
        ), f"Pin 1 Y at 90° should match KiCad: {pin1_pos.y} vs 102.235"

        assert math.isclose(
            pin2_pos.x, 102.235, abs_tol=0.01
        ), f"Pin 2 X at 90° should match KiCad: {pin2_pos.x} vs 102.235"
        assert math.isclose(
            pin2_pos.y, 102.235, abs_tol=0.01
        ), f"Pin 2 Y at 90° should match KiCad: {pin2_pos.y} vs 102.235"

    def test_pin_rotation_180_degrees_reference(self):
        """Test 180° rotation against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/rotated_resistor_180deg/rotated_resistor_180deg.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        r1 = self.get_component_by_reference(sch, "R1")
        assert r1 is not None
        assert r1.rotation == 180.0, "R1 should be at 180° rotation"

        pin1_pos = r1.get_pin_position("1")
        pin2_pos = r1.get_pin_position("2")

        # Reference wire endpoints from KiCad file:
        # Wires at: (100.33, 104.14) and (100.33, 96.52)
        # At 180°, pins swap positions
        assert math.isclose(pin1_pos.x, 100.33, abs_tol=0.01)
        assert math.isclose(pin2_pos.x, 100.33, abs_tol=0.01)

        # One pin at 96.52, one at 104.14
        pin_ys = sorted([pin1_pos.y, pin2_pos.y])
        assert math.isclose(
            pin_ys[0], 96.52, abs_tol=0.01
        ), f"Lower pin Y at 180° should match KiCad: {pin_ys[0]} vs 96.52"
        assert math.isclose(
            pin_ys[1], 104.14, abs_tol=0.01
        ), f"Upper pin Y at 180° should match KiCad: {pin_ys[1]} vs 104.14"

    def test_pin_rotation_270_degrees_reference(self):
        """Test 270° rotation against manual KiCad reference."""
        sch_path = "tests/reference_kicad_projects/rotated_resistor_270deg/rotated_resistor_270deg.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        r1 = self.get_component_by_reference(sch, "R1")
        assert r1 is not None
        assert r1.rotation == 270.0, "R1 should be at 270° rotation"

        pin1_pos = r1.get_pin_position("1")
        pin2_pos = r1.get_pin_position("2")

        # Reference wire endpoints from KiCad file:
        # Wires at: (102.235, 98.425) and (94.615, 98.425)
        assert math.isclose(pin1_pos.y, 98.425, abs_tol=0.01)
        assert math.isclose(pin2_pos.y, 98.425, abs_tol=0.01)

        # One pin at 94.615, one at 102.235
        pin_xs = sorted([pin1_pos.x, pin2_pos.x])
        assert math.isclose(
            pin_xs[0], 94.615, abs_tol=0.01
        ), f"Left pin X at 270° should match KiCad: {pin_xs[0]} vs 94.615"
        assert math.isclose(
            pin_xs[1], 102.235, abs_tol=0.01
        ), f"Right pin X at 270° should match KiCad: {pin_xs[1]} vs 102.235"

    @pytest.mark.parametrize(
        "rotation,sch_dir",
        [
            (0, "rotated_resistor_0deg"),
            (90, "rotated_resistor_90deg"),
            (180, "rotated_resistor_180deg"),
            (270, "rotated_resistor_270deg"),
        ],
    )
    def test_all_rotations_match_kicad_references(self, rotation, sch_dir):
        """Verify all rotations match manually created KiCad references."""
        sch_path = f"tests/reference_kicad_projects/{sch_dir}/{sch_dir}.kicad_sch"
        sch = ksa.Schematic.load(sch_path)

        r1 = self.get_component_by_reference(sch, "R1")
        assert r1 is not None, f"R1 should exist in {sch_dir}"
        assert r1.rotation == float(rotation), f"R1 should be at {rotation}° rotation"

        # Verify both pins exist and are at correct distance from component center
        pin1_pos = r1.get_pin_position("1")
        pin2_pos = r1.get_pin_position("2")

        assert pin1_pos is not None
        assert pin2_pos is not None

        # Resistor pins are 3.81mm from component center
        comp_x, comp_y = r1.position.x, r1.position.y
        dist1 = math.sqrt((pin1_pos.x - comp_x) ** 2 + (pin1_pos.y - comp_y) ** 2)
        dist2 = math.sqrt((pin2_pos.x - comp_x) ** 2 + (pin2_pos.y - comp_y) ** 2)

        assert math.isclose(
            dist1, 3.81, abs_tol=0.01
        ), f"Pin 1 distance incorrect at {rotation}°: {dist1} vs 3.81"
        assert math.isclose(
            dist2, 3.81, abs_tol=0.01
        ), f"Pin 2 distance incorrect at {rotation}°: {dist2} vs 3.81"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
