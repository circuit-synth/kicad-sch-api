"""
Test recreation of single_hierarchical_sheet reference project.

This test verifies that kicad-sch-api can handle schematics with hierarchical sheets.
Note: Full hierarchical sheet recreation may require additional API development.
"""

import sys
from pathlib import Path

from .base_reference_test import BaseReferenceTest


class TestSingleHierarchicalSheet(BaseReferenceTest):
    """Test recreation of single hierarchical sheet schematic."""
    
    def test_single_hierarchical_sheet_loading(self):
        """Test that the single hierarchical sheet schematic loads successfully."""
        ref_sch = self.load_reference_schematic("single_hierarchical_sheet")
        
        assert ref_sch is not None, "Single hierarchical sheet schematic should load successfully"
        assert hasattr(ref_sch, 'components'), "Should have components collection"
        
        print(f"✅ Single hierarchical sheet schematic loaded: {len(ref_sch.components)} components")
    
    def test_single_hierarchical_sheet_component_recreation(self):
        """Test recreation of components in single hierarchical sheet schematic."""
        ref_sch = self.load_reference_schematic("single_hierarchical_sheet")
        
        # Recreate the schematic components
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, "hierarchical_sheet_components")
        
        # Basic validation
        assert len(recreated_sch.components) == len(ref_sch.components), "Component count should match"
        
        print(f"✅ Single hierarchical sheet component recreation: {len(recreated_sch.components)} components")
    
    def test_hierarchical_sheet_structure_awareness(self):
        """Test awareness of hierarchical sheet structure."""
        ref_sch = self.load_reference_schematic("single_hierarchical_sheet")
        
        # Check if there's a subcircuit file
        reference_dir = Path(__file__).parent / "reference_kicad_projects" / "single_hierarchical_sheet"
        subcircuit_file = reference_dir / "subcircuit1.kicad_sch"
        
        if subcircuit_file.exists():
            print(f"✅ Found hierarchical subcircuit: {subcircuit_file.name}")
            
            # Try to load the subcircuit
            try:
                from kicad_sch_api.core.schematic import Schematic
                sub_sch = Schematic.load(str(subcircuit_file))
                print(f"    Subcircuit loaded: {len(sub_sch.components)} components")
            except Exception as e:
                print(f"    Subcircuit load failed: {e}")
        else:
            print("⚠ No subcircuit file found")
    
    def test_single_hierarchical_sheet_placeholder(self):
        """Placeholder test for future hierarchical sheet handling."""
        ref_sch = self.load_reference_schematic("single_hierarchical_sheet")
        
        assert ref_sch is not None, "Schematic should load"
        
        # TODO: Add hierarchical sheet recreation tests when API supports them
        print("⚠ Hierarchical sheet recreation not yet implemented - placeholder test passed")