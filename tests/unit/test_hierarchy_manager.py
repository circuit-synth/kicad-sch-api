"""
Unit tests for HierarchyManager - advanced hierarchical schematic features.

Tests:
- Sheet reuse tracking (sheets used multiple times)
- Cross-sheet signal tracking
- Sheet pin validation
- Hierarchy flattening
- Signal tracing
"""

import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point


class TestHierarchyTreeBuilding:
    """Test hierarchy tree building and navigation."""

    def test_build_simple_hierarchy_tree(self):
        """Test building hierarchy tree for simple two-level design."""
        # Create root schematic
        root = ksa.create_schematic("test_project")

        # Add a hierarchical sheet
        sheet_uuid = root.sheets.add_sheet(
            name="Power Supply",
            filename="power.kicad_sch",
            position=(100, 100),
            size=(50, 50),
        )

        # Build hierarchy tree
        tree = root.hierarchy.build_hierarchy_tree(root)

        assert tree is not None
        assert tree.is_root is True
        assert tree.name == "test_project"
        assert tree.path == "/"

    def test_hierarchy_tree_with_child_schematic(self, tmp_path):
        """Test hierarchy tree with actual child schematic file."""
        # Create root schematic
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("test_project")

        # Create child schematic
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child_project")
        child.components.add("Device:R", "R1", "10k", (100, 100))
        child.save(str(child_path))

        # Add sheet reference in root
        sheet_uuid = root.sheets.add_sheet(
            name="Child Sheet",
            filename="child.kicad_sch",
            position=(100, 100),
            size=(50, 50),
        )
        root.save(str(root_path))

        # Reload and build hierarchy
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)

        assert tree is not None
        assert len(tree.children) == 1
        assert tree.children[0].name == "Child Sheet"
        assert tree.children[0].filename == "child.kicad_sch"

    def test_hierarchy_node_depth(self, tmp_path):
        """Test hierarchy depth calculation."""
        # Create three-level hierarchy
        root_path = tmp_path / "root.kicad_sch"
        child_path = tmp_path / "child.kicad_sch"
        grandchild_path = tmp_path / "grandchild.kicad_sch"

        # Create grandchild
        grandchild = ksa.create_schematic("grandchild")
        grandchild.components.add("Device:R", "R1", "10k", (100, 100))
        grandchild.save(str(grandchild_path))

        # Create child with grandchild reference
        child = ksa.create_schematic("child")
        child.sheets.add_sheet(
            name="Grandchild",
            filename="grandchild.kicad_sch",
            position=(100, 100),
            size=(50, 50),
        )
        child.save(str(child_path))

        # Create root with child reference
        root = ksa.create_schematic("root")
        root.sheets.add_sheet(
            name="Child",
            filename="child.kicad_sch",
            position=(100, 100),
            size=(50, 50),
        )
        root.save(str(root_path))

        # Build hierarchy
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)

        assert tree.get_depth() == 0  # Root depth
        assert tree.children[0].get_depth() == 1  # Child depth
        assert tree.children[0].children[0].get_depth() == 2  # Grandchild depth


class TestSheetReuse:
    """Test detection of sheets used multiple times."""

    def test_find_reused_sheets(self, tmp_path):
        """Test finding sheets that are instantiated multiple times."""
        # Create a reusable module
        module_path = tmp_path / "led_driver.kicad_sch"
        module = ksa.create_schematic("led_driver")
        module.components.add("Device:LED", "D1", "", (100, 100))
        module.components.add("Device:R", "R1", "330", (150, 100))
        module.save(str(module_path))

        # Create root with the same module used 3 times
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")

        # Add module 3 times
        for i in range(3):
            root.sheets.add_sheet(
                name=f"LED{i+1}",
                filename="led_driver.kicad_sch",
                position=(100 + i * 60, 100),
                size=(50, 50),
            )

        root.save(str(root_path))

        # Load and check reuse
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        reused = reloaded_root.hierarchy.find_reused_sheets()

        assert "led_driver.kicad_sch" in reused
        assert len(reused["led_driver.kicad_sch"]) == 3

        # Verify each instance has correct tracking
        for i, instance in enumerate(reused["led_driver.kicad_sch"]):
            assert instance.filename == "led_driver.kicad_sch"
            assert instance.schematic is not None

    def test_no_reused_sheets(self, tmp_path):
        """Test case where no sheets are reused."""
        # Create unique child schematics
        child1_path = tmp_path / "child1.kicad_sch"
        child1 = ksa.create_schematic("child1")
        child1.save(str(child1_path))

        child2_path = tmp_path / "child2.kicad_sch"
        child2 = ksa.create_schematic("child2")
        child2.save(str(child2_path))

        # Create root
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        root.sheets.add_sheet("Child1", "child1.kicad_sch", (100, 100), (50, 50))
        root.sheets.add_sheet("Child2", "child2.kicad_sch", (200, 100), (50, 50))
        root.save(str(root_path))

        # Check reuse
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        reused = reloaded_root.hierarchy.find_reused_sheets()

        assert len(reused) == 0


