"""
Test recreation of single_resistor reference project.

This test verifies that kicad-sch-api can recreate a schematic with a single
resistor component, matching all properties, position, and footprint exactly.
"""

from .base_reference_test import BaseReferenceTest


class TestSingleResistor(BaseReferenceTest):
    """Test recreation of single resistor schematic."""
    
    def test_single_resistor_recreation(self):
        """Test that we can recreate the single resistor schematic exactly."""
        result = self.assert_schematic_recreation_successful("single_resistor")
        
        # Additional validation specific to single resistor
        ref_sch = result['reference']
        recreated_sch = result['recreated']
        
        # Both should have exactly 1 component
        assert len(ref_sch.components) == 1, "Reference should have 1 component"
        assert len(recreated_sch.components) == 1, "Recreated should have 1 component"
        
        # Get the resistor components
        ref_resistor = list(ref_sch.components)[0]
        rec_resistor = list(recreated_sch.components)[0]
        
        # Validate resistor properties
        assert ref_resistor.reference == "R1", "Reference component should be R1"
        assert rec_resistor.reference == "R1", "Recreated component should be R1"
        assert ref_resistor.lib_id == "Device:R", "Should use Device:R library"
        assert rec_resistor.lib_id == "Device:R", "Should use Device:R library"
        assert ref_resistor.value == "10k", "Should have 10k value"
        assert rec_resistor.value == "10k", "Should have 10k value"
        
        print(f"✅ Single resistor recreation successful: R1 = {rec_resistor.value}")
    
    def test_single_resistor_properties(self):
        """Test that all resistor properties are preserved correctly."""
        ref_sch = self.load_reference_schematic("single_resistor")
        resistor = list(ref_sch.components)[0]
        
        # Check expected properties
        expected_properties = {
            'reference': 'R1',
            'lib_id': 'Device:R',
            'value': '10k',
            'footprint': 'Resistor_SMD:R_0603_1608Metric'
        }
        
        for prop, expected_value in expected_properties.items():
            actual_value = getattr(resistor, prop, None)
            assert actual_value == expected_value, f"Property {prop}: expected {expected_value}, got {actual_value}"
        
        # Check custom properties
        assert 'Datasheet' in resistor.properties, "Should have Datasheet property"
        assert 'Description' in resistor.properties, "Should have Description property"
        assert resistor.properties['Description'] == 'Resistor', "Description should be 'Resistor'"
        
        print(f"✅ Single resistor properties validation passed")
    
    def test_single_resistor_position_accuracy(self):
        """Test that resistor position is preserved with high accuracy."""
        ref_sch = self.load_reference_schematic("single_resistor")
        resistor = list(ref_sch.components)[0]
        
        # Check position values (from reference analysis)
        expected_x = 93.98
        expected_y = 81.28
        
        assert abs(resistor.position.x - expected_x) < 0.001, f"X position: expected {expected_x}, got {resistor.position.x}"
        assert abs(resistor.position.y - expected_y) < 0.001, f"Y position: expected {expected_y}, got {resistor.position.y}"
        
        print(f"✅ Single resistor position accuracy validated: ({resistor.position.x}, {resistor.position.y})")
    
    def test_single_resistor_footprint_preservation(self):
        """Test that footprint information is preserved correctly."""
        ref_sch = self.load_reference_schematic("single_resistor")
        resistor = list(ref_sch.components)[0]
        
        expected_footprint = "Resistor_SMD:R_0603_1608Metric"
        assert resistor.footprint == expected_footprint, f"Footprint: expected {expected_footprint}, got {resistor.footprint}"
        
        # Recreate and verify footprint preservation
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, "footprint_test")
        recreated_resistor = list(recreated_sch.components)[0]
        
        assert recreated_resistor.footprint == expected_footprint, "Footprint should be preserved in recreation"
        
        print(f"✅ Single resistor footprint preservation validated: {recreated_resistor.footprint}")
    
    def test_single_resistor_api_usage(self):
        """Test creating single resistor using the documented API patterns."""
        from kicad_sch_api.core.schematic import Schematic
        
        # Create schematic using API
        sch = Schematic.create("api_test")
        
        # Add resistor using documented API pattern
        resistor = sch.components.add('Device:R', reference='R1', value='10k', position=(93.98, 81.28))
        
        # Set footprint using documented API
        resistor.footprint = 'Resistor_SMD:R_0603_1608Metric'
        
        # Set properties using documented API  
        resistor.set_property('Datasheet', '~')
        resistor.set_property('Description', 'Resistor')
        
        # Verify API worked correctly
        assert resistor.reference == 'R1'
        assert resistor.lib_id == 'Device:R'
        assert resistor.value == '10k'
        assert resistor.position.x == 93.98
        assert resistor.position.y == 81.28
        assert resistor.footprint == 'Resistor_SMD:R_0603_1608Metric'
        assert resistor.get_property('Datasheet') == '~'
        assert resistor.get_property('Description') == 'Resistor'
        
        print(f"✅ Single resistor API usage validation passed")