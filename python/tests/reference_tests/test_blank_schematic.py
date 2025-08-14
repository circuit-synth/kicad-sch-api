"""
Test recreation of blank_schematic reference project.

This test verifies that kicad-sch-api can create and save blank schematics
that match the reference blank_schematic.kicad_sch format.
"""

from .base_reference_test import BaseReferenceTest


class TestBlankSchematic(BaseReferenceTest):
    """Test recreation of blank schematic."""
    
    def test_blank_schematic_recreation(self):
        """Test that we can recreate the blank schematic exactly."""
        result = self.assert_schematic_recreation_successful("blank_schematic")
        
        # Additional validation specific to blank schematic
        ref_sch = result['reference']
        recreated_sch = result['recreated']
        
        # Both should have 0 components
        assert len(ref_sch.components) == 0, "Reference blank schematic should have 0 components"
        assert len(recreated_sch.components) == 0, "Recreated blank schematic should have 0 components"
        
        print(f"✅ Blank schematic recreation successful: {len(recreated_sch.components)} components")
    
    def test_blank_schematic_structure(self):
        """Test the structure of blank schematic matches expectations."""
        ref_sch = self.load_reference_schematic("blank_schematic")
        
        # Should load without errors
        assert ref_sch is not None, "Blank schematic should load successfully"
        
        # Should have no components
        assert len(ref_sch.components) == 0, "Blank schematic should be empty"
        
        # Should have basic schematic structure
        assert hasattr(ref_sch, 'components'), "Should have components collection"
        
        print(f"✅ Blank schematic structure validation passed")
    
    def test_blank_schematic_save_load_cycle(self):
        """Test that blank schematic survives save/load cycle."""
        # Create blank schematic
        from kicad_sch_api.core.schematic import Schematic
        blank_sch = Schematic.create("test_blank")
        
        # Should have 0 components
        assert len(blank_sch.components) == 0
        
        # Save and reload
        saved_sch = self.save_and_reload_schematic(blank_sch, "blank_cycle_test")
        
        # Should still have 0 components
        assert len(saved_sch.components) == 0
        
        print(f"✅ Blank schematic save/load cycle passed")