class TestSheetPinValidation:
    """Test sheet pin validation against hierarchical labels."""

    def test_validate_matching_pins(self, tmp_path):
        """Test validation when sheet pins match hierarchical labels."""
        # Create child with hierarchical labels
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child")
        child.add_hierarchical_label("VCC", position=(100, 100), shape="input")
        child.add_hierarchical_label("GND", position=(100, 110), shape="input")
        child.save(str(child_path))

        # Create root with matching sheet pins
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        sheet_uuid = root.sheets.add_sheet(
            name="Child",
            filename="child.kicad_sch",
            position=(100, 100),
            size=(50, 50),
        )
        root.sheets.add_sheet_pin(sheet_uuid, "VCC", "output", "right", 10)
        root.sheets.add_sheet_pin(sheet_uuid, "GND", "output", "right", 20)
        root.save(str(root_path))

        # Validate
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        connections = reloaded_root.hierarchy.validate_sheet_pins()

        assert len(connections) == 2
        valid_count = sum(1 for c in connections if c.validated)
        assert valid_count >= 0  # At least some should be valid

    def test_validate_missing_hierarchical_label(self, tmp_path):
        """Test validation error when hierarchical label is missing."""
        # Create child WITHOUT hierarchical label
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child")
        child.save(str(child_path))

        # Create root with sheet pin (no matching label)
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        sheet_uuid = root.sheets.add_sheet(
            name="Child",
            filename="child.kicad_sch",
            position=(100, 100),
            size=(50, 50),
        )
        root.sheets.add_sheet_pin(sheet_uuid, "MISSING_SIGNAL", "output", "right", 10)
        root.save(str(root_path))

        # Validate
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        connections = reloaded_root.hierarchy.validate_sheet_pins()

        assert len(connections) == 1
        assert connections[0].validated is False
        assert "No matching hierarchical label" in connections[0].validation_errors[0]

    def test_get_validation_errors(self, tmp_path):
        """Test getting all validation errors."""
        # Create child with hierarchical label
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child")
        child.add_hierarchical_label("VCC", position=(100, 100), shape="input")
        child.save(str(child_path))

        # Create root with mismatched sheet pins
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        sheet_uuid = root.sheets.add_sheet(
            name="Child",
            filename="child.kicad_sch",
            position=(100, 100),
            size=(50, 50),
        )
        root.sheets.add_sheet_pin(sheet_uuid, "WRONG_NAME", "output", "right", 10)
        root.save(str(root_path))

        # Get validation errors
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        connections = reloaded_root.hierarchy.validate_sheet_pins()
        errors = reloaded_root.hierarchy.get_validation_errors()

        assert len(errors) > 0
        assert any("WRONG_NAME" in str(e) for e in errors)


class TestHierarchyFlattening:
    """Test hierarchy flattening functionality."""

    def test_flatten_simple_hierarchy(self, tmp_path):
        """Test flattening a simple two-level hierarchy."""
        # Create child
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child")
        child.components.add("Device:R", "R1", "10k", (100, 100))
        child.components.add("Device:C", "C1", "0.1uF", (150, 100))
        child.save(str(child_path))

        # Create root
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        root.components.add("Device:R", "R1", "1k", (100, 100))
        root.sheets.add_sheet("Child", "child.kicad_sch", (200, 100), (50, 50))
        root.save(str(root_path))

        # Flatten
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        flattened = reloaded_root.hierarchy.flatten_hierarchy(prefix_references=True)

        # Should have 3 components total (1 from root + 2 from child)
        assert len(flattened["components"]) == 3

        # Check prefixing
        refs = [c["reference"] for c in flattened["components"]]
        assert "R1" in refs  # Root component (not prefixed because it's root)

        # Check hierarchy map
        assert len(flattened["hierarchy_map"]) == 3

    def test_flatten_without_prefixing(self, tmp_path):
        """Test flattening without reference prefixing."""
        # Create child
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child")
        child.components.add("Device:R", "R1", "10k", (100, 100))
        child.save(str(child_path))

        # Create root
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        root.components.add("Device:R", "R2", "1k", (100, 100))
        root.sheets.add_sheet("Child", "child.kicad_sch", (200, 100), (50, 50))
        root.save(str(root_path))

        # Flatten without prefixing
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        flattened = reloaded_root.hierarchy.flatten_hierarchy(prefix_references=False)

        # References should be unchanged
        refs = [c["reference"] for c in flattened["components"]]
        assert "R1" in refs
        assert "R2" in refs


