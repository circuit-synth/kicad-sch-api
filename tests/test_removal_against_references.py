#!/usr/bin/env python3
"""
Test component removal against reference schematics for exact format preservation.

This validates that removal operations produce output that exactly matches
KiCAD reference files, ensuring professional-grade format preservation.
"""

import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa


class TestRemovalAgainstReferences:
    """Test removal operations against KiCAD reference files."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "reference_tests"
        self.reference_dir = self.test_dir / "reference_kicad_projects"

    def _compare_schematics(self, generated_path: Path, reference_path: Path) -> tuple[bool, str]:
        """Compare two schematic files for exact match."""
        with open(generated_path, "r") as f:
            generated = f.read()
        with open(reference_path, "r") as f:
            reference = f.read()

        if generated == reference:
            return True, ""

        # Generate diff for debugging
        import difflib

        diff = "\n".join(
            difflib.unified_diff(
                reference.splitlines(keepends=True),
                generated.splitlines(keepends=True),
                fromfile=str(reference_path),
                tofile=str(generated_path),
            )
        )
        return False, diff

    def _normalize_for_comparison(self, content: str) -> str:
        """Normalize content for semantic comparison (ignoring UUIDs)."""
        import re

        # Remove UUIDs and other volatile elements
        normalized = re.sub(
            r'"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"', '"UUID"', content
        )
        return normalized

    def test_single_resistor_to_blank(self):
        """Test: single_resistor → remove R1 → should match blank_schematic."""
        blank_ref = self.reference_dir / "blank_schematic" / "blank_schematic.kicad_sch"
        assert blank_ref.exists(), "blank_schematic reference not found"

        # Create schematic with resistor
        sch = ksa.create_schematic("Blank Schematic")  # Use exact reference name

        # Add resistor
        resistor = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(93.98, 81.28)
        )

        # Verify resistor exists
        assert len(sch.components) == 1, "Should have 1 component"
        assert sch.components.get("R1") is not None, "R1 should exist"

        # Remove the resistor
        removed = sch.components.remove("R1")
        assert removed, "Component removal should succeed"
        assert len(sch.components) == 0, "Should have 0 components after removal"

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_path = Path(f.name)
        sch.save(temp_path)

        # Compare with blank reference
        is_identical, diff = self._compare_schematics(temp_path, blank_ref)

        if not is_identical:
            # Try semantic comparison
            with open(temp_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(blank_ref, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print("✅ Semantically equivalent to blank_schematic (UUIDs differ)")
            else:
                print("❌ Generated blank schematic differs from reference")
                print("Diff output:")
                print(diff[:2000])
                pytest.fail("Generated blank schematic differs from reference")
        else:
            print("✅ Exact match with blank_schematic reference")

        # Clean up
        temp_path.unlink()

    def test_two_resistors_remove_one_matches_single(self):
        """Test: two_resistors → remove R2 → should match single_resistor."""
        single_resistor_ref = self.reference_dir / "single_resistor" / "single_resistor.kicad_sch"
        assert single_resistor_ref.exists(), "single_resistor reference not found"

        # Create schematic with two resistors using single_resistor reference data as target
        sch = ksa.create_schematic("single_resistor")  # Target single_resistor format
        sch._data["uuid"] = "d80ef055-e33f-44b7-9702-8ce9cf922ab9"  # single_resistor UUID

        # Add R1 with single_resistor reference position and properties
        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(93.98, 81.28),  # single_resistor position
            footprint="Resistor_SMD:R_0603_1608Metric",  # single_resistor footprint
            component_uuid="a9fd95f7-6e8c-4e46-ba2c-21946a035fdb",  # single_resistor UUID
        )

        # Set additional properties to match reference
        r1.set_property("Datasheet", "~")
        r1.set_property("Description", "Resistor")

        # Add R2 (will be removed)
        r2 = sch.components.add(
            lib_id="Device:R", reference="R2", value="10k", position=(118.11, 68.58)
        )

        # Verify we have 2 components
        assert len(sch.components) == 2, "Should have 2 components before removal"

        # Remove R2
        removed = sch.components.remove("R2")
        assert removed, "R2 removal should succeed"

        # Verify we have 1 component
        assert len(sch.components) == 1, "Should have 1 component after removal"
        assert sch.components.get("R1") is not None, "R1 should still exist"
        assert sch.components.get("R2") is None, "R2 should be gone"

        # Trigger lib_symbols sync to check symbol cleanup
        sch._sync_components_to_data()

        # lib_symbols should still contain Device:R since R1 still uses it
        assert "Device:R" in str(
            sch._data.get("lib_symbols", {})
        ), "Device:R lib_symbol should remain since R1 still uses it"

        # Save and compare with single_resistor reference
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_path = Path(f.name)
        sch.save(temp_path)

        is_identical, diff = self._compare_schematics(temp_path, single_resistor_ref)

        if not is_identical:
            # Try semantic comparison (ignoring UUIDs in symbol pins)
            with open(temp_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(single_resistor_ref, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print("✅ Semantically equivalent to single_resistor (pin UUIDs differ)")
            else:
                print("❌ Generated schematic differs from single_resistor reference")
                print("Diff output:")
                print(diff[:2000])
                pytest.fail("Generated schematic differs from single_resistor reference")
        else:
            print("✅ Exact match with single_resistor reference")

        # Clean up
        temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
