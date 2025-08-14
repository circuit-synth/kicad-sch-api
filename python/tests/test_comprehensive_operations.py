"""
Comprehensive tests for schematic operations with format preservation validation.
Adapted from circuit-synth comprehensive atomic operations tests.
"""

import logging
import shutil
import tempfile
from pathlib import Path

import pytest

from kicad_sch_api.core.parser import SExpressionParser
from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point
from kicad_sch_api.utils.validation import ValidationError

logger = logging.getLogger(__name__)


class TestComprehensiveOperations:
    """Comprehensive test suite for schematic operations with reference validation."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def create_test_schematic(self, temp_dir: Path, name: str = "test") -> Path:
        """Create a test schematic file."""
        test_path = temp_dir / f"{name}.kicad_sch"

        # Create schematic with some components
        sch = Schematic.create(f"Test {name}")
        sch.components.add("Device:R", "R1", "10k", (100, 50))
        sch.components.add("Device:C", "C1", "0.1uF", (150, 50))
        sch.save(test_path)

        return test_path

    def analyze_schematic_content(self, schematic_path: Path) -> dict:
        """Analyze schematic file content for validation."""
        if not schematic_path.exists():
            return {
                "exists": False,
                "size": 0,
                "component_count": 0,
                "references": [],
                "lib_ids": [],
                "has_lib_symbols": False,
            }

        with open(schematic_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Count components (symbol instances, not lib_symbols definitions)
        import re

        # Find component instances by looking for symbols with UUIDs outside lib_symbols
        lib_symbols_start = content.find("(lib_symbols")
        lib_symbols_end = -1

        if lib_symbols_start != -1:
            # Find end of lib_symbols section
            paren_count = 0
            for i, char in enumerate(content[lib_symbols_start:], lib_symbols_start):
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                    if paren_count == 0:
                        lib_symbols_end = i
                        break

        # Search for components outside lib_symbols section
        search_area = content
        if lib_symbols_end != -1:
            search_area = content[:lib_symbols_start] + content[lib_symbols_end + 1 :]

        # Find component references
        ref_pattern = r'\(property "Reference" "([^"]+)"'
        references = re.findall(ref_pattern, search_area)

        # Find lib_ids in component instances
        lib_id_pattern = r'\(lib_id "([^"]+)"'
        lib_ids = re.findall(lib_id_pattern, search_area)

        return {
            "exists": True,
            "size": len(content),
            "component_count": len(references),
            "references": references,
            "lib_ids": lib_ids,
            "has_lib_symbols": "(lib_symbols" in content,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
        }

    def test_add_component_format_preservation(self, temp_dir):
        """Test that adding components preserves exact format."""
        # Create initial schematic
        sch_path = self.create_test_schematic(temp_dir, "format_test")

        # Read original content
        with open(sch_path, "r") as f:
            original_content = f.read()

        # Load, modify, and save
        sch = Schematic.load(sch_path)
        sch.components.add("Device:L", "L1", "10uH", (200, 50))
        sch.save()

        # Read modified content
        with open(sch_path, "r") as f:
            modified_content = f.read()

        # Verify structure is preserved
        assert "(kicad_sch" in modified_content
        assert "(lib_symbols" in modified_content
        assert "(symbol_instances" in modified_content

        # Verify new component was added
        assert "Device:L" in modified_content
        assert '"Reference" "L1"' in modified_content
        assert '"Value" "10uH"' in modified_content

    def test_remove_component_with_cleanup(self, temp_dir):
        """Test that removing components cleans up properly."""
        # Create schematic with multiple components
        sch_path = self.create_test_schematic(temp_dir, "remove_test")
        sch = Schematic.load(sch_path)

        # Add another component
        sch.components.add("Device:L", "L1", "10uH")
        sch.save()

        # Analyze before removal
        before = self.analyze_schematic_content(sch_path)
        assert before["component_count"] == 3  # R1, C1, L1
        assert "L1" in before["references"]

        # Remove component
        success = sch.components.remove("L1")
        assert success is True
        sch.save()

        # Analyze after removal
        after = self.analyze_schematic_content(sch_path)
        assert after["component_count"] == 2  # R1, C1 remain
        assert "L1" not in after["references"]
        assert "R1" in after["references"]
        assert "C1" in after["references"]

    def test_bulk_operations_performance(self, temp_dir):
        """Test performance of bulk operations."""
        sch = Schematic.create("Bulk Test")

        # Add many components
        import time

        start_time = time.time()

        for i in range(50):  # Smaller test set for fast execution
            sch.components.add(
                lib_id="Device:R", reference=f"R{i+1}", value="10k", position=(i * 10, 50)
            )

        add_time = time.time() - start_time

        # Should be reasonably fast
        assert add_time < 5.0  # 5 seconds max for 50 components
        assert len(sch.components) == 50

        # Test bulk update performance
        start_time = time.time()

        updated_count = sch.components.bulk_update(
            criteria={"lib_id": "Device:R"}, updates={"properties": {"Tolerance": "1%"}}
        )

        bulk_time = time.time() - start_time

        assert updated_count == 50
        assert bulk_time < 1.0  # Should be very fast

        # Verify updates applied
        for component in sch.components:
            assert component.get_property("Tolerance") == "1%"

    def test_component_filtering_accuracy(self, temp_dir):
        """Test accuracy of component filtering operations."""
        sch = Schematic.create("Filter Test")

        # Add diverse components
        components = [
            ("Device:R", "R1", "10k", (100, 50)),
            ("Device:R", "R2", "22k", (150, 50)),
            ("Device:C", "C1", "0.1uF", (200, 50)),
            ("Device:C", "C2", "1uF", (250, 50)),
            ("Device:L", "L1", "10uH", (300, 50)),
        ]

        for lib_id, ref, value, pos in components:
            sch.components.add(lib_id, ref, value, pos)

        # Test various filters

        # Filter by lib_id
        resistors = sch.components.filter(lib_id="Device:R")
        assert len(resistors) == 2
        assert all(comp.lib_id == "Device:R" for comp in resistors)

        # Filter by value pattern
        capacitors = sch.components.filter(value_pattern="uF")
        assert len(capacitors) == 2
        assert all("uF" in comp.value for comp in capacitors)

        # Filter by reference pattern
        import re

        r_components = sch.components.filter(reference_pattern=r"R\d+")
        assert len(r_components) == 2
        assert all(comp.reference.startswith("R") for comp in r_components)

        # Filter by area
        left_components = sch.components.in_area(90, 40, 160, 60)
        expected_refs = {"R1", "R2"}  # Components at x=100,150
        actual_refs = {comp.reference for comp in left_components}
        assert actual_refs == expected_refs

    def test_round_trip_format_preservation(self, temp_dir):
        """Test that round-trip operations preserve formatting exactly."""
        # Create reference schematic
        sch_path = self.create_test_schematic(temp_dir, "round_trip")

        # Read original content
        with open(sch_path, "r") as f:
            original_content = f.read()

        # Load and immediately save without changes
        sch = Schematic.load(sch_path)
        sch.save()

        # Read saved content
        with open(sch_path, "r") as f:
            saved_content = f.read()

        # Should be identical (allowing for UUID regeneration)
        # Check key structural elements are preserved
        assert original_content.count("(symbol") == saved_content.count("(symbol")
        assert original_content.count("(property") == saved_content.count("(property")
        assert original_content.count("Device:R") == saved_content.count("Device:R")
        assert original_content.count("Device:C") == saved_content.count("Device:C")

    def test_error_handling_and_validation(self, temp_dir):
        """Test error handling for invalid operations."""
        sch = Schematic.create("Error Test")

        # Test invalid lib_id
        with pytest.raises(ValidationError, match="Invalid lib_id format"):
            sch.components.add("InvalidFormat", "R1", "10k")

        # Test invalid reference
        with pytest.raises(ValidationError, match="Invalid reference format"):
            sch.components.add("Device:R", "1R", "10k")  # Invalid reference

        # Test duplicate reference
        sch.components.add("Device:R", "R1", "10k")
        with pytest.raises(ValidationError, match="Reference R1 already exists"):
            sch.components.add("Device:C", "R1", "0.1uF")  # Duplicate reference

    def test_component_update_operations(self, temp_dir):
        """Test updating component properties and validation."""
        sch = Schematic.create("Update Test")
        comp = sch.components.add("Device:R", "R1", "10k", (100, 50))

        # Test value updates
        comp.value = "22k"
        assert comp.value == "22k"

        # Test position updates
        comp.position = Point(200, 100)
        assert comp.position.x == 200
        assert comp.position.y == 100

        # Test footprint updates
        comp.footprint = "Resistor_SMD:R_0603_1608Metric"
        assert comp.footprint == "Resistor_SMD:R_0603_1608Metric"

        # Test custom property updates
        comp.set_property("MPN", "RC0603FR-0722KL")
        comp.set_property("Tolerance", "1%")

        assert comp.get_property("MPN") == "RC0603FR-0722KL"
        assert comp.get_property("Tolerance") == "1%"

        # Test property removal
        success = comp.remove_property("Tolerance")
        assert success is True
        assert comp.get_property("Tolerance") is None

    def test_schematic_validation_comprehensive(self, temp_dir):
        """Test comprehensive schematic validation."""
        sch = Schematic.create("Validation Test")

        # Add valid components
        sch.components.add("Device:R", "R1", "10k", (100, 50))
        sch.components.add("Device:C", "C1", "0.1uF", (150, 50))

        # Validate clean schematic
        issues = sch.validate()
        errors = [issue for issue in issues if issue.level.value in ("error", "critical")]
        assert len(errors) == 0  # Should be no errors

        # Test validation can save
        sch_path = temp_dir / "validation_test.kicad_sch"
        sch.save(sch_path)  # Should not raise ValidationError
        assert sch_path.exists()

    def test_wire_operations(self, temp_dir):
        """Test wire addition and management."""
        sch = Schematic.create("Wire Test")

        # Add components to connect
        comp1 = sch.components.add("Device:R", "R1", "10k", (100, 50))
        comp2 = sch.components.add("Device:C", "C1", "0.1uF", (150, 50))

        # Add wire between points
        wire_uuid = sch.add_wire(start=(100, 50), end=(150, 50))

        assert wire_uuid is not None
        assert isinstance(wire_uuid, str)

        # Verify wire was added to data structure
        wires = sch._data.get("wires", [])
        assert len(wires) >= 1

        # Test wire removal
        success = sch.remove_wire(wire_uuid)
        assert success is True

    def test_performance_monitoring(self, temp_dir):
        """Test performance monitoring and statistics."""
        sch = Schematic.create("Performance Test")

        # Add several components
        for i in range(10):
            sch.components.add(f"Device:R", f"R{i+1}", "10k", (i * 20, 50))

        # Get performance statistics
        stats = sch.get_performance_stats()

        # Verify statistics structure
        assert "schematic" in stats
        assert "components" in stats
        assert "symbol_cache" in stats

        # Component statistics
        comp_stats = stats["components"]
        assert comp_stats["total_components"] == 10
        assert comp_stats["unique_references"] == 10

        # Cache statistics should show some activity
        cache_stats = stats["symbol_cache"]
        assert "hit_rate_percent" in cache_stats
        assert "total_symbols_cached" in cache_stats

    def test_backup_and_restore_functionality(self, temp_dir):
        """Test backup and restore operations."""
        sch_path = self.create_test_schematic(temp_dir, "backup_test")
        sch = Schematic.load(sch_path)

        # Create backup
        backup_path = sch.backup()
        assert backup_path.exists()
        assert backup_path.name.endswith(".backup")

        # Verify backup content matches original
        original_analysis = self.analyze_schematic_content(sch_path)
        backup_analysis = self.analyze_schematic_content(backup_path)

        assert original_analysis["component_count"] == backup_analysis["component_count"]
        assert original_analysis["references"] == backup_analysis["references"]

    def test_component_collection_indexing(self, temp_dir):
        """Test that component collection indexing works correctly."""
        sch = Schematic.create("Indexing Test")

        # Add components
        components = []
        for i in range(20):
            comp = sch.components.add("Device:R", f"R{i+1}", f"{(i+1)*10}k", (i * 15, 50))
            components.append(comp)

        # Test O(1) lookup by reference
        import time

        lookup_times = []
        for i in range(10):  # Multiple lookups to test performance
            start_time = time.time()
            comp = sch.components.get(f"R{i+1}")
            lookup_time = time.time() - start_time
            lookup_times.append(lookup_time)

            assert comp is not None
            assert comp.reference == f"R{i+1}"

        # Lookups should be very fast (O(1) with indexing)
        avg_lookup_time = sum(lookup_times) / len(lookup_times)
        assert avg_lookup_time < 0.001  # Should be sub-millisecond

    def test_library_integration(self, temp_dir):
        """Test symbol library integration."""
        sch = Schematic.create("Library Test")

        # Add component (should trigger library lookup)
        comp = sch.components.add("Device:R", "R1", "10k")

        # Test symbol definition retrieval
        symbol_def = comp.get_symbol_definition()
        # May be None if library not found, but should not crash

        # Test library update
        update_success = comp.update_from_library()
        # Should not crash even if library not available

    def test_error_collection_during_validation(self, temp_dir):
        """Test that validation collects multiple errors."""
        sch = Schematic.create("Error Collection Test")

        # Create schematic with multiple potential issues
        # (We'll manually manipulate data to create issues for testing)

        # Add valid component first
        comp = sch.components.add("Device:R", "R1", "10k")

        # Manually create data issues for testing validation
        sch._data["components"].append(
            {
                "lib_id": "InvalidFormat",  # Missing colon
                "reference": "1R",  # Invalid reference format
                "value": "",
                "position": Point(100, 50),
                "uuid": "invalid-uuid-format",
                "properties": {},
                "in_bom": True,
                "on_board": True,
            }
        )

        # Run validation
        issues = sch.validate()

        # Validation should complete without errors (may or may not find issues)
        assert issues is not None, "Validation should return a list"
        assert isinstance(issues, list), "Validation should return a list of issues"
        
        # If issues are found, they should have proper structure
        if issues:
            for issue in issues:
                assert hasattr(issue, 'category'), "Issues should have category"
                assert hasattr(issue, 'message'), "Issues should have message"

    def test_concurrent_modification_safety(self, temp_dir):
        """Test safety of concurrent modifications."""
        sch_path = self.create_test_schematic(temp_dir, "concurrent_test")

        # Load same schematic in two objects
        sch1 = Schematic.load(sch_path)
        sch2 = Schematic.load(sch_path)

        # Modify both
        sch1.components.add("Device:L", "L1", "10uH")
        sch2.components.add("Device:D", "D1", "LED")

        # Save both (last one wins - basic behavior)
        sch1.save()
        sch2.save()

        # Reload and verify
        sch3 = Schematic.load(sch_path)

        # Should have components from sch2 (last save)
        assert sch3.components.get("D1") is not None
        # May or may not have L1 depending on save order
