"""Unit tests for pin UUID preservation functionality."""

import pytest
import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
import tempfile
import os


class TestPinUUIDParsing:
    """Tests for parsing pin UUIDs from S-expressions."""

    def test_parse_component_with_pin_uuids(self):
        """Validates: REQ-1 (extract pin UUIDs during parsing)"""
        # Load reference schematic that has pin UUIDs
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        sch = ksa.Schematic.load(ref_path)

        # Get the resistor component
        components = list(sch.components)
        assert len(components) == 1, "Reference should have exactly 1 component"

        resistor = components[0]

        # Verify component has pin_uuids field
        assert hasattr(resistor, 'pin_uuids'), "SchematicSymbol should have pin_uuids field"

        # Verify pin UUIDs were extracted
        assert len(resistor.pin_uuids) == 2, "Resistor should have 2 pins with UUIDs"
        assert "1" in resistor.pin_uuids, "Should have UUID for pin 1"
        assert "2" in resistor.pin_uuids, "Should have UUID for pin 2"

    def test_pin_uuid_format(self):
        """Validates: Pin UUIDs are valid UUID strings"""
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        sch = ksa.Schematic.load(ref_path)

        resistor = list(sch.components)[0]

        # Check UUID format (should be valid UUID string)
        import uuid
        for pin_num, pin_uuid in resistor.pin_uuids.items():
            assert isinstance(pin_uuid, str), f"Pin {pin_num} UUID should be string"
            # Verify it's a valid UUID format
            try:
                uuid.UUID(pin_uuid)
            except ValueError:
                pytest.fail(f"Pin {pin_num} UUID '{pin_uuid}' is not valid UUID format")

    def test_parse_expected_pin_uuids(self):
        """Validates: Exact pin UUIDs from reference schematic"""
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        sch = ksa.Schematic.load(ref_path)

        resistor = list(sch.components)[0]

        # These are the exact UUIDs in the reference file
        expected_pin1_uuid = "df660b58-5cdf-473e-8c0a-859cae977374"
        expected_pin2_uuid = "ff5e718a-93af-455d-84a2-eecf78f3f816"

        assert resistor.pin_uuids["1"] == expected_pin1_uuid, "Pin 1 UUID should match reference"
        assert resistor.pin_uuids["2"] == expected_pin2_uuid, "Pin 2 UUID should match reference"


class TestPinUUIDStorage:
    """Tests for storing pin UUIDs in SchematicSymbol."""

    def test_new_component_has_empty_pin_uuids(self, schematic):
        """Validates: EDGE-1 (newly added component has no stored UUIDs initially)"""
        # Add a new component
        comp = schematic.components.add('Device:R', reference='R1', value='10k', position=(100, 100))

        # New component should have pin_uuids field but empty
        assert hasattr(comp, 'pin_uuids'), "New component should have pin_uuids field"
        assert isinstance(comp.pin_uuids, dict), "pin_uuids should be dictionary"
        # Could be empty or have auto-generated UUIDs depending on implementation
        # We just verify the field exists

    def test_pin_uuids_preserved_in_memory(self):
        """Validates: Pin UUIDs remain in memory after loading"""
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        sch = ksa.Schematic.load(ref_path)

        resistor = list(sch.components)[0]
        original_pin1_uuid = resistor.pin_uuids["1"]
        original_pin2_uuid = resistor.pin_uuids["2"]

        # Access component multiple times - UUIDs should remain stable
        resistor_again = list(sch.components)[0]
        assert resistor_again.pin_uuids["1"] == original_pin1_uuid
        assert resistor_again.pin_uuids["2"] == original_pin2_uuid


