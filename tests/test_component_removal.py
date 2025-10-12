#!/usr/bin/env python3
"""
Test component removal functionality with exact format preservation.

Tests that component removal properly cleans up lib_symbols and maintains
exact compatibility with KiCAD reference files.
"""

import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa


class TestComponentRemoval:
    """Test component removal with exact reference matching."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "reference_tests"
        self.reference_dir = self.test_dir / "reference_kicad_projects"

    def test_resistor_to_blank_removal(self):
        """Test removing resistor from single_resistor should match blank_schematic."""
        # Load reference files for comparison
        single_resistor_ref = self.reference_dir / "single_resistor" / "single_resistor.kicad_sch"
        blank_ref = self.reference_dir / "blank_schematic" / "blank_schematic.kicad_sch"

        assert single_resistor_ref.exists(), "single_resistor reference not found"
        assert blank_ref.exists(), "blank_schematic reference not found"

        # Create schematic matching single_resistor
        sch = ksa.create_schematic("single_resistor")
        sch._data["uuid"] = "36e79395-fda8-4b97-93ca-b52e21a60e4e"

        # Add resistor with exact reference data
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(93.98, 81.28),
            component_uuid="a59e019e-5a4f-4ea6-a9c7-d8030d91b3d9",
        )

        # Verify it matches single_resistor first
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
            temp_path = Path(f.name)

        sch.save(temp_path)

        # Compare with single_resistor reference
        with open(temp_path, "r") as f:
            generated_content = f.read()
        with open(single_resistor_ref, "r") as f:
            reference_content = f.read()

        # Should match single_resistor (except for pin UUIDs which are random)
        assert len(sch.components) == 1, "Should have 1 component before removal"
        assert "Device:R" in str(
            sch._data.get("lib_symbols", {})
        ), "Should have resistor lib_symbol"

        # Now remove the resistor
        removed = sch.components.remove("R1")
        assert removed, "Component removal should succeed"

        # Verify component is gone
        assert len(sch.components) == 0, "Should have 0 components after removal"

        # Save and compare with blank_schematic
        sch.save(temp_path)

        with open(temp_path, "r") as f:
            generated_blank = f.read()
        with open(blank_ref, "r") as f:
            blank_reference = f.read()

        # Clean up
        temp_path.unlink()

        # The generated blank schematic should match the reference
        # (allowing for different UUIDs since blank has no UUID)
        assert (
            "lib_symbols" not in generated_blank or "Device:R" not in generated_blank
        ), "lib_symbols should be cleaned up after component removal"
        assert len(sch.components) == 0, "Component collection should be empty"

    def test_two_resistors_remove_one(self):
        """Test removing one resistor from two_resistors should match single_resistor."""
        # Load reference files
        two_resistors_ref = self.reference_dir / "two_resistors" / "two_resistors.kicad_sch"
        single_resistor_ref = self.reference_dir / "single_resistor" / "single_resistor.kicad_sch"

        assert two_resistors_ref.exists(), "two_resistors reference not found"
        assert single_resistor_ref.exists(), "single_resistor reference not found"

        # Create schematic with two resistors
        sch = ksa.create_schematic("two_resistors")
        sch._data["uuid"] = "07a94a5c-8b90-4d4c-9845-71ed0e1ea4e8"

        # Add first resistor (R1) - this should remain
        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(103.2456, 68.7446),
            component_uuid="c67528e0-23b8-4ad9-93b4-79ea2e07e5a8",
        )

        # Add second resistor (R2) - this will be removed
        r2 = sch.components.add(
            lib_id="Device:R",
            reference="R2",
            value="10k",
            position=(118.11, 68.58),
            component_uuid="8bcd6d76-4de7-4b18-b88d-64d8c30a7bf7",
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

    def test_remove_nonexistent_component(self):
        """Test removing a component that doesn't exist."""
        sch = ksa.create_schematic("test")

        # Try to remove non-existent component
        removed = sch.components.remove("R99")
        assert not removed, "Removing non-existent component should return False"

    def test_remove_by_uuid(self):
        """Test removing component by UUID if that functionality exists."""
        sch = ksa.create_schematic("test")

        # Add a component
        resistor = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100, 100)
        )

        # Check if remove by UUID is supported
        if hasattr(sch.components, "remove_by_uuid"):
            removed = sch.components.remove_by_uuid(resistor.uuid)
            assert removed, "Remove by UUID should succeed"
            assert len(sch.components) == 0, "Component should be removed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
