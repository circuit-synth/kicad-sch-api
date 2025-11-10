"""
Unit tests for multi-unit component support (Issue #107).

Tests cover:
- Adding multi-unit components with add_all_units parameter
- Manual unit-by-unit addition
- MultiUnitComponentGroup position overrides
- Reference validation (duplicate units, mismatched lib_id)
- Unit number validation
- Symbol library introspection
"""

import pytest

from kicad_sch_api import create_schematic
from kicad_sch_api.core.exceptions import LibraryError, ValidationError
from kicad_sch_api.core.types import Point, SymbolInfo


class TestMultiUnitAutomatic:
    """Test automatic multi-unit component addition with add_all_units=True."""

    def test_add_all_units_tl072(self):
        """Test adding all 3 units of TL072 with one call."""
        sch = create_schematic("test_tl072")

        # Add all units with add_all_units=True
        result = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            add_all_units=True,
        )

        # Should return MultiUnitComponentGroup
        assert result is not None
        assert hasattr(result, "get_unit")
        assert hasattr(result, "place_unit")
        assert len(result) == 3

        # Verify all 3 units added to schematic
        components = list(sch.components)
        assert len(components) == 3

        # All units should have same reference
        refs = [c.reference for c in components]
        assert all(r == "U1" for r in refs)

        # Different unit numbers
        units = sorted([c._data.unit for c in components])
        assert units == [1, 2, 3]

        # Different UUIDs
        uuids = [c.uuid for c in components]
        assert len(uuids) == len(set(uuids))  # All unique

    def test_add_all_units_default_spacing(self):
        """Test default horizontal spacing of 25.4mm (1 inch)."""
        sch = create_schematic("test_spacing")

        result = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            add_all_units=True,
            # Default unit_spacing=25.4
        )

        # Get positions of all units
        positions = result.get_all_positions()

        # Unit 1 at (100, 100)
        assert positions[1].x == pytest.approx(100, abs=0.01)
        assert positions[1].y == pytest.approx(100, abs=0.01)

        # Unit 2 at (125.4, 100) - 25.4mm to the right
        assert positions[2].x == pytest.approx(125.4, abs=0.01)
        assert positions[2].y == pytest.approx(100, abs=0.01)

        # Unit 3 at (150.8, 100) - another 25.4mm to the right
        assert positions[3].x == pytest.approx(150.8, abs=0.01)
        assert positions[3].y == pytest.approx(100, abs=0.01)

    def test_add_all_units_custom_spacing(self):
        """Test custom unit spacing."""
        sch = create_schematic("test_custom_spacing")

        result = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            add_all_units=True,
            unit_spacing=50.0,  # Custom 50mm spacing
        )

        positions = result.get_all_positions()

        # Unit 1 at (100, 100)
        assert positions[1].x == pytest.approx(100, abs=0.01)

        # Unit 2 at (150, 100)
        assert positions[2].x == pytest.approx(150, abs=0.01)

        # Unit 3 at (200, 100)
        assert positions[3].x == pytest.approx(200, abs=0.01)

    def test_add_all_units_single_unit_component(self):
        """Test add_all_units=True on single-unit component (should add just 1 unit)."""
        sch = create_schematic("test_single_unit")

        # Resistor has only 1 unit
        result = sch.components.add(
            "Device:R", reference="R1", value="10k", position=(100, 100), add_all_units=True
        )

        # Should behave like normal resistor - just 1 component
        components = list(sch.components)
        assert len(components) == 1
        assert components[0].reference == "R1"
        assert components[0]._data.unit == 1


class TestMultiUnitManual:
    """Test manual unit-by-unit addition with explicit unit parameter."""

    def test_manual_add_three_units(self):
        """Test manually adding 3 units of TL072 one-by-one."""
        sch = create_schematic("test_manual")

        # Add unit 1
        u1_1 = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            unit=1,
        )

        # Add unit 2 (same reference, different unit)
        u1_2 = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(150, 100),
            unit=2,
        )

        # Add unit 3
        u1_3 = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(125, 150),
            unit=3,
        )

        # Verify all 3 units added
        components = list(sch.components)
        assert len(components) == 3

        # Same reference
        assert all(c.reference == "U1" for c in components)

        # Different units
        units = sorted([c._data.unit for c in components])
        assert units == [1, 2, 3]

        # Different positions
        positions = [(c.position.x, c.position.y) for c in components]
        assert len(positions) == len(set(positions))  # All unique

    def test_manual_explicit_positions(self):
        """Test manual placement with exact position control."""
        sch = create_schematic("test_positions")

        # Custom positions for each unit
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=1
        )
        sch.components.add("Amplifier_Operational:TL072", "U1", "TL072", position=(175, 80), unit=2)
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(137.5, 130), unit=3
        )

        # Verify exact positions
        comps = sorted(list(sch.components), key=lambda c: c._data.unit)

        assert comps[0]._data.unit == 1
        assert comps[0].position.x == pytest.approx(100, abs=0.01)
        assert comps[0].position.y == pytest.approx(100, abs=0.01)

        assert comps[1]._data.unit == 2
        assert comps[1].position.x == pytest.approx(175, abs=0.01)
        assert comps[1].position.y == pytest.approx(80, abs=0.01)

        assert comps[2]._data.unit == 3
        assert comps[2].position.x == pytest.approx(137.5, abs=0.01)
        assert comps[2].position.y == pytest.approx(130, abs=0.01)