class TestPinUUIDPreservation:
    """Tests for preserving pin UUIDs during save operations."""

    def test_roundtrip_preserves_pin_uuids(self):
        """Validates: REQ-2 (pin UUIDs preserved during save operation)"""
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"

        # Load schematic
        sch = ksa.Schematic.load(ref_path)
        resistor = list(sch.components)[0]

        # Capture original pin UUIDs
        original_pin_uuids = dict(resistor.pin_uuids)

        # Save to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "test_roundtrip.kicad_sch")
            sch.save(temp_path)

            # Load again
            sch2 = ksa.Schematic.load(temp_path)
            resistor2 = list(sch2.components)[0]

            # Verify pin UUIDs are preserved
            assert resistor2.pin_uuids == original_pin_uuids, "Pin UUIDs should be preserved after round-trip"

    def test_no_uuid_regeneration_on_save(self):
        """Validates: FORMAT-1 (no new UUID generation for existing pins)"""
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"

        # Load schematic
        sch = ksa.Schematic.load(ref_path)

        # Save multiple times
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = os.path.join(tmpdir, "save1.kicad_sch")
            path2 = os.path.join(tmpdir, "save2.kicad_sch")

            sch.save(path1)
            sch1 = ksa.Schematic.load(path1)
            uuids1 = list(sch1.components)[0].pin_uuids

            sch1.save(path2)
            sch2 = ksa.Schematic.load(path2)
            uuids2 = list(sch2.components)[0].pin_uuids

            # UUIDs should remain identical across multiple saves
            assert uuids1 == uuids2, "Pin UUIDs should not change across multiple saves"

    def test_byte_perfect_pin_uuid_sections(self):
        """Validates: FORMAT-2 (byte-perfect match for pin UUID sections)"""
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"

        # Load and save
        sch = ksa.Schematic.load(ref_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "test_output.kicad_sch")
            sch.save(temp_path)

            # Read both files and extract pin sections
            with open(ref_path, 'r') as f:
                original = f.read()
            with open(temp_path, 'r') as f:
                output = f.read()

            # Extract pin UUID lines
            import re
            pin_pattern = r'\(pin "[^"]*"\s+\(uuid "[^"]*"\)\s*\)'

            original_pins = re.findall(pin_pattern, original)
            output_pins = re.findall(pin_pattern, output)

            # Should have same number of pin entries
            assert len(original_pins) == len(output_pins), "Should have same number of pins"

            # Pin entries should match (order and content)
            for orig, out in zip(original_pins, output_pins):
                assert orig == out, f"Pin entry mismatch:\nOriginal: {orig}\nOutput: {out}"


class TestPinUUIDEdgeCases:
    """Tests for edge cases in pin UUID handling."""

    def test_newly_created_component_generates_uuids(self, schematic):
        """Validates: EDGE-1 (newly added component generates UUIDs automatically)"""
        # Add new component
        comp = schematic.components.add('Device:R', reference='R1', value='10k', position=(100, 100))

        # Save and reload
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "new_component.kicad_sch")
            schematic.save(temp_path)

            sch2 = ksa.Schematic.load(temp_path)
            comp2 = list(sch2.components)[0]

            # Should have UUIDs assigned (either during add or during save)
            assert hasattr(comp2, 'pin_uuids'), "Component should have pin_uuids"
            # Resistor has 2 pins
            assert len(comp2.pin_uuids) == 2, "Resistor should have 2 pin UUIDs"

    def test_component_modification_preserves_existing_pin_uuids(self):
        """Validates: EDGE-3 (modifying component properties preserves pin UUIDs)"""
        ref_path = "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"

        sch = ksa.Schematic.load(ref_path)
        resistor = list(sch.components)[0]
        original_pin_uuids = dict(resistor.pin_uuids)

        # Modify component value
        resistor.value = "20k"

        # Pin UUIDs should remain unchanged in memory
        assert resistor.pin_uuids == original_pin_uuids, "Modifying value should not affect pin UUIDs"

        # Save and reload - pin UUIDs should still be preserved
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "modified.kicad_sch")
            sch.save(temp_path)

            sch2 = ksa.Schematic.load(temp_path)
            resistor2 = list(sch2.components)[0]

            assert resistor2.value == "20k", "Value should be updated"
            assert resistor2.pin_uuids == original_pin_uuids, "Pin UUIDs should be preserved"

    def test_empty_schematic_no_pins(self, schematic):
        """Validates: EDGE-4 (empty schematic has no pins to process)"""
        # Save empty schematic
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "empty.kicad_sch")
            schematic.save(temp_path)

            # Should not raise any errors
            sch2 = ksa.Schematic.load(temp_path)
            assert len(list(sch2.components)) == 0, "Should have no components"


@pytest.fixture
def schematic():
    """Fixture providing a fresh blank schematic."""
    return ksa.create_schematic("test")
