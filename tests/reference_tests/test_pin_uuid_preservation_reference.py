"""Reference schematic validation for pin UUID preservation."""

import os
import re
import tempfile

import pytest

import kicad_sch_api as ksa


class TestPinUUIDReferenceSchematic:
    """Tests against reference schematics with pin UUIDs."""

    REFERENCE_PATHS = [
        "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch",
        "tests/reference_kicad_projects/rotated_resistor_90deg/rotated_resistor_90deg.kicad_sch",
        "tests/reference_kicad_projects/rotated_resistor_180deg/rotated_resistor_180deg.kicad_sch",
        "tests/reference_kicad_projects/rotated_resistor_270deg/rotated_resistor_270deg.kicad_sch",
    ]

    @pytest.mark.parametrize("ref_path", REFERENCE_PATHS)
    def test_parse_pin_uuids_from_reference(self, ref_path):
        """Validates: Can parse reference schematic with pin UUIDs"""
        sch = ksa.Schematic.load(ref_path)

        # Get component
        components = list(sch.components)
        assert len(components) > 0, f"Reference {ref_path} should have components"

        resistor = components[0]

        # Verify pin UUIDs were extracted
        assert hasattr(resistor, "pin_uuids"), "Component should have pin_uuids field"
        assert len(resistor.pin_uuids) == 2, "Resistor should have 2 pin UUIDs"
        assert "1" in resistor.pin_uuids, "Should have UUID for pin 1"
        assert "2" in resistor.pin_uuids, "Should have UUID for pin 2"

    @pytest.mark.format
    @pytest.mark.parametrize("ref_path", REFERENCE_PATHS)
    def test_exact_format_preservation_pin_uuids(self, ref_path):
        """Validates: FORMAT-2 (exact format preservation against reference)"""
        # Load reference
        sch = ksa.Schematic.load(ref_path)

        # Save to temp
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "test_output.kicad_sch")
            sch.save(temp_path)

            # Compare pin UUID sections
            with open(ref_path, "r") as f:
                original = f.read()
            with open(temp_path, "r") as f:
                output = f.read()

            # Extract pin sections for comparison
            original_pins = self._extract_pin_sections(original)
            output_pins = self._extract_pin_sections(output)

            # Should have same pin entries
            assert len(original_pins) == len(output_pins), f"Pin count mismatch in {ref_path}"

            # Compare each pin entry
            for i, (orig, out) in enumerate(zip(original_pins, output_pins)):
                assert (
                    orig == out
                ), f"Pin {i+1} entry mismatch in {ref_path}:\nOriginal: {orig}\nOutput: {out}"

    def test_rotated_resistor_0deg_exact_uuids(self):
        """Validates: Exact UUIDs for rotated_resistor_0deg reference"""
        ref_path = (
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )
        sch = ksa.Schematic.load(ref_path)

        resistor = list(sch.components)[0]

        # These are the exact UUIDs from the reference file
        expected_uuids = {
            "1": "df660b58-5cdf-473e-8c0a-859cae977374",
            "2": "ff5e718a-93af-455d-84a2-eecf78f3f816",
        }

        assert (
            resistor.pin_uuids == expected_uuids
        ), f"Pin UUIDs should match reference exactly: expected {expected_uuids}, got {resistor.pin_uuids}"

    def test_rotated_resistor_90deg_exact_uuids(self):
        """Validates: Exact UUIDs for rotated_resistor_90deg reference"""
        ref_path = (
            "tests/reference_kicad_projects/rotated_resistor_90deg/rotated_resistor_90deg.kicad_sch"
        )
        sch = ksa.Schematic.load(ref_path)

        resistor = list(sch.components)[0]

        # These are the exact UUIDs from the reference file (same as 0deg - rotation doesn't change UUIDs)
        expected_uuids = {
            "1": "df660b58-5cdf-473e-8c0a-859cae977374",
            "2": "ff5e718a-93af-455d-84a2-eecf78f3f816",
        }

        assert resistor.pin_uuids == expected_uuids, "Pin UUIDs should match reference exactly"

    @pytest.mark.format
    def test_roundtrip_byte_perfect_preservation(self):
        """Validates: Byte-perfect preservation on round-trip"""
        ref_path = (
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )

        # Load
        sch = ksa.Schematic.load(ref_path)

        # Save
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "roundtrip.kicad_sch")
            sch.save(temp_path)

            # Compare files
            with open(ref_path, "r") as f:
                original = f.read()
            with open(temp_path, "r") as f:
                output = f.read()

            # For pin UUID preservation, we specifically check pin sections
            # (full file might differ in other ways, but pins should match)
            original_pins = self._extract_pin_sections(original)
            output_pins = self._extract_pin_sections(output)

            assert (
                original_pins == output_pins
            ), "Pin sections should be byte-perfect after round-trip"

    def test_multiple_roundtrips_stable_uuids(self):
        """Validates: Pin UUIDs remain stable across multiple round-trips"""
        ref_path = (
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )

        # First round-trip
        sch1 = ksa.Schematic.load(ref_path)
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = os.path.join(tmpdir, "trip1.kicad_sch")
            sch1.save(path1)

            # Second round-trip
            sch2 = ksa.Schematic.load(path1)
            path2 = os.path.join(tmpdir, "trip2.kicad_sch")
            sch2.save(path2)

            # Third round-trip
            sch3 = ksa.Schematic.load(path2)
            path3 = os.path.join(tmpdir, "trip3.kicad_sch")
            sch3.save(path3)

            # Extract pin UUIDs from each
            resistor1 = list(sch1.components)[0]
            resistor2 = list(sch2.components)[0]
            resistor3 = list(sch3.components)[0]

            # All should have identical pin UUIDs
            assert (
                resistor1.pin_uuids == resistor2.pin_uuids == resistor3.pin_uuids
            ), "Pin UUIDs should remain stable across multiple round-trips"

    def _extract_pin_sections(self, content: str) -> list:
        """Extract pin sections from schematic content for comparison."""
        # Pattern matches: (pin "1" (uuid "..."))
        pin_pattern = r'\(pin\s+"[^"]*"\s+\(uuid\s+"[^"]*"\)\s*\)'
        return re.findall(pin_pattern, content)


class TestPinUUIDFormatValidation:
    """Validate pin UUID format in reference schematics."""

    def test_reference_pin_uuids_are_valid_format(self):
        """Validates: Reference schematics have valid UUID format"""
        ref_path = (
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )

        with open(ref_path, "r") as f:
            content = f.read()

        # Extract all pin UUID values
        uuid_pattern = r'\(pin\s+"[^"]*"\s+\(uuid\s+"([^"]*)"\)'
        pin_uuids = re.findall(uuid_pattern, content)

        assert len(pin_uuids) > 0, "Reference should have pin UUIDs"

        # Validate each UUID format
        import uuid

        for pin_uuid in pin_uuids:
            try:
                uuid.UUID(pin_uuid)
            except ValueError:
                pytest.fail(f"Invalid UUID format in reference: {pin_uuid}")

    def test_pin_uuids_unique_within_component(self):
        """Validates: Each pin has unique UUID within component"""
        ref_path = (
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )
        sch = ksa.Schematic.load(ref_path)

        resistor = list(sch.components)[0]

        # All pin UUIDs should be unique
        uuid_values = list(resistor.pin_uuids.values())
        assert len(uuid_values) == len(
            set(uuid_values)
        ), "Pin UUIDs should be unique within component"