class TestMultiUnitComponentGroup:
    """Test MultiUnitComponentGroup position overrides."""

    def test_place_unit_override(self):
        """Test overriding unit position after auto-placement."""
        sch = create_schematic("test_override")

        group = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            add_all_units=True,
        )

        # Override unit 2 position
        group.place_unit(2, (175, 100))

        # Verify new position
        unit_2 = group.get_unit(2)
        assert unit_2.position.x == pytest.approx(175, abs=0.01)
        assert unit_2.position.y == pytest.approx(100, abs=0.01)

        # Other units unchanged
        unit_1 = group.get_unit(1)
        assert unit_1.position.x == pytest.approx(100, abs=0.01)

    def test_get_all_positions(self):
        """Test getting all unit positions."""
        sch = create_schematic("test_get_positions")

        group = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            add_all_units=True,
            unit_spacing=25.4,
        )

        positions = group.get_all_positions()

        assert len(positions) == 3
        assert 1 in positions
        assert 2 in positions
        assert 3 in positions

        assert isinstance(positions[1], Point)
        assert isinstance(positions[2], Point)
        assert isinstance(positions[3], Point)

    def test_get_unit(self):
        """Test retrieving individual units."""
        sch = create_schematic("test_get_unit")

        group = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            add_all_units=True,
        )

        # Get each unit
        unit_1 = group.get_unit(1)
        unit_2 = group.get_unit(2)
        unit_3 = group.get_unit(3)

        assert unit_1 is not None
        assert unit_2 is not None
        assert unit_3 is not None

        assert unit_1.reference == "U1"
        assert unit_2.reference == "U1"
        assert unit_3.reference == "U1"

        assert unit_1._data.unit == 1
        assert unit_2._data.unit == 2
        assert unit_3._data.unit == 3

    def test_iteration(self):
        """Test iterating over MultiUnitComponentGroup."""
        sch = create_schematic("test_iteration")

        group = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            add_all_units=True,
        )

        # Should be iterable
        units = list(group)
        assert len(units) == 3

        # All should have same reference
        assert all(u.reference == "U1" for u in units)


class TestReferenceValidation:
    """Test validation of duplicate units and mismatched lib_id."""

    def test_duplicate_unit_raises_error(self):
        """Test that adding duplicate unit raises ValidationError."""
        sch = create_schematic("test_duplicate")

        # Add U1 unit 1
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=1
        )

        # Try to add U1 unit 1 again - should fail
        with pytest.raises(ValidationError, match="Unit 1 of reference 'U1' already exists"):
            sch.components.add(
                "Amplifier_Operational:TL072", "U1", "TL072", position=(150, 100), unit=1
            )

    def test_mismatched_lib_id_raises_error(self):
        """Test that adding same reference with different lib_id raises error."""
        sch = create_schematic("test_mismatch")

        # Add U1 as TL072
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=1
        )

        # Try to add U1 unit 2 as different lib_id - should fail
        with pytest.raises(
            ValidationError, match="Reference 'U1' already exists with different lib_id"
        ):
            sch.components.add("Device:R", "U1", "10k", position=(150, 100), unit=2)

    def test_invalid_unit_number_raises_error(self):
        """Test that invalid unit number raises ValidationError."""
        sch = create_schematic("test_invalid_unit")

        # TL072 has 3 units, trying to add unit 99 should fail
        with pytest.raises(
            ValidationError, match="Unit 99 invalid for symbol 'Amplifier_Operational:TL072'"
        ):
            sch.components.add(
                "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=99
            )

    def test_unit_zero_raises_error(self):
        """Test that unit 0 raises ValidationError."""
        sch = create_schematic("test_unit_zero")

        with pytest.raises(ValidationError, match="Unit number must be >= 1"):
            sch.components.add(
                "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=0
            )

    def test_negative_unit_raises_error(self):
        """Test that negative unit number raises ValidationError."""
        sch = create_schematic("test_negative_unit")

        with pytest.raises(ValidationError, match="Unit number must be >= 1"):
            sch.components.add(
                "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=-1
            )


