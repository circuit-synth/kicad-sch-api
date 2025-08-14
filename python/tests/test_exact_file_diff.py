"""
Exact File Diff Tests - Strict Validation

These tests perform direct file comparison between generated and reference
schematics to catch ANY differences in content, format, or structure.

This testing approach would have immediately caught the lib_symbols issue.
"""

import filecmp
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from kicad_sch_api.core.schematic import Schematic


class TestExactFileDiff:
    """Strict file-level validation tests."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.reference_dir = Path(__file__).parent / "reference_tests" / "reference_kicad_projects"
    
    def load_reference_and_recreate(self, project_name: str):
        """Load reference and recreate exactly."""
        reference_path = self.reference_dir / project_name / f"{project_name}.kicad_sch"
        
        if not reference_path.exists():
            pytest.skip(f"Reference file not found: {reference_path}")
        
        # Load reference
        ref_sch = Schematic.load(str(reference_path))
        
        # Recreate exactly
        rec_sch = Schematic.create(project_name)
        for ref_comp in ref_sch.components:
            new_comp = rec_sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=(ref_comp.position.x, ref_comp.position.y),
                footprint=ref_comp.footprint
            )
            # Copy all properties
            for prop_name, prop_value in ref_comp.properties.items():
                new_comp.set_property(prop_name, prop_value)
        
        # Save recreation
        recreated_path = self.temp_path / f"{project_name}_recreated.kicad_sch"
        rec_sch.save(str(recreated_path))
        
        return reference_path, recreated_path
    
    def compare_files_with_diff(self, reference_path: Path, recreated_path: Path):
        """Perform detailed file comparison with diff output."""
        import difflib
        
        with open(reference_path, 'r') as f:
            ref_lines = f.readlines()
        
        with open(recreated_path, 'r') as f:
            rec_lines = f.readlines()
        
        # Generate diff
        diff = list(difflib.unified_diff(
            ref_lines,
            rec_lines,
            fromfile=f"reference/{reference_path.name}",
            tofile=f"recreated/{recreated_path.name}",
            lineterm=''
        ))
        
        return {
            'identical': len(diff) == 0,
            'diff_lines': diff,
            'ref_line_count': len(ref_lines),
            'rec_line_count': len(rec_lines),
            'line_count_diff': abs(len(ref_lines) - len(rec_lines))
        }
    
    def test_single_resistor_exact_file_match(self):
        """Test that single resistor recreation matches reference file exactly."""
        ref_path, rec_path = self.load_reference_and_recreate("single_resistor")
        
        # Perform detailed comparison
        comparison = self.compare_files_with_diff(ref_path, rec_path)
        
        # Report differences
        if not comparison['identical']:
            print(f"\n❌ Files are NOT identical!")
            print(f"Reference lines: {comparison['ref_line_count']}")
            print(f"Recreated lines: {comparison['rec_line_count']}")
            print(f"Line count difference: {comparison['line_count_diff']}")
            
            print(f"\n📋 First 20 differences:")
            for i, line in enumerate(comparison['diff_lines'][:20]):
                print(f"  {line.rstrip()}")
            
            if len(comparison['diff_lines']) > 20:
                print(f"  ... and {len(comparison['diff_lines']) - 20} more differences")
        
        # STRICT REQUIREMENT: Files must be identical
        assert comparison['identical'], f"Files are not identical - {len(comparison['diff_lines'])} differences found"
    
    def test_blank_schematic_exact_file_match(self):
        """Test that blank schematic recreation matches reference file exactly."""
        ref_path, rec_path = self.load_reference_and_recreate("blank_schematic")
        
        comparison = self.compare_files_with_diff(ref_path, rec_path)
        
        if not comparison['identical']:
            print(f"\n❌ Blank schematic files differ!")
            print(f"Differences: {len(comparison['diff_lines'])}")
            for line in comparison['diff_lines'][:10]:
                print(f"  {line.rstrip()}")
        
        # Blank schematics should be nearly identical
        assert comparison['identical'], "Blank schematic recreation must be identical"
    
    def test_two_resistors_exact_file_match(self):
        """Test that two resistors recreation matches reference file exactly."""
        ref_path, rec_path = self.load_reference_and_recreate("two_resistors")
        
        comparison = self.compare_files_with_diff(ref_path, rec_path)
        
        if not comparison['identical']:
            print(f"\n❌ Two resistors files differ!")
            print(f"Reference: {comparison['ref_line_count']} lines")
            print(f"Recreated: {comparison['rec_line_count']} lines")
            print(f"First few differences:")
            for line in comparison['diff_lines'][:15]:
                print(f"  {line.rstrip()}")
        
        # STRICT: Must be identical
        assert comparison['identical'], f"Two resistors recreation must be identical"
    
    def test_file_diff_detects_lib_symbols_differences(self):
        """Test that file diff catches lib_symbols content differences."""
        # Create two schematics - one with proper lib_symbols, one without
        sch1 = Schematic.create("Test 1")
        sch1.components.add('Device:R', reference='R1', value='10k')
        
        sch2 = Schematic.create("Test 2") 
        sch2.components.add('Device:R', reference='R1', value='10k')
        # Manually break lib_symbols to simulate the bug
        sch2._data['lib_symbols'] = {}
        
        # Save both
        path1 = self.temp_path / "test1.kicad_sch"
        path2 = self.temp_path / "test2.kicad_sch"
        
        sch1.save(str(path1))
        sch2.save(str(path2))
        
        # Compare files
        comparison = self.compare_files_with_diff(path1, path2)
        
        # These files SHOULD be different (one has lib_symbols, one doesn't)
        assert not comparison['identical'], "Files with different lib_symbols should NOT be identical"
        
        # Should detect significant line count difference
        assert comparison['line_count_diff'] > 10, f"Should detect major difference, got {comparison['line_count_diff']} lines"
        
        print(f"✅ File diff correctly detected lib_symbols difference:")
        print(f"  Line count difference: {comparison['line_count_diff']}")
        print(f"  Total differences: {len(comparison['diff_lines'])}")
    
    @pytest.mark.parametrize("project_name", [
        "blank_schematic",
        "single_resistor", 
        "two_resistors"
    ])
    def test_strict_file_comparison_all_references(self, project_name):
        """Strict file comparison for all reference projects."""
        ref_path, rec_path = self.load_reference_and_recreate(project_name)
        
        # Use Python's filecmp for exact comparison
        files_identical = filecmp.cmp(ref_path, rec_path, shallow=False)
        
        if not files_identical:
            # Generate detailed diff for debugging
            comparison = self.compare_files_with_diff(ref_path, rec_path)
            
            # Provide detailed failure information
            pytest.fail(
                f"{project_name} recreation not identical to reference.\n"
                f"Reference: {comparison['ref_line_count']} lines\n"
                f"Recreated: {comparison['rec_line_count']} lines\n"
                f"Differences: {len(comparison['diff_lines'])}\n"
                f"Use 'diff {ref_path} {rec_path}' for details."
            )
        
        print(f"✅ {project_name}: Perfect file-level match")


class TestFileDiffFailureDetection:
    """Tests that demonstrate how file diff would catch issues."""
    
    def test_file_diff_would_catch_missing_lib_symbols(self):
        """Demonstrate that file diff would have caught the lib_symbols bug."""
        
        # Create a schematic the OLD way (without proper lib_symbols)
        import tempfile
        
        # Write a schematic with empty lib_symbols (simulating the bug)
        old_buggy_content = """(kicad_sch
	(version 20230121)
	(generator "kicad-sch-api")
	(uuid "test-uuid")
	(lib_symbols)
	(symbol
		(lib_id "Device:R")
		(at 100 100 0)
		(uuid "comp-uuid")
		(property "Reference" "R1")
		(property "Value" "10k")
		(in_bom yes)
		(on_board yes))
	(symbol_instances))"""
        
        # Create a proper schematic with our current implementation
        sch = Schematic.create("Proper Test")
        sch.components.add('Device:R', reference='R1', value='10k', position=(100, 100))
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kicad_sch', delete=False) as f:
            f.write(old_buggy_content)
            buggy_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            proper_path = f.name
        
        sch.save(proper_path)
        
        # File comparison should detect the difference
        files_identical = filecmp.cmp(buggy_path, proper_path, shallow=False)
        
        # Clean up
        Path(buggy_path).unlink()
        Path(proper_path).unlink()
        
        # This should be False - files should be different
        assert not files_identical, "File diff should detect lib_symbols differences"
        
        print("✅ File diff correctly detects lib_symbols content differences")
        print("✅ This test would have caught the original bug immediately")