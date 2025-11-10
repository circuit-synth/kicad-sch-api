"""
Reference tests for multi-unit component format preservation.

Tests validate that multi-unit components match exact KiCAD format
by comparing against manually created reference schematic.
"""

from pathlib import Path

import pytest

from kicad_sch_api import Schematic, create_schematic

# Path to reference schematic
REFERENCE_DIR = Path(__file__).parent.parent / "reference_kicad_projects" / "multi_unit_tl072"
REFERENCE_SCHEMATIC = REFERENCE_DIR / "test.kicad_sch"


class TestTL072ReferenceFormat:
    """Test loading TL072 reference schematic and validating format."""

    def test_load_tl072_reference(self):
        """Test loading reference schematic with 3 units of TL072."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        # Should have 3 components (3 units)
        components = list(sch.components)
        assert len(components) == 3, "Reference should have 3 units of U1"

    def test_reference_same_reference_all_units(self):
        """Test that all units have same reference 'U1'."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        references = [c.reference for c in sch.components]
        assert all(r == "U1" for r in references), "All units should have reference 'U1'"

    def test_reference_different_unit_numbers(self):
        """Test that units have different unit numbers (1, 2, 3)."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        units = sorted([c._data.unit for c in sch.components])
        assert units == [1, 2, 3], "Should have units 1, 2, 3"

    def test_reference_different_uuids(self):
        """Test that each unit has unique UUID."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        uuids = [c.uuid for c in sch.components]
        assert len(uuids) == 3
        assert len(set(uuids)) == 3, "All UUIDs should be unique"

    def test_reference_lib_id(self):
        """Test that all units have same lib_id."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        lib_ids = [c.lib_id for c in sch.components]
        assert all(lid == "Amplifier_Operational:TL072" for lid in lib_ids)

    def test_reference_value(self):
        """Test that all units have same value 'TL072'."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        values = [c.value for c in sch.components]
        assert all(v == "TL072" for v in values)

    def test_reference_positions(self):
        """Test that units have different positions."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        # Create dict of unit -> position
        positions = {c._data.unit: c.position for c in sch.components}

        # All 3 units should be present
        assert 1 in positions
        assert 2 in positions
        assert 3 in positions

        # Positions should be different
        pos_tuples = [(p.x, p.y) for p in positions.values()]
        assert len(pos_tuples) == len(set(pos_tuples)), "All positions should be unique"

    def test_reference_pin_uuids_unique_per_unit(self):
        """Test that each unit has its own unique pin UUIDs."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        # Get all pin UUIDs across all units
        all_pin_uuids = []
        for comp in sch.components:
            pin_uuids = comp.pin_uuids.values()
            all_pin_uuids.extend(pin_uuids)

        # All pin UUIDs should be unique
        assert len(all_pin_uuids) == len(set(all_pin_uuids)), "All pin UUIDs should be unique"

    def test_reference_pin_numbers_per_unit(self):
        """Test that each unit has correct pin numbers."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        # Map units to their pins
        unit_pins = {}
        for comp in sch.components:
            unit = comp._data.unit
            pins = list(comp.pin_uuids.keys())
            unit_pins[unit] = sorted(pins)

        # TL072 pin assignments:
        # Unit 1: pins 1, 2, 3 (and all 8 pins for compatibility)
        # Unit 2: pins 5, 6, 7 (and all 8 pins)
        # Unit 3: pins 4, 8 (and all 8 pins)

        # Each unit should have pins defined
        assert 1 in unit_pins
        assert 2 in unit_pins
        assert 3 in unit_pins

        # Each unit has all 8 pins in pin_uuids dict (KiCAD format)
        assert len(unit_pins[1]) == 8
        assert len(unit_pins[2]) == 8
        assert len(unit_pins[3]) == 8


class TestTL072ReferenceRoundTrip:
    """Test round-trip preservation of TL072 multi-unit format."""

    def test_roundtrip_preserves_units(self, tmp_path):
        """Test that loading and saving preserves all units."""
        # Load reference
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))
        original_count = len(sch.components)

        # Save to temp file
        temp_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(temp_file))

        # Reload
        sch2 = Schematic.load(str(temp_file))
        reloaded_count = len(sch2.components)

        # Should have same number of units
        assert reloaded_count == original_count == 3

    def test_roundtrip_preserves_references(self, tmp_path):
        """Test that round-trip preserves reference 'U1' for all units."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))
        temp_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(temp_file))

        sch2 = Schematic.load(str(temp_file))
        references = [c.reference for c in sch2.components]

        assert all(r == "U1" for r in references)

    def test_roundtrip_preserves_unit_numbers(self, tmp_path):
        """Test that round-trip preserves unit numbers."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))
        original_units = sorted([c._data.unit for c in sch.components])

        temp_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(temp_file))

        sch2 = Schematic.load(str(temp_file))
        reloaded_units = sorted([c._data.unit for c in sch2.components])

        assert reloaded_units == original_units == [1, 2, 3]

    def test_roundtrip_preserves_uuids(self, tmp_path):
        """Test that round-trip preserves all UUIDs."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))
        original_uuids = {c._data.unit: c.uuid for c in sch.components}

        temp_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(temp_file))

        sch2 = Schematic.load(str(temp_file))
        reloaded_uuids = {c._data.unit: c.uuid for c in sch2.components}

        assert reloaded_uuids == original_uuids

    def test_roundtrip_preserves_positions(self, tmp_path):
        """Test that round-trip preserves component positions."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))
        original_positions = {c._data.unit: (c.position.x, c.position.y) for c in sch.components}

        temp_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(temp_file))

        sch2 = Schematic.load(str(temp_file))
        reloaded_positions = {c._data.unit: (c.position.x, c.position.y) for c in sch2.components}

        # Compare positions with tolerance
        for unit in [1, 2, 3]:
            orig_x, orig_y = original_positions[unit]
            reload_x, reload_y = reloaded_positions[unit]

            assert reload_x == pytest.approx(orig_x, abs=0.01)
            assert reload_y == pytest.approx(orig_y, abs=0.01)

    def test_roundtrip_preserves_pin_uuids(self, tmp_path):
        """Test that round-trip preserves pin UUIDs."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))
        original_pin_uuids = {c._data.unit: c.pin_uuids.copy() for c in sch.components}

        temp_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(temp_file))

        sch2 = Schematic.load(str(temp_file))
        reloaded_pin_uuids = {c._data.unit: c.pin_uuids.copy() for c in sch2.components}

        assert reloaded_pin_uuids == original_pin_uuids


