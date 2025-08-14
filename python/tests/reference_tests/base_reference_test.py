"""
Base class and utilities for reference schematic tests.

Provides common functionality for testing recreation of reference schematics.
"""

import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import pytest

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kicad_sch_api.core.schematic import Schematic


class BaseReferenceTest:
    """Base class for reference schematic recreation tests."""
    
    @pytest.fixture
    def reference_dir(self):
        """Path to reference KiCAD projects."""
        return Path(__file__).parent / "reference_kicad_projects"
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def load_reference_schematic(self, project_name: str) -> Optional[Schematic]:
        """
        Load a reference schematic by project name.
        
        Args:
            project_name: Name of reference project (e.g., 'single_resistor')
            
        Returns:
            Loaded Schematic object or None if failed
        """
        reference_dir = Path(__file__).parent / "reference_kicad_projects"
        reference_path = reference_dir / project_name / f"{project_name}.kicad_sch"
        
        if not reference_path.exists():
            pytest.skip(f"Reference file not found: {reference_path}")
            return None
        
        try:
            return Schematic.load(str(reference_path))
        except Exception as e:
            pytest.fail(f"Failed to load reference schematic {project_name}: {e}")
            return None
    
    def recreate_schematic_from_reference(self, ref_sch: Schematic, project_name: str) -> Schematic:
        """
        Recreate a schematic by copying all components from reference.
        
        Args:
            ref_sch: Reference schematic to copy from
            project_name: Name for new schematic
            
        Returns:
            Recreated schematic
        """
        recreated_sch = Schematic.create(project_name)
        
        # Copy all components exactly
        for ref_comp in ref_sch.components:
            new_comp = recreated_sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=(ref_comp.position.x, ref_comp.position.y),
                footprint=ref_comp.footprint
            )
            
            # Copy all properties
            for prop_name, prop_value in ref_comp.properties.items():
                new_comp.set_property(prop_name, prop_value)
        
        return recreated_sch
    
    def compare_schematics(self, reference: Schematic, recreated: Schematic, tolerance: float = 0.001) -> Dict:
        """
        Compare two schematics for semantic equivalence.
        
        Args:
            reference: Reference schematic
            recreated: Recreated schematic  
            tolerance: Position tolerance for floating point comparison
            
        Returns:
            Dictionary with comparison results
        """
        result = {
            'success': True,
            'component_count_match': False,
            'differences': []
        }
        
        # Compare component counts
        ref_count = len(reference.components)
        rec_count = len(recreated.components)
        result['component_count_match'] = (ref_count == rec_count)
        
        if ref_count != rec_count:
            result['differences'].append(
                f"Component count mismatch: reference={ref_count}, recreated={rec_count}"
            )
            result['success'] = False
        
        # Compare each component
        for ref_comp in reference.components:
            rec_comp = recreated.components.get(ref_comp.reference)
            
            if rec_comp is None:
                result['differences'].append(f"Missing component: {ref_comp.reference}")
                result['success'] = False
                continue
            
            # Compare component properties
            comp_diffs = self._compare_component_properties(ref_comp, rec_comp, tolerance)
            if comp_diffs:
                result['differences'].extend(comp_diffs)
                result['success'] = False
        
        return result
    
    def compare_files_exactly(self, reference_path: Path, recreated_path: Path) -> Dict:
        """
        Perform EXACT file comparison including formatting, whitespace, everything.
        
        This is the strict validation that catches ALL differences.
        """
        import difflib
        import filecmp
        
        result = {
            'files_identical': False,
            'byte_identical': False,
            'line_count_match': False,
            'diff_lines': [],
            'formatting_differences': []
        }
        
        # STRICT: Byte-for-byte comparison
        with open(reference_path, 'rb') as f:
            ref_bytes = f.read()
        
        with open(recreated_path, 'rb') as f:
            rec_bytes = f.read()
        
        result['byte_identical'] = (ref_bytes == rec_bytes)
        
        # Text-level comparison for analysis
        with open(reference_path, 'r') as f:
            ref_lines = f.readlines()
        
        with open(recreated_path, 'r') as f:
            rec_lines = f.readlines()
        
        result['line_count_match'] = (len(ref_lines) == len(rec_lines))
        result['files_identical'] = filecmp.cmp(reference_path, recreated_path, shallow=False)
        
        if not result['files_identical']:
            # Generate detailed diff
            diff = list(difflib.unified_diff(
                ref_lines,
                rec_lines,
                fromfile="reference",
                tofile="recreated",
                lineterm=''
            ))
            result['diff_lines'] = diff
            
            # Analyze formatting differences
            for line in diff:
                if line.startswith('+ ') or line.startswith('- '):
                    if '\t' in line or '  ' in line:
                        result['formatting_differences'].append(line.strip())
        
        return result
    
    def _compare_component_properties(self, ref_comp, rec_comp, tolerance: float) -> List[str]:
        """Compare properties of two components."""
        differences = []
        
        # Compare basic properties
        basic_props = [
            ('lib_id', 'Library ID'),
            ('value', 'Value'),
            ('footprint', 'Footprint')
        ]
        
        for prop_name, display_name in basic_props:
            ref_val = getattr(ref_comp, prop_name, None)
            rec_val = getattr(rec_comp, prop_name, None)
            
            if ref_val != rec_val:
                differences.append(
                    f"Component {ref_comp.reference}: {display_name} mismatch "
                    f"(expected '{ref_val}', got '{rec_val}')"
                )
        
        # Compare positions with tolerance
        if hasattr(ref_comp, 'position') and hasattr(rec_comp, 'position'):
            x_diff = abs(ref_comp.position.x - rec_comp.position.x)
            y_diff = abs(ref_comp.position.y - rec_comp.position.y)
            
            if x_diff > tolerance or y_diff > tolerance:
                differences.append(
                    f"Component {ref_comp.reference}: Position mismatch "
                    f"(expected ({ref_comp.position.x}, {ref_comp.position.y}), "
                    f"got ({rec_comp.position.x}, {rec_comp.position.y}))"
                )
        
        # Compare custom properties
        ref_props = getattr(ref_comp, 'properties', {})
        rec_props = getattr(rec_comp, 'properties', {})
        
        all_prop_keys = set(ref_props.keys()) | set(rec_props.keys())
        
        for prop_key in all_prop_keys:
            ref_val = ref_props.get(prop_key)
            rec_val = rec_props.get(prop_key)
            
            if ref_val != rec_val:
                differences.append(
                    f"Component {ref_comp.reference}: Property '{prop_key}' mismatch "
                    f"(expected '{ref_val}', got '{rec_val}')"
                )
        
        return differences
    
    def save_and_reload_schematic(self, schematic: Schematic, name: str) -> Schematic:
        """Save schematic to temp file and reload it."""
        temp_path = self.temp_path / f"{name}.kicad_sch"
        schematic.save(str(temp_path))
        return Schematic.load(str(temp_path))
    
    def assert_schematic_recreation_successful(self, project_name: str):
        """Complete test pattern for successful schematic recreation with EXACT file matching."""
        reference_dir = Path(__file__).parent / "reference_kicad_projects"
        reference_path = reference_dir / project_name / f"{project_name}.kicad_sch"
        
        if not reference_path.exists():
            pytest.skip(f"Reference file not found: {reference_path}")
        
        # Load reference
        ref_sch = self.load_reference_schematic(project_name)
        assert ref_sch is not None, f"Failed to load reference {project_name}"
        
        # Recreate schematic
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, f"{project_name}_recreated")
        
        # Save recreation
        recreated_path = self.temp_path / f"{project_name}_recreated.kicad_sch"
        recreated_sch.save(str(recreated_path))
        
        # STRICT: Compare files exactly - formatting, content, everything
        file_comparison = self.compare_files_exactly(reference_path, recreated_path)
        
        if not file_comparison['files_identical']:
            # Detailed failure analysis
            diff_summary = []
            if not file_comparison['line_count_match']:
                diff_summary.append(f"Line count differs")
            if file_comparison.get('major_differences'):
                diff_summary.append(f"{len(file_comparison['major_differences'])} major content differences")
            if file_comparison.get('formatting_differences'):
                diff_summary.append(f"{len(file_comparison['formatting_differences'])} formatting differences")
            
            # Show first few differences for debugging
            diff_preview = file_comparison['diff_lines'][:10] if file_comparison['diff_lines'] else []
            
            pytest.fail(
                f"EXACT FILE COMPARISON FAILED for {project_name}\\n"
                f"Issues: {', '.join(diff_summary)}\\n"
                f"First differences: {diff_preview}\\n"
                f"Use 'diff {reference_path} {recreated_path}' for full details"
            )
        
        return {
            'reference': ref_sch,
            'recreated': recreated_sch,
            'file_comparison': file_comparison
        }