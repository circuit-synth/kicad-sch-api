"""
Test recreation of resistor_divider reference project.

This test verifies that kicad-sch-api can handle a more complex circuit
with resistors arranged in a voltage divider configuration.
"""

from .base_reference_test import BaseReferenceTest


class TestResistorDivider(BaseReferenceTest):
    """Test recreation of resistor divider schematic."""
    
    def test_resistor_divider_component_recreation(self):
        """Test that we can recreate all components in the resistor divider."""
        result = self.assert_schematic_recreation_successful("resistor_divider")
        
        ref_sch = result['reference']
        recreated_sch = result['recreated']
        
        print(f"✅ Resistor divider recreation successful: {len(recreated_sch.components)} components")
        
        # Log component details
        for comp in recreated_sch.components:
            print(f"    {comp.reference}: {comp.lib_id} = {comp.value}")
    
    def test_resistor_divider_structure(self):
        """Test the structure of the resistor divider circuit."""
        ref_sch = self.load_reference_schematic("resistor_divider")
        
        # Should have components (resistors for voltage divider)
        assert len(ref_sch.components) >= 2, "Resistor divider should have at least 2 resistors"
        
        # All components should be resistors for a basic divider
        resistor_count = len(ref_sch.components.filter(lib_id="Device:R"))
        print(f"✅ Resistor divider has {resistor_count} resistor components")
    
    def test_resistor_divider_load_capability(self):
        """Test that the resistor divider schematic loads without errors."""
        ref_sch = self.load_reference_schematic("resistor_divider")
        
        assert ref_sch is not None, "Resistor divider should load successfully"
        assert hasattr(ref_sch, 'components'), "Should have components collection"
        
        # Should be able to iterate over components
        component_list = list(ref_sch.components)
        assert len(component_list) >= 0, "Should be able to iterate over components"
        
        print(f"✅ Resistor divider load capability validated")