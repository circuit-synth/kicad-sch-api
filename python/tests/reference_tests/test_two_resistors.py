"""
Test recreation of two_resistors reference project.

This test verifies that kicad-sch-api can recreate a schematic with multiple
components, testing component management for multi-component schematics.
"""

from .base_reference_test import BaseReferenceTest


class TestTwoResistors(BaseReferenceTest):
    """Test recreation of two resistors schematic."""
    
    def test_two_resistors_recreation(self):
        """Test that we can recreate the two resistors schematic exactly."""
        result = self.assert_schematic_recreation_successful("two_resistors")
        
        # Additional validation specific to two resistors
        ref_sch = result['reference']
        recreated_sch = result['recreated']
        
        # Both should have exactly 2 components
        assert len(ref_sch.components) == 2, "Reference should have 2 components"
        assert len(recreated_sch.components) == 2, "Recreated should have 2 components"
        
        # Get references of all components
        ref_refs = {comp.reference for comp in ref_sch.components}
        rec_refs = {comp.reference for comp in recreated_sch.components}
        
        # Should have R1 and R2
        expected_refs = {"R1", "R2"}
        assert ref_refs == expected_refs, f"Reference should have {expected_refs}, got {ref_refs}"
        assert rec_refs == expected_refs, f"Recreated should have {expected_refs}, got {rec_refs}"
        
        print(f"✅ Two resistors recreation successful: {len(recreated_sch.components)} components ({sorted(rec_refs)})")
    
    def test_two_resistors_individual_components(self):
        """Test each resistor component individually."""
        ref_sch = self.load_reference_schematic("two_resistors")
        
        # Get both resistors
        r1 = ref_sch.components.get("R1")
        r2 = ref_sch.components.get("R2")
        
        assert r1 is not None, "R1 should exist"
        assert r2 is not None, "R2 should exist"
        
        # Both should be Device:R with 10k value
        for resistor in [r1, r2]:
            assert resistor.lib_id == "Device:R", f"{resistor.reference} should use Device:R"
            assert resistor.value == "10k", f"{resistor.reference} should have 10k value"
            assert resistor.footprint == "Resistor_SMD:R_0603_1608Metric", f"{resistor.reference} should have correct footprint"
        
        # They should have different positions
        assert r1.position != r2.position, "R1 and R2 should have different positions"
        
        print(f"✅ Individual resistor validation passed:")
        print(f"    R1: pos=({r1.position.x}, {r1.position.y})")
        print(f"    R2: pos=({r2.position.x}, {r2.position.y})")
    
    def test_two_resistors_position_differences(self):
        """Test that the resistors have different positions as expected."""
        ref_sch = self.load_reference_schematic("two_resistors")
        
        r1 = ref_sch.components.get("R1")
        r2 = ref_sch.components.get("R2")
        
        # Calculate distance between resistors
        x_distance = abs(r1.position.x - r2.position.x)
        y_distance = abs(r1.position.y - r2.position.y)
        
        # Should be separated by some distance
        assert x_distance > 1.0 or y_distance > 1.0, "Resistors should be separated by meaningful distance"
        
        print(f"✅ Resistor separation validated: Δx={x_distance:.3f}, Δy={y_distance:.3f}")
    
    def test_two_resistors_component_access(self):
        """Test that component access methods work with multiple components."""
        ref_sch = self.load_reference_schematic("two_resistors")
        
        # Test various access methods
        assert len(ref_sch.components) == 2, "Should have 2 components"
        
        # Test get by reference
        r1 = ref_sch.components.get("R1")
        r2 = ref_sch.components.get("R2")
        assert r1 is not None and r2 is not None, "Should be able to get components by reference"
        
        # Test iteration
        components_list = list(ref_sch.components)
        assert len(components_list) == 2, "Should be able to iterate over components"
        
        # Test filtering
        all_resistors = ref_sch.components.filter(lib_id="Device:R")
        assert len(all_resistors) == 2, "Should be able to filter components"
        
        print(f"✅ Component access methods validation passed")
    
    def test_two_resistors_bulk_operations(self):
        """Test bulk operations on multiple resistors."""
        from kicad_sch_api.core.schematic import Schematic
        
        # Create test schematic with two resistors
        sch = Schematic.create("bulk_test")
        
        # Add two resistors
        r1 = sch.components.add('Device:R', 'R1', '10k', (100, 100))
        r2 = sch.components.add('Device:R', 'R2', '10k', (150, 100))
        
        # Test bulk update operation
        updated_count = sch.components.bulk_update(
            criteria={'lib_id': 'Device:R'},
            updates={'properties': {'Tolerance': '1%', 'Power': '0.1W'}}
        )
        
        assert updated_count == 2, "Should update both resistors"
        
        # Verify bulk update worked
        for resistor in [r1, r2]:
            assert resistor.get_property('Tolerance') == '1%', f"{resistor.reference} should have Tolerance property"
            assert resistor.get_property('Power') == '0.1W', f"{resistor.reference} should have Power property"
        
        print(f"✅ Bulk operations validation passed: updated {updated_count} components")
    
    def test_two_resistors_recreation_fidelity(self):
        """Test high-fidelity recreation of two resistors schematic."""
        ref_sch = self.load_reference_schematic("two_resistors")
        
        # Recreate schematic
        recreated_sch = self.recreate_schematic_from_reference(ref_sch, "fidelity_test")
        
        # Save and reload
        saved_sch = self.save_and_reload_schematic(recreated_sch, "fidelity_saved")
        
        # Compare each component in detail
        for ref_comp in ref_sch.components:
            rec_comp = saved_sch.components.get(ref_comp.reference)
            assert rec_comp is not None, f"Component {ref_comp.reference} should exist in recreation"
            
            # Check all basic properties
            assert rec_comp.lib_id == ref_comp.lib_id, f"{ref_comp.reference}: lib_id mismatch"
            assert rec_comp.value == ref_comp.value, f"{ref_comp.reference}: value mismatch"
            assert rec_comp.footprint == ref_comp.footprint, f"{ref_comp.reference}: footprint mismatch"
            
            # Check position with tolerance
            pos_tolerance = 0.001
            x_diff = abs(rec_comp.position.x - ref_comp.position.x)
            y_diff = abs(rec_comp.position.y - ref_comp.position.y)
            assert x_diff < pos_tolerance, f"{ref_comp.reference}: X position difference {x_diff} > {pos_tolerance}"
            assert y_diff < pos_tolerance, f"{ref_comp.reference}: Y position difference {y_diff} > {pos_tolerance}"
            
            # Check properties
            for prop_name, prop_value in ref_comp.properties.items():
                rec_prop_value = rec_comp.get_property(prop_name)
                assert rec_prop_value == prop_value, f"{ref_comp.reference}: property {prop_name} mismatch"
        
        print(f"✅ High-fidelity recreation validation passed")