class TestProgrammaticReplication:
    """Test that we can programmatically create schematic matching reference."""

    def test_create_matching_tl072(self, tmp_path):
        """Test creating TL072 schematic that matches reference format."""
        # Create new schematic
        sch = create_schematic("test_replication")

        # Add 3 units manually (once implementation complete, use add_all_units)
        # For now, this test will fail until implementation is done

        # Load reference to get exact positions
        ref_sch = Schematic.load(str(REFERENCE_SCHEMATIC))
        ref_positions = {c._data.unit: c.position for c in ref_sch.components}

        # Add units with same positions as reference
        for unit in [1, 2, 3]:
            sch.components.add(
                "Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=ref_positions[unit],
                unit=unit,
            )

        # Save programmatically created schematic
        prog_file = tmp_path / "programmatic.kicad_sch"
        sch.save(str(prog_file))

        # Load both and compare
        prog_sch = Schematic.load(str(prog_file))

        # Should have same number of components
        assert len(prog_sch.components) == len(ref_sch.components) == 3

        # Same references
        prog_refs = sorted([c.reference for c in prog_sch.components])
        ref_refs = sorted([c.reference for c in ref_sch.components])
        assert prog_refs == ref_refs

        # Same units
        prog_units = sorted([c._data.unit for c in prog_sch.components])
        ref_units = sorted([c._data.unit for c in ref_sch.components])
        assert prog_units == ref_units


class TestInstancesSection:
    """Test that instances section is correctly formatted for multi-unit."""

    def test_instances_format(self):
        """Test that instances section contains correct reference and unit."""
        sch = Schematic.load(str(REFERENCE_SCHEMATIC))

        for comp in sch.components:
            # Each component should have instances
            assert len(comp._data.instances) > 0

            # Get first instance
            instance = comp._data.instances[0]

            # Instance reference should match component reference
            assert instance.reference == comp.reference == "U1"

            # Instance unit should match component unit
            assert instance.unit == comp._data.unit
