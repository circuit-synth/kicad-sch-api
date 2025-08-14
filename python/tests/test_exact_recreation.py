"""
Focused tests for exact recreation of critical reference schematics.

These tests ensure that kicad-sch-api can recreate reference schematics
with pixel-perfect accuracy, validating the core functionality required
for public release.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kicad_sch_api.core.schematic import Schematic
from tests.utils.schematic_comparison import SchematicComparator, compare_with_reference

# Create convenience module-like access
class KSAModule:
    @staticmethod
    def load_schematic(path):
        return Schematic.load(path)
    
    @staticmethod
    def create_schematic(name):
        return Schematic.create(name)

ksa = KSAModule()


class TestExactRecreation:
    """Test exact recreation of the most important reference schematics."""
    
    def setup_method(self):
        """Set up test environment.""" 
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.comparator = SchematicComparator(tolerance=0.001)
    
    @pytest.fixture
    def reference_dir(self):
        """Path to reference KiCAD projects."""
        return Path(__file__).parent / "reference_tests" / "reference_kicad_projects"
    
    def test_exact_blank_schematic(self, reference_dir):
        """Test exact recreation of blank schematic - should be perfect match."""
        output_path = self.temp_path / "blank_exact.kicad_sch"
        
        # Create minimal schematic
        sch = ksa.create_schematic("blank_schematic")
        
        # Set exact properties to match reference
        # This may require examining the reference file structure
        
        sch.save(str(output_path))
        
        # Compare with reference
        result = compare_with_reference(
            "blank_schematic",
            output_path,
            reference_dir,
            verbose=True
        )
        
        assert result['success'], f"Comparison failed: {result.get('error')}"
        assert result['semantic_match'], "Blank schematic should have semantic match"
    
    def test_exact_single_resistor(self, reference_dir):
        """Test exact recreation of single resistor schematic."""
        output_path = self.temp_path / "single_resistor_exact.kicad_sch"
        
        # First, analyze the reference to extract exact parameters
        reference_path = reference_dir / "single_resistor" / "single_resistor.kicad_sch"
        ref_sch = ksa.load_schematic(str(reference_path))
        
        print(f"Reference has {len(ref_sch.components)} components")
        
        # Get the exact reference component
        if len(ref_sch.components) > 0:
            ref_resistor = list(ref_sch.components)[0]
            print(f"Reference resistor: {ref_resistor.reference}")
            print(f"  lib_id: {ref_resistor.lib_id}")
            print(f"  value: {ref_resistor.value}")
            print(f"  position: ({ref_resistor.position.x}, {ref_resistor.position.y})")
            print(f"  footprint: {ref_resistor.footprint}")
            print(f"  properties: {list(ref_resistor.properties.keys())}")
        
        # Create new schematic with exact parameters
        sch = ksa.create_schematic("single_resistor")
        
        # Add resistor with exact parameters from reference
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k", 
            position=(93.98, 81.28),
            footprint="Resistor_SMD:R_0603_1608Metric"
        )
        
        # Set exact properties to match reference
        resistor.set_property("Datasheet", "~")
        resistor.set_property("Description", "Resistor")
        
        # Copy any additional properties from reference
        if len(ref_sch.components) > 0:
            ref_resistor = list(ref_sch.components)[0]
            for prop_name, prop_value in ref_resistor.properties.items():
                if prop_name not in ["Datasheet", "Description"]:
                    resistor.set_property(prop_name, prop_value)
        
        sch.save(str(output_path))
        
        # Detailed comparison
        result = compare_with_reference(
            "single_resistor",
            output_path, 
            reference_dir,
            verbose=True
        )
        
        assert result['success'], f"Comparison failed: {result.get('error')}"
        assert result['semantic_match'], "Single resistor should have semantic match"
        
        # Verify component count
        assert result['summary']['reference_components'] == result['summary']['recreated_components'], \
            "Component counts should match exactly"
    
    def test_exact_two_resistors(self, reference_dir):
        """Test exact recreation of two resistors schematic."""
        output_path = self.temp_path / "two_resistors_exact.kicad_sch"
        
        # Load reference to get exact parameters
        reference_path = reference_dir / "two_resistors" / "two_resistors.kicad_sch"
        ref_sch = ksa.load_schematic(str(reference_path))
        
        print(f"Reference has {len(ref_sch.components)} components")
        for comp in ref_sch.components:
            print(f"  {comp.reference}: {comp.lib_id}, {comp.value}, pos=({comp.position.x}, {comp.position.y})")
        
        # Create new schematic
        sch = ksa.create_schematic("two_resistors")
        
        # Recreate each component with exact parameters
        for ref_comp in ref_sch.components:
            new_comp = sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=(ref_comp.position.x, ref_comp.position.y),
                footprint=ref_comp.footprint
            )
            
            # Copy all properties exactly
            for prop_name, prop_value in ref_comp.properties.items():
                new_comp.set_property(prop_name, prop_value)
        
        sch.save(str(output_path))
        
        # Compare with reference
        result = compare_with_reference(
            "two_resistors",
            output_path,
            reference_dir, 
            verbose=True
        )
        
        assert result['success'], f"Comparison failed: {result.get('error')}"
        assert result['semantic_match'], "Two resistors should have semantic match"
        assert result['summary']['component_differences'] == 0, "Should have no component differences"
    
    def test_component_property_accuracy(self, reference_dir):
        """Test that all component properties are recreated accurately."""
        reference_projects = ["single_resistor", "two_resistors"]
        
        for project_name in reference_projects:
            reference_path = reference_dir / project_name / f"{project_name}.kicad_sch"
            if not reference_path.exists():
                continue
            
            # Load reference
            ref_sch = ksa.load_schematic(str(reference_path))
            
            # Create recreation
            new_sch = ksa.create_schematic(project_name)
            
            # Copy each component exactly
            for ref_comp in ref_sch.components:
                new_comp = new_sch.components.add(
                    lib_id=ref_comp.lib_id,
                    reference=ref_comp.reference,
                    value=ref_comp.value,
                    position=(ref_comp.position.x, ref_comp.position.y),
                    footprint=ref_comp.footprint
                )
                
                # Test property copying
                for prop_name, prop_value in ref_comp.properties.items():
                    new_comp.set_property(prop_name, prop_value)
                
                # Verify properties were set correctly
                for prop_name, expected_value in ref_comp.properties.items():
                    actual_value = new_comp.get_property(prop_name)
                    assert actual_value == expected_value, \
                        f"Property {prop_name} mismatch in {ref_comp.reference}: expected '{expected_value}', got '{actual_value}'"
    
    def test_position_precision(self, reference_dir):
        """Test that component positions are preserved with full precision."""
        # Test with single_resistor which has specific coordinates
        reference_path = reference_dir / "single_resistor" / "single_resistor.kicad_sch"
        if not reference_path.exists():
            pytest.skip("single_resistor reference not found")
        
        ref_sch = ksa.load_schematic(str(reference_path))
        
        for ref_comp in ref_sch.components:
            # Create new component with same position
            sch = ksa.create_schematic("position_test")
            new_comp = sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=(ref_comp.position.x, ref_comp.position.y)
            )
            
            # Verify position precision
            assert abs(new_comp.position.x - ref_comp.position.x) < 0.001, \
                f"X position precision lost: expected {ref_comp.position.x}, got {new_comp.position.x}"
            assert abs(new_comp.position.y - ref_comp.position.y) < 0.001, \
                f"Y position precision lost: expected {ref_comp.position.y}, got {new_comp.position.y}"
    
    def test_library_id_accuracy(self, reference_dir):
        """Test that library IDs are preserved exactly."""
        test_projects = ["single_resistor", "two_resistors"]
        
        for project_name in test_projects:
            reference_path = reference_dir / project_name / f"{project_name}.kicad_sch"
            if not reference_path.exists():
                continue
            
            ref_sch = ksa.load_schematic(str(reference_path))
            
            for ref_comp in ref_sch.components:
                # Test that library ID is exactly preserved
                assert ref_comp.lib_id, f"Reference component {ref_comp.reference} has empty lib_id"
                assert ":" in ref_comp.lib_id, f"Library ID {ref_comp.lib_id} should contain ':' separator"
                
                # Test recreation preserves lib_id
                sch = ksa.create_schematic("lib_test")
                new_comp = sch.components.add(
                    lib_id=ref_comp.lib_id,
                    reference=ref_comp.reference,
                    value=ref_comp.value or "test_value"
                )
                
                assert new_comp.lib_id == ref_comp.lib_id, \
                    f"Library ID not preserved: expected '{ref_comp.lib_id}', got '{new_comp.lib_id}'"
    
    def test_footprint_preservation(self, reference_dir):
        """Test that footprints are preserved exactly."""
        reference_path = reference_dir / "single_resistor" / "single_resistor.kicad_sch"
        if not reference_path.exists():
            pytest.skip("single_resistor reference not found")
        
        ref_sch = ksa.load_schematic(str(reference_path))
        
        for ref_comp in ref_sch.components:
            if ref_comp.footprint:  # Only test components that have footprints
                sch = ksa.create_schematic("footprint_test")
                new_comp = sch.components.add(
                    lib_id=ref_comp.lib_id,
                    reference=ref_comp.reference,
                    value=ref_comp.value,
                    footprint=ref_comp.footprint
                )
                
                assert new_comp.footprint == ref_comp.footprint, \
                    f"Footprint not preserved: expected '{ref_comp.footprint}', got '{new_comp.footprint}'"
    
    @pytest.mark.parametrize("project_name", [
        "blank_schematic",
        "single_resistor", 
        "two_resistors"
    ])
    def test_roundtrip_preservation(self, reference_dir, project_name):
        """Test that loading and saving preserves schematic exactly."""
        reference_path = reference_dir / project_name / f"{project_name}.kicad_sch"
        if not reference_path.exists():
            pytest.skip(f"Reference {project_name} not found")
        
        # Load original
        original_sch = ksa.load_schematic(str(reference_path))
        
        # Save to temp file
        temp_path = self.temp_path / f"{project_name}_roundtrip.kicad_sch"
        original_sch.save(str(temp_path))
        
        # Load saved version
        roundtrip_sch = ksa.load_schematic(str(temp_path))
        
        # Compare component by component
        assert len(original_sch.components) == len(roundtrip_sch.components), \
            "Component count should be preserved in roundtrip"
        
        for orig_comp in original_sch.components:
            rt_comp = roundtrip_sch.components.get(orig_comp.reference)
            assert rt_comp is not None, f"Component {orig_comp.reference} missing after roundtrip"
            
            # Compare key properties
            assert rt_comp.lib_id == orig_comp.lib_id, \
                f"Library ID changed in roundtrip for {orig_comp.reference}"
            assert rt_comp.value == orig_comp.value, \
                f"Value changed in roundtrip for {orig_comp.reference}"
            assert abs(rt_comp.position.x - orig_comp.position.x) < 0.001, \
                f"X position changed in roundtrip for {orig_comp.reference}"
            assert abs(rt_comp.position.y - orig_comp.position.y) < 0.001, \
                f"Y position changed in roundtrip for {orig_comp.reference}"


class TestAPIUsabilityForRecreation:
    """Test that the API is usable for practical schematic recreation."""
    
    def test_intuitive_component_creation(self):
        """Test that component creation API is intuitive and matches documentation."""
        sch = ksa.create_schematic("usability_test")
        
        # Test the documented API from CLAUDE.md
        resistor = sch.components.add('Device:R', reference='R1', value='10k', position=(100, 100))
        
        # Verify the API works as documented
        assert resistor.reference == 'R1'
        assert resistor.lib_id == 'Device:R'
        assert resistor.value == '10k'
        assert resistor.position.x == 100.0
        assert resistor.position.y == 100.0
    
    def test_property_management_api(self):
        """Test that property management API works as documented."""
        sch = ksa.create_schematic("property_api_test")
        
        resistor = sch.components.add('Device:R', 'R1', '10k')
        
        # Test property setting as documented
        resistor.footprint = 'Resistor_SMD:R_0603_1608Metric'
        resistor.set_property('MPN', 'RC0603FR-0710KL')
        
        # Verify API works
        assert resistor.footprint == 'Resistor_SMD:R_0603_1608Metric'
        assert resistor.get_property('MPN') == 'RC0603FR-0710KL'
    
    def test_bulk_operations_api(self):
        """Test bulk operations API as documented."""
        sch = ksa.create_schematic("bulk_test")
        
        # Add multiple resistors
        for i in range(5):
            sch.components.add('Device:R', f'R{i+1}', '10k')
        
        # Test bulk update as documented in CLAUDE.md
        updated_count = sch.components.bulk_update(
            criteria={'lib_id': 'Device:R'},
            updates={'properties': {'Tolerance': '1%'}}
        )
        
        assert updated_count == 5
        
        # Verify all resistors were updated
        for comp in sch.components.filter(lib_id='Device:R'):
            assert comp.get_property('Tolerance') == '1%'
    
    def test_save_api_compatibility(self):
        """Test that save API matches documentation."""
        sch = ksa.create_schematic("save_test")
        sch.components.add('Device:R', 'R1', '10k')
        
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        # Test save API as documented
        sch.save(temp_path)
        
        # Verify file was created and is loadable
        assert Path(temp_path).exists()
        
        # Test that saved file can be loaded back
        reloaded = ksa.load_schematic(temp_path)
        assert len(reloaded.components) == 1
        assert reloaded.components.get('R1') is not None
        
        # Clean up
        Path(temp_path).unlink()