class TestSymbolIntrospection:
    """Test get_symbol_info() for querying unit information."""

    def test_get_symbol_info_tl072(self):
        """Test querying TL072 symbol info."""
        sch = create_schematic("test_info")

        info = sch.library.get_symbol_info("Amplifier_Operational:TL072")

        assert info is not None
        assert isinstance(info, SymbolInfo)
        assert info.lib_id == "Amplifier_Operational:TL072"
        assert info.unit_count == 3
        assert info.reference_prefix == "U"
        assert "TL072" in info.name
        assert len(info.description) > 0

    def test_get_symbol_info_single_unit(self):
        """Test querying single-unit component."""
        sch = create_schematic("test_single_info")

        info = sch.library.get_symbol_info("Device:R")

        assert info.unit_count == 1
        assert info.reference_prefix == "R"

    def test_get_symbol_info_quad_opamp(self):
        """Test querying quad op-amp (5 units)."""
        sch = create_schematic("test_quad")

        info = sch.library.get_symbol_info("Amplifier_Operational:TL074")

        assert info.unit_count == 5  # 4 op-amps + 1 power
        assert info.reference_prefix == "U"

    def test_get_symbol_info_invalid_lib_id(self):
        """Test querying non-existent symbol."""
        sch = create_schematic("test_invalid")

        with pytest.raises(LibraryError, match="Symbol .* not found"):
            sch.library.get_symbol_info("Invalid:Symbol")

    def test_programmatic_unit_addition(self):
        """Test LLM pattern: query units then add programmatically."""
        sch = create_schematic("test_programmatic")

        # Query symbol info
        info = sch.library.get_symbol_info("Amplifier_Operational:TL072")

        # Add all units programmatically
        for unit in range(1, info.unit_count + 1):
            sch.components.add(
                "Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=(100 + unit * 25.4, 100),
                unit=unit,
            )

        # Verify all units added
        components = list(sch.components)
        assert len(components) == 3
        assert all(c.reference == "U1" for c in components)


class TestBackwardCompatibility:
    """Test that existing code continues to work."""

    def test_default_unit_parameter(self):
        """Test that unit defaults to 1 if not specified."""
        sch = create_schematic("test_default")

        # Add component without explicit unit parameter
        comp = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            # unit defaults to 1
        )

        assert comp._data.unit == 1

    def test_add_all_units_defaults_to_false(self):
        """Test that add_all_units defaults to False."""
        sch = create_schematic("test_default_false")

        # Add component without add_all_units parameter
        comp = sch.components.add(
            "Amplifier_Operational:TL072",
            reference="U1",
            value="TL072",
            position=(100, 100),
            # add_all_units defaults to False
        )

        # Should only add 1 component (unit 1)
        components = list(sch.components)
        assert len(components) == 1
        assert components[0]._data.unit == 1


class TestRoundTripPreservation:
    """Test that multi-unit components preserve format through load/save cycle."""

    def test_load_save_preserves_units(self, tmp_path):
        """Test that loading and saving preserves all units."""
        sch = create_schematic("test_roundtrip")

        # Add 3 units manually
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=1
        )
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(150, 100), unit=2
        )
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(125, 150), unit=3
        )

        # Save
        filepath = tmp_path / "test.kicad_sch"
        sch.save(str(filepath))

        # Load
        sch2 = sch.load(str(filepath))

        # Verify all 3 units preserved
        components = list(sch2.components)
        assert len(components) == 3

        # Same reference
        assert all(c.reference == "U1" for c in components)

        # Units preserved
        units = sorted([c._data.unit for c in components])
        assert units == [1, 2, 3]

        # Positions preserved
        comps_by_unit = {c._data.unit: c for c in components}
        assert comps_by_unit[1].position.x == pytest.approx(100, abs=0.1)
        assert comps_by_unit[2].position.x == pytest.approx(150, abs=0.1)
        assert comps_by_unit[3].position.x == pytest.approx(125, abs=0.1)

    def test_load_save_preserves_uuids(self, tmp_path):
        """Test that UUIDs are preserved through round-trip."""
        sch = create_schematic("test_uuid_preservation")

        # Add units
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(100, 100), unit=1
        )
        sch.components.add(
            "Amplifier_Operational:TL072", "U1", "TL072", position=(150, 100), unit=2
        )

        # Capture original UUIDs
        original_uuids = {c._data.unit: c.uuid for c in sch.components}

        # Save and reload
        filepath = tmp_path / "test.kicad_sch"
        sch.save(str(filepath))
        sch2 = sch.load(str(filepath))

        # Verify UUIDs preserved
        reloaded_uuids = {c._data.unit: c.uuid for c in sch2.components}
        assert original_uuids == reloaded_uuids
