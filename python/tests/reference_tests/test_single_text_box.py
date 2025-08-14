"""
Test recreation of single_text_box reference project.

This test verifies that kicad-sch-api can handle schematics with text box elements.
Note: Full text box recreation may require additional API development.
"""

from .base_reference_test import BaseReferenceTest


class TestSingleTextBox(BaseReferenceTest):
    """Test recreation of single text box schematic."""
    
    def test_single_text_box_schematic_loading(self):
        """Test that the single text box schematic loads successfully."""
        ref_sch = self.load_reference_schematic("single_text_box")
        
        assert ref_sch is not None, "Single text box schematic should load successfully"
        assert hasattr(ref_sch, 'components'), "Should have components collection"
        
        print(f"✅ Single text box schematic loaded: {len(ref_sch.components)} components")
    
    def test_single_text_box_component_recreation(self):
        """Test recreation of components in single text box schematic."""
        ref_sch = self.load_reference_schematic("single_text_box")
        
        # Recreate the schematic components
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, "text_box_components")
        
        # Basic validation
        assert len(recreated_sch.components) == len(ref_sch.components), "Component count should match"
        
        print(f"✅ Single text box component recreation: {len(recreated_sch.components)} components")
    
    def test_single_text_box_placeholder(self):
        """Placeholder test for future text box handling."""
        ref_sch = self.load_reference_schematic("single_text_box")
        
        assert ref_sch is not None, "Schematic should load"
        
        # TODO: Add text box recreation tests when API supports them
        print("⚠ Text box recreation not yet implemented - placeholder test passed")