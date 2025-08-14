"""
Test recreation of single_text reference project.

This test verifies that kicad-sch-api can handle schematics with text elements.
Note: Full text recreation may require additional API development.
"""

from .base_reference_test import BaseReferenceTest


class TestSingleText(BaseReferenceTest):
    """Test recreation of single text schematic."""
    
    def test_single_text_schematic_loading(self):
        """Test that the single text schematic loads successfully."""
        ref_sch = self.load_reference_schematic("single_text")
        
        assert ref_sch is not None, "Single text schematic should load successfully"
        assert hasattr(ref_sch, 'components'), "Should have components collection"
        
        print(f"✅ Single text schematic loaded: {len(ref_sch.components)} components")
    
    def test_single_text_component_recreation(self):
        """Test recreation of components in single text schematic."""
        ref_sch = self.load_reference_schematic("single_text")
        
        # Recreate the schematic components
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, "single_text_components")
        
        # Basic validation
        assert len(recreated_sch.components) == len(ref_sch.components), "Component count should match"
        
        print(f"✅ Single text component recreation: {len(recreated_sch.components)} components")
    
    def test_single_text_placeholder(self):
        """Placeholder test for future text element handling."""
        ref_sch = self.load_reference_schematic("single_text")
        
        assert ref_sch is not None, "Schematic should load"
        
        # TODO: Add text element recreation tests when API supports them
        print("⚠ Text element recreation not yet implemented - placeholder test passed")