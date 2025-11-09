"""
Test hierarchical schematic instance preservation.

Tests the fix for circuit-synth #406 - ensure component instances
are preserved through save/load cycles for hierarchical schematics.
"""

import tempfile
from pathlib import Path

import pytest

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point, SymbolInstance


class TestHierarchicalInstances:
    """Test hierarchical instance path preservation."""

    def test_instances_field_exists(self):
        """Test that SchematicSymbol has instances field."""
        sch = Schematic(name="test_project")
        comp = sch.components.add("Device:R", "R1", "10k", (100, 100))

        # Should have instances field (even if empty)
        assert hasattr(comp._data, "instances")
        assert isinstance(comp._data.instances, list)

    def test_set_hierarchical_instance(self):
        """Test setting a hierarchical instance path."""
        sch = Schematic(name="test_project")
        comp = sch.components.add("Device:R", "R1", "10k", (100, 100))

        # Set hierarchical instance
        root_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        child_uuid = "11111111-2222-3333-4444-555555555555"
        hierarchical_path = f"/{root_uuid}/{child_uuid}"

        inst = SymbolInstance(path=hierarchical_path, reference="R1", unit=1)
        comp._data.instances = [inst]

        # Verify it was set
        assert len(comp._data.instances) == 1
        assert comp._data.instances[0].path == hierarchical_path
        assert comp._data.instances[0].reference == "R1"

    def test_instance_preservation_through_save(self):
        """Test that instances are preserved through save/load cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_hierarchical.kicad_sch"

            # Create schematic with hierarchical instance
            sch = Schematic(name="test_project")
            comp = sch.components.add("Device:R", "R1", "10k", (100, 100))

            # Set hierarchical path
            root_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
            child_uuid = "11111111-2222-3333-4444-555555555555"
            hierarchical_path = f"/{root_uuid}/{child_uuid}"

            inst = SymbolInstance(path=hierarchical_path, reference="R1", unit=1)
            comp._data.instances = [inst]

            # Save
            sch.save(str(output_path))

            # Reload
            reloaded = Schematic.load(str(output_path))

            # Verify component exists
            assert len(reloaded.components) == 1
            reloaded_comp = list(reloaded.components)[0]

            # Verify instances preserved
            assert hasattr(reloaded_comp._data, "instances")
            assert len(reloaded_comp._data.instances) == 1

            # THE CRITICAL TEST: Path must be preserved exactly
            assert reloaded_comp._data.instances[0].path == hierarchical_path
            assert reloaded_comp._data.instances[0].reference == "R1"
            assert reloaded_comp._data.instances[0].unit == 1

    def test_multiple_instances(self):
        """Test component with multiple instances (multi-unit symbols)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_multi_instance.kicad_sch"

            sch = Schematic(name="test_project")
            comp = sch.components.add("Device:R", "R1", "10k", (100, 100))

            # Set multiple instances
            root_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
            child_uuid1 = "11111111-2222-3333-4444-555555555555"
            child_uuid2 = "22222222-3333-4444-5555-666666666666"

            comp._data.instances = [
                SymbolInstance(path=f"/{root_uuid}/{child_uuid1}", reference="R1", unit=1),
                SymbolInstance(path=f"/{root_uuid}/{child_uuid2}", reference="R1", unit=2),
            ]

            # Save and reload
            sch.save(str(output_path))
            reloaded = Schematic.load(str(output_path))

            reloaded_comp = list(reloaded.components)[0]
            assert len(reloaded_comp._data.instances) == 2
            assert reloaded_comp._data.instances[0].path == f"/{root_uuid}/{child_uuid1}"
            assert reloaded_comp._data.instances[1].path == f"/{root_uuid}/{child_uuid2}"

    def test_backward_compatibility_no_instances(self):
        """Test that components without instances still work (backward compat)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_no_instances.kicad_sch"

            # Create component without setting instances
            sch = Schematic(name="test_project")
            comp = sch.components.add("Device:R", "R1", "10k", (100, 100))

            # Don't set instances - should get auto-generated path
            # Save and reload
            sch.save(str(output_path))
            reloaded = Schematic.load(str(output_path))

            # Should still work (parser generates default instance)
            assert len(reloaded.components) == 1
            reloaded_comp = list(reloaded.components)[0]
            assert reloaded_comp.reference == "R1"

    def test_empty_instances_list(self):
        """Test component with empty instances list."""
        sch = Schematic(name="test_project")
        comp = sch.components.add("Device:R", "R1", "10k", (100, 100))

        # Explicitly set empty list
        comp._data.instances = []

        # Should not raise error
        assert comp._data.instances == []


class TestHierarchicalPaths:
    """Test hierarchical path formats."""

    def test_simple_root_path(self):
        """Test simple root-level path (/)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_root.kicad_sch"

            sch = Schematic(name="test_project")
            comp = sch.components.add("Device:R", "R1", "10k", (100, 100))

            inst = SymbolInstance(path="/", reference="R1", unit=1)
            comp._data.instances = [inst]

            sch.save(str(output_path))
            reloaded = Schematic.load(str(output_path))

            reloaded_comp = list(reloaded.components)[0]
            assert reloaded_comp._data.instances[0].path == "/"

    def test_two_level_hierarchy(self):
        """Test two-level hierarchy: /ROOT_UUID/CHILD_UUID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_two_level.kicad_sch"

            sch = Schematic(name="test_project")
            comp = sch.components.add("Device:R", "R2", "4.7k", (100, 100))

            path = "/b0893f52-599b-414d-923c-1b56f2f78600/6c965abc-eb03-4248-b925-eaa4d33b8832"
            inst = SymbolInstance(path=path, reference="R2", unit=1)
            comp._data.instances = [inst]

            sch.save(str(output_path))
            reloaded = Schematic.load(str(output_path))

            reloaded_comp = list(reloaded.components)[0]
            assert reloaded_comp._data.instances[0].path == path

    def test_three_level_hierarchy(self):
        """Test three-level hierarchy: /ROOT/CHILD/GRANDCHILD."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_three_level.kicad_sch"

            sch = Schematic(name="test_project")
            comp = sch.components.add("Device:R", "R3", "1k", (100, 100))

            # Three-level path
            path = "/root-uuid/child-uuid/grandchild-uuid"
            inst = SymbolInstance(path=path, reference="R3", unit=1)
            comp._data.instances = [inst]

            sch.save(str(output_path))
            reloaded = Schematic.load(str(output_path))

            reloaded_comp = list(reloaded.components)[0]
            assert reloaded_comp._data.instances[0].path == path
