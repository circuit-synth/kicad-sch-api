"""
Test recreation of single_label reference project.

This test verifies that kicad-sch-api can handle schematics with labels.
Note: Full label recreation may require additional API development.
"""

from .base_reference_test import BaseReferenceTest


class TestSingleLabel(BaseReferenceTest):
    """Test recreation of single label schematic."""
    
    def test_single_label_schematic_loading(self):
        """Test that the single label schematic loads successfully."""
        ref_sch = self.load_reference_schematic("single_label")
        
        assert ref_sch is not None, "Single label schematic should load successfully"
        assert hasattr(ref_sch, 'components'), "Should have components collection"
        
        print(f"✅ Single label schematic loaded: {len(ref_sch.components)} components")
    
    def test_single_label_component_recreation(self):
        """Test recreation of components in single label schematic."""
        ref_sch = self.load_reference_schematic("single_label")
        
        # Recreate the schematic components
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, "single_label_components")
        
        # Basic validation - components should match
        assert len(recreated_sch.components) == len(ref_sch.components), "Component count should match"
        
        print(f"✅ Single label component recreation: {len(recreated_sch.components)} components")
    
    def test_single_label_future_enhancement_placeholder(self):
        """Placeholder test for future label handling enhancement."""
        ref_sch = self.load_reference_schematic("single_label")
        
        assert ref_sch is not None, "Schematic should load"
        
        # TODO: Add label recreation tests when API supports labels
        print("⚠ Label recreation not yet implemented - placeholder test passed")