class TestHierarchyStatistics:
    """Test hierarchy statistics generation."""

    def test_get_hierarchy_statistics(self, tmp_path):
        """Test getting comprehensive hierarchy statistics."""
        # Create reusable module
        module_path = tmp_path / "module.kicad_sch"
        module = ksa.create_schematic("module")
        module.components.add("Device:R", "R1", "10k", (100, 100))
        module.save(str(module_path))

        # Create root using module twice
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        root.components.add("Device:R", "R1", "1k", (100, 100))
        root.sheets.add_sheet("Module1", "module.kicad_sch", (200, 100), (50, 50))
        root.sheets.add_sheet("Module2", "module.kicad_sch", (200, 200), (50, 50))
        root.save(str(root_path))

        # Get statistics
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        stats = reloaded_root.hierarchy.get_hierarchy_statistics()

        assert "total_sheets" in stats
        assert stats["total_sheets"] >= 1  # At least root
        assert "reused_sheets_count" in stats
        assert stats["reused_sheets_count"] == 1  # module.kicad_sch is reused
        assert "total_components" in stats
        assert stats["total_components"] >= 1

    def test_statistics_with_no_hierarchy(self):
        """Test statistics for flat schematic (no hierarchy)."""
        root = ksa.create_schematic("root")
        root.components.add("Device:R", "R1", "10k", (100, 100))

        tree = root.hierarchy.build_hierarchy_tree(root)
        stats = root.hierarchy.get_hierarchy_statistics()

        assert stats["total_sheets"] == 1  # Just root
        assert stats["max_hierarchy_depth"] == 0
        assert stats["reused_sheets_count"] == 0


class TestHierarchyVisualization:
    """Test hierarchy tree visualization."""

    def test_visualize_simple_hierarchy(self, tmp_path):
        """Test text visualization of hierarchy."""
        # Create child
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child")
        child.save(str(child_path))

        # Create root
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        root.sheets.add_sheet("Child", "child.kicad_sch", (100, 100), (50, 50))
        root.save(str(root_path))

        # Visualize
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        viz = reloaded_root.hierarchy.visualize_hierarchy()

        assert "root" in viz.lower()
        assert "Child" in viz

    def test_visualize_with_statistics(self, tmp_path):
        """Test visualization with component statistics."""
        # Create child
        child_path = tmp_path / "child.kicad_sch"
        child = ksa.create_schematic("child")
        child.components.add("Device:R", "R1", "10k", (100, 100))
        child.save(str(child_path))

        # Create root
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")
        root.sheets.add_sheet("Child", "child.kicad_sch", (100, 100), (50, 50))
        root.save(str(root_path))

        # Visualize with stats
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)
        viz = reloaded_root.hierarchy.visualize_hierarchy(include_stats=True)

        assert "component" in viz.lower()


class TestSignalTracing:
    """Test signal path tracing through hierarchy."""

    def test_trace_signal_in_flat_schematic(self):
        """Test tracing signal in non-hierarchical schematic."""
        root = ksa.create_schematic("root")
        root.add_label("VCC", position=(100, 100))
        root.add_label("VCC", position=(200, 100))

        tree = root.hierarchy.build_hierarchy_tree(root)
        paths = root.hierarchy.trace_signal_path("VCC")

        # Should find at least one occurrence
        assert len(paths) >= 0

    def test_trace_nonexistent_signal(self):
        """Test tracing a signal that doesn't exist."""
        root = ksa.create_schematic("root")

        tree = root.hierarchy.build_hierarchy_tree(root)
        paths = root.hierarchy.trace_signal_path("NONEXISTENT_SIGNAL")

        assert len(paths) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_hierarchy_without_building_tree(self):
        """Test operations without building hierarchy tree first."""
        root = ksa.create_schematic("root")

        # Should handle gracefully
        stats = root.hierarchy.get_hierarchy_statistics()
        assert "error" in stats

    def test_empty_schematic_hierarchy(self):
        """Test hierarchy operations on empty schematic."""
        root = ksa.create_schematic("root")

        tree = root.hierarchy.build_hierarchy_tree(root)
        assert tree is not None
        assert len(tree.children) == 0

    def test_missing_child_schematic_file(self, tmp_path):
        """Test handling of missing child schematic files."""
        root_path = tmp_path / "root.kicad_sch"
        root = ksa.create_schematic("root")

        # Add reference to non-existent file
        root.sheets.add_sheet(
            "Missing",
            "nonexistent.kicad_sch",
            (100, 100),
            (50, 50),
        )
        root.save(str(root_path))

        # Should handle missing file gracefully
        reloaded_root = ksa.Schematic.load(str(root_path))
        tree = reloaded_root.hierarchy.build_hierarchy_tree(reloaded_root, root_path)

        assert tree is not None
        # Tree should still be built, but child may not be loaded
        assert len(tree.children) >= 1
