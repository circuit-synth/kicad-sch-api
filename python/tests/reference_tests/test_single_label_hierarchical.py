"""
Test recreation of single_label_hierarchical reference project.

This test verifies that kicad-sch-api can handle schematics with hierarchical labels.
Note: Full hierarchical label recreation may require additional API development.
"""

from .base_reference_test import BaseReferenceTest


class TestSingleLabelHierarchical(BaseReferenceTest):
    """Test recreation of single hierarchical label schematic."""
    
    def test_single_label_hierarchical_loading(self):
        """Test that the single hierarchical label schematic loads successfully."""
        ref_sch = self.load_reference_schematic("single_label_hierarchical")
        
        assert ref_sch is not None, "Single hierarchical label schematic should load successfully"
        assert hasattr(ref_sch, 'components'), "Should have components collection"
        
        print(f"✅ Single hierarchical label schematic loaded: {len(ref_sch.components)} components")
    
    def test_single_label_hierarchical_component_recreation(self):
        """Test recreation of components in single hierarchical label schematic."""
        ref_sch = self.load_reference_schematic("single_label_hierarchical")
        
        # Recreate the schematic components
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, "hierarchical_label_components")
        
        # Basic validation
        assert len(recreated_sch.components) == len(ref_sch.components), "Component count should match"
        
        print(f"✅ Single hierarchical label component recreation: {len(recreated_sch.components)} components")
    
    def test_single_label_hierarchical_placeholder(self):
        """Placeholder test for future hierarchical label handling."""
        ref_sch = self.load_reference_schematic("single_label_hierarchical")
        
        assert ref_sch is not None, "Schematic should load"
        
        # TODO: Add hierarchical label recreation tests when API supports them
        print("⚠ Hierarchical label recreation not yet implemented - placeholder test passed")