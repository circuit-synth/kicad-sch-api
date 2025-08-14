"""
Advanced schematic comparison utilities for testing.

Provides detailed comparison functionality for validating that recreated
schematics match reference files both semantically and at the file level.
"""

import difflib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kicad_sch_api.core.schematic import Schematic

# Create convenience module-like access
class KSAModule:
    @staticmethod
    def load_schematic(path):
        return Schematic.load(path)

ksa = KSAModule()


class SchematicComparator:
    """Advanced schematic comparison with detailed analysis."""
    
    def __init__(self, tolerance: float = 0.001):
        """
        Initialize comparator.
        
        Args:
            tolerance: Floating point tolerance for position comparisons
        """
        self.tolerance = tolerance
        
    def compare_schematics(
        self, 
        reference_path: Union[str, Path], 
        recreated_path: Union[str, Path],
        include_file_diff: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive comparison between reference and recreated schematics.
        
        Args:
            reference_path: Path to reference .kicad_sch file
            recreated_path: Path to recreated .kicad_sch file
            include_file_diff: Whether to include text-level file differences
            
        Returns:
            Detailed comparison results dictionary
        """
        reference_path = Path(reference_path)
        recreated_path = Path(recreated_path)
        
        if not reference_path.exists():
            raise FileNotFoundError(f"Reference file not found: {reference_path}")
        if not recreated_path.exists():
            raise FileNotFoundError(f"Recreated file not found: {recreated_path}")
        
        # Load both schematics
        try:
            ref_sch = ksa.load_schematic(str(reference_path))
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to load reference schematic: {e}",
                'reference_path': str(reference_path),
                'recreated_path': str(recreated_path)
            }
        
        try:
            rec_sch = ksa.load_schematic(str(recreated_path))
        except Exception as e:
            return {
                'success': False, 
                'error': f"Failed to load recreated schematic: {e}",
                'reference_path': str(reference_path),
                'recreated_path': str(recreated_path)
            }
        
        # Perform comprehensive comparison
        result = {
            'success': True,
            'reference_path': str(reference_path),
            'recreated_path': str(recreated_path),
            'semantic_match': True,
            'exact_file_match': False,
            'summary': {},
            'components': {},
            'wires': {},
            'labels': {},
            'differences': [],
            'statistics': {}
        }
        
        # Compare components
        component_result = self._compare_components(ref_sch, rec_sch)
        result['components'] = component_result
        if not component_result['match']:
            result['semantic_match'] = False
        
        # Compare file-level differences if requested
        if include_file_diff:
            file_diff = self._compare_files(reference_path, recreated_path)
            result['file_comparison'] = file_diff
            result['exact_file_match'] = file_diff['identical']
        
        # Generate summary statistics
        result['summary'] = {
            'reference_components': len(ref_sch.components),
            'recreated_components': len(rec_sch.components),
            'component_differences': len(component_result.get('differences', [])),
            'overall_match': result['semantic_match']
        }
        
        return result
    
    def _compare_components(self, ref_sch: Schematic, rec_sch: Schematic) -> Dict[str, Any]:
        """Compare components between two schematics."""
        result = {
            'match': True,
            'reference_count': len(ref_sch.components),
            'recreated_count': len(rec_sch.components),
            'differences': [],
            'missing_components': [],
            'extra_components': [],
            'property_mismatches': []
        }
        
        # Get component references
        ref_refs = {comp.reference for comp in ref_sch.components}
        rec_refs = {comp.reference for comp in rec_sch.components}
        
        # Find missing and extra components
        missing = ref_refs - rec_refs
        extra = rec_refs - ref_refs
        
        if missing:
            result['missing_components'] = list(missing)
            result['differences'].append(f"Missing components: {', '.join(missing)}")
            result['match'] = False
        
        if extra:
            result['extra_components'] = list(extra)
            result['differences'].append(f"Extra components: {', '.join(extra)}")
            result['match'] = False
        
        # Compare matching components
        for ref_comp in ref_sch.components:
            if ref_comp.reference in rec_refs:
                rec_comp = rec_sch.components.get(ref_comp.reference)
                comp_diff = self._compare_component_properties(ref_comp, rec_comp)
                if comp_diff['differences']:
                    result['property_mismatches'].append({
                        'reference': ref_comp.reference,
                        'differences': comp_diff['differences']
                    })
                    result['match'] = False
        
        return result
    
    def _compare_component_properties(self, ref_comp, rec_comp) -> Dict[str, Any]:
        """Compare properties of two components."""
        result = {
            'match': True,
            'differences': []
        }
        
        # Compare basic properties
        properties_to_compare = [
            ('lib_id', 'Library ID'),
            ('value', 'Value'), 
            ('footprint', 'Footprint'),
            ('rotation', 'Rotation')
        ]
        
        for prop_name, display_name in properties_to_compare:
            ref_value = getattr(ref_comp, prop_name, None)
            rec_value = getattr(rec_comp, prop_name, None)
            
            if ref_value != rec_value:
                result['differences'].append(
                    f"{display_name}: expected '{ref_value}', got '{rec_value}'"
                )
                result['match'] = False
        
        # Compare positions with tolerance
        if hasattr(ref_comp, 'position') and hasattr(rec_comp, 'position'):
            ref_pos = ref_comp.position
            rec_pos = rec_comp.position
            
            x_diff = abs(ref_pos.x - rec_pos.x)
            y_diff = abs(ref_pos.y - rec_pos.y)
            
            if x_diff > self.tolerance or y_diff > self.tolerance:
                result['differences'].append(
                    f"Position: expected ({ref_pos.x}, {ref_pos.y}), "
                    f"got ({rec_pos.x}, {rec_pos.y}) "
                    f"(diff: {x_diff:.4f}, {y_diff:.4f})"
                )
                result['match'] = False
        
        # Compare custom properties
        ref_props = getattr(ref_comp, 'properties', {})
        rec_props = getattr(rec_comp, 'properties', {})
        
        all_prop_keys = set(ref_props.keys()) | set(rec_props.keys())
        
        for prop_key in all_prop_keys:
            ref_val = ref_props.get(prop_key)
            rec_val = rec_props.get(prop_key)
            
            if ref_val != rec_val:
                result['differences'].append(
                    f"Property '{prop_key}': expected '{ref_val}', got '{rec_val}'"
                )
                result['match'] = False
        
        return result
    
    def _compare_files(self, ref_path: Path, rec_path: Path) -> Dict[str, Any]:
        """Compare files at the text level."""
        result = {
            'identical': False,
            'line_differences': [],
            'unified_diff': ""
        }
        
        try:
            with open(ref_path, 'r', encoding='utf-8') as f:
                ref_lines = f.readlines()
            
            with open(rec_path, 'r', encoding='utf-8') as f:
                rec_lines = f.readlines()
            
            # Check if files are identical
            result['identical'] = (ref_lines == rec_lines)
            
            if not result['identical']:
                # Generate diff
                diff = list(difflib.unified_diff(
                    ref_lines,
                    rec_lines, 
                    fromfile=str(ref_path),
                    tofile=str(rec_path),
                    lineterm=''
                ))
                result['unified_diff'] = '\n'.join(diff)
                
                # Count line differences
                additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
                deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
                
                result['line_differences'] = {
                    'additions': additions,
                    'deletions': deletions,
                    'total_changes': additions + deletions
                }
        
        except Exception as e:
            result['error'] = f"Failed to compare files: {e}"
        
        return result
    
    def generate_comparison_report(self, comparison_result: Dict[str, Any]) -> str:
        """Generate a human-readable comparison report."""
        if not comparison_result['success']:
            return f"Comparison failed: {comparison_result.get('error', 'Unknown error')}"
        
        report_lines = [
            "=" * 60,
            "SCHEMATIC COMPARISON REPORT",
            "=" * 60,
            "",
            f"Reference: {comparison_result['reference_path']}",
            f"Recreated: {comparison_result['recreated_path']}",
            ""
        ]
        
        # Summary
        summary = comparison_result['summary']
        report_lines.extend([
            "SUMMARY:",
            f"  Reference components: {summary['reference_components']}",
            f"  Recreated components: {summary['recreated_components']}",
            f"  Component differences: {summary['component_differences']}",
            f"  Overall match: {'✓ PASS' if summary['overall_match'] else '✗ FAIL'}",
            f"  Exact file match: {'✓ YES' if comparison_result.get('exact_file_match', False) else '✗ NO'}",
            ""
        ])
        
        # Component analysis
        comp_result = comparison_result['components']
        if not comp_result['match']:
            report_lines.extend([
                "COMPONENT DIFFERENCES:",
                ""
            ])
            
            if comp_result['missing_components']:
                report_lines.append(f"  Missing: {', '.join(comp_result['missing_components'])}")
            
            if comp_result['extra_components']:
                report_lines.append(f"  Extra: {', '.join(comp_result['extra_components'])}")
            
            if comp_result['property_mismatches']:
                report_lines.append("  Property mismatches:")
                for mismatch in comp_result['property_mismatches']:
                    report_lines.append(f"    {mismatch['reference']}:")
                    for diff in mismatch['differences']:
                        report_lines.append(f"      - {diff}")
            
            report_lines.append("")
        
        # File differences (if available)
        if 'file_comparison' in comparison_result:
            file_comp = comparison_result['file_comparison']
            if not file_comp['identical'] and 'line_differences' in file_comp:
                line_diffs = file_comp['line_differences']
                report_lines.extend([
                    "FILE-LEVEL DIFFERENCES:",
                    f"  Lines added: {line_diffs['additions']}",
                    f"  Lines deleted: {line_diffs['deletions']}",
                    f"  Total changes: {line_diffs['total_changes']}",
                    ""
                ])
        
        report_lines.append("=" * 60)
        
        return '\n'.join(report_lines)


def compare_with_reference(
    reference_name: str,
    recreated_path: Union[str, Path],
    reference_base_dir: Optional[Union[str, Path]] = None,
    tolerance: float = 0.001,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Convenient function to compare a recreated schematic with its reference.
    
    Args:
        reference_name: Name of reference project (e.g., 'single_resistor')
        recreated_path: Path to recreated schematic file
        reference_base_dir: Base directory containing reference projects
        tolerance: Position comparison tolerance
        verbose: Whether to print detailed report
        
    Returns:
        Comparison result dictionary
    """
    if reference_base_dir is None:
        # Default to test reference directory
        test_dir = Path(__file__).parent.parent
        reference_base_dir = test_dir / "reference_kicad_projects"
    else:
        reference_base_dir = Path(reference_base_dir)
    
    reference_path = reference_base_dir / reference_name / f"{reference_name}.kicad_sch"
    
    comparator = SchematicComparator(tolerance=tolerance)
    result = comparator.compare_schematics(reference_path, recreated_path)
    
    if verbose:
        report = comparator.generate_comparison_report(result)
        print(report)
    
    return result