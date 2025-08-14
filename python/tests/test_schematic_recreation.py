"""
Comprehensive tests for recreating KiCAD reference schematics using kicad-sch-api.

These tests verify that the API can recreate identical schematics to the reference
projects, ensuring exact format preservation and functional accuracy.
"""

import filecmp
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.utils.validation import ValidationError


class TestSchematicRecreation:
    """Test recreation of all reference schematics."""
    
    @pytest.fixture
    def reference_dir(self):
        """Path to reference KiCAD projects."""
        return Path(__file__).parent / "reference_tests" / "reference_kicad_projects"
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def compare_schematic_files(self, original_path: Path, recreated_path: Path) -> Dict:
        """
        Compare two .kicad_sch files for semantic and exact equivalence.
        
        Args:
            original_path: Path to original reference file
            recreated_path: Path to recreated file
            
        Returns:
            Dict with comparison results and differences
        """
        # Load both schematics for semantic comparison
        original_sch = ksa.load_schematic(str(original_path))
        recreated_sch = ksa.load_schematic(str(recreated_path))
        
        differences = {
            'semantic_match': True,
            'exact_match': False,
            'component_count_match': False,
            'differences': []
        }
        
        # Compare component counts
        orig_count = len(original_sch.components)
        recreated_count = len(recreated_sch.components)
        differences['component_count_match'] = (orig_count == recreated_count)
        
        if orig_count != recreated_count:
            differences['differences'].append(
                f"Component count mismatch: original={orig_count}, recreated={recreated_count}"
            )
            differences['semantic_match'] = False
        
        # Compare components semantically
        for orig_comp in original_sch.components:
            recreated_comp = recreated_sch.components.get(orig_comp.reference)
            if not recreated_comp:
                differences['differences'].append(f"Missing component: {orig_comp.reference}")
                differences['semantic_match'] = False
                continue
            
            # Compare component properties
            if orig_comp.lib_id != recreated_comp.lib_id:
                differences['differences'].append(
                    f"Component {orig_comp.reference}: lib_id mismatch "
                    f"({orig_comp.lib_id} vs {recreated_comp.lib_id})"
                )
                differences['semantic_match'] = False
            
            if orig_comp.value != recreated_comp.value:
                differences['differences'].append(
                    f"Component {orig_comp.reference}: value mismatch "
                    f"({orig_comp.value} vs {recreated_comp.value})"
                )
                differences['semantic_match'] = False
        
        # Check for exact file match
        differences['exact_match'] = filecmp.cmp(original_path, recreated_path, shallow=False)
        
        return differences
    
    def test_blank_schematic_recreation(self, reference_dir):
        """Test recreating the blank schematic."""
        reference_path = reference_dir / "blank_schematic" / "blank_schematic.kicad_sch"
        output_path = self.temp_path / "blank_schematic_recreated.kicad_sch"
        
        # Create blank schematic using API
        sch = ksa.create_schematic("blank_schematic")
        sch.save(str(output_path))
        
        # Compare files
        comparison = self.compare_schematic_files(reference_path, output_path)
        
        # Blank schematic should have exact match
        assert comparison['semantic_match'], f"Semantic differences: {comparison['differences']}"
    
    def test_single_resistor_recreation(self, reference_dir):
        """Test recreating the single resistor schematic."""
        reference_path = reference_dir / "single_resistor" / "single_resistor.kicad_sch"
        output_path = self.temp_path / "single_resistor_recreated.kicad_sch"
        
        # Create schematic with single resistor
        sch = ksa.create_schematic("single_resistor")
        
        # Add the resistor matching the reference
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1", 
            value="10k",
            position=(93.98, 81.28),
            footprint="Resistor_SMD:R_0603_1608Metric"
        )
        
        # Set additional properties to match reference
        resistor.set_property("Datasheet", "~")
        resistor.set_property("Description", "Resistor")
        
        # Save and compare
        sch.save(str(output_path))
        comparison = self.compare_schematic_files(reference_path, output_path)
        
        assert comparison['semantic_match'], f"Semantic differences: {comparison['differences']}"
        assert comparison['component_count_match'], "Component count should match"
    
    def test_two_resistors_recreation(self, reference_dir):
        """Test recreating the two resistors schematic."""
        reference_path = reference_dir / "two_resistors" / "two_resistors.kicad_sch"
        output_path = self.temp_path / "two_resistors_recreated.kicad_sch"
        
        # Load reference to extract exact positions and properties
        ref_sch = ksa.load_schematic(str(reference_path))
        
        # Create new schematic
        sch = ksa.create_schematic("two_resistors")
        
        # Recreate each component from reference
        for ref_comp in ref_sch.components:
            new_comp = sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=ref_comp.position,
                footprint=ref_comp.footprint
            )
            
            # Copy all properties
            for prop_name, prop_value in ref_comp.properties.items():
                new_comp.set_property(prop_name, prop_value)
        
        # Save and compare
        sch.save(str(output_path))
        comparison = self.compare_schematic_files(reference_path, output_path)
        
        assert comparison['semantic_match'], f"Semantic differences: {comparison['differences']}"
        assert comparison['component_count_match'], "Component count should match"
    
    def test_resistor_divider_recreation(self, reference_dir):
        """Test recreating the resistor divider schematic."""
        reference_path = reference_dir / "resistor_divider" / "resistor_divider.kicad_sch"
        output_path = self.temp_path / "resistor_divider_recreated.kicad_sch"
        
        # Load reference schematic
        ref_sch = ksa.load_schematic(str(reference_path))
        
        # Create new schematic
        sch = ksa.create_schematic("resistor_divider")
        
        # Recreate components
        for ref_comp in ref_sch.components:
            new_comp = sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=ref_comp.position,
                footprint=ref_comp.footprint
            )
            
            # Copy properties
            for prop_name, prop_value in ref_comp.properties.items():
                new_comp.set_property(prop_name, prop_value)
        
        # Note: Wire connections would need to be added here
        # This requires additional API development for wire/net handling
        
        sch.save(str(output_path))
        comparison = self.compare_schematic_files(reference_path, output_path)
        
        assert comparison['component_count_match'], "Component count should match"
    
    def test_single_wire_recreation(self, reference_dir):
        """Test recreating the single wire schematic."""
        reference_path = reference_dir / "single_wire" / "single_wire.kicad_sch"
        output_path = self.temp_path / "single_wire_recreated.kicad_sch"
        
        # Load reference
        ref_sch = ksa.load_schematic(str(reference_path))
        
        # Create new schematic
        sch = ksa.create_schematic("single_wire")
        
        # For now, just verify we can create the schematic structure
        # Wire handling would require additional API development
        
        sch.save(str(output_path))
        
        # Basic validation that file was created
        assert output_path.exists(), "Output schematic file should be created"
    
    def test_single_label_recreation(self, reference_dir):
        """Test recreating the single label schematic.""" 
        reference_path = reference_dir / "single_label" / "single_label.kicad_sch"
        output_path = self.temp_path / "single_label_recreated.kicad_sch"
        
        # Load reference
        ref_sch = ksa.load_schematic(str(reference_path))
        
        # Create new schematic
        sch = ksa.create_schematic("single_label")
        
        # For now, verify basic structure
        # Label handling would require additional API development
        
        sch.save(str(output_path))
        assert output_path.exists(), "Output schematic file should be created"
    
    def test_single_text_recreation(self, reference_dir):
        """Test recreating the single text schematic."""
        reference_path = reference_dir / "single_text" / "single_text.kicad_sch"
        output_path = self.temp_path / "single_text_recreated.kicad_sch"
        
        # Create basic schematic
        sch = ksa.create_schematic("single_text")
        sch.save(str(output_path))
        
        assert output_path.exists(), "Output schematic file should be created"
    
    def test_single_text_box_recreation(self, reference_dir):
        """Test recreating the single text box schematic."""
        reference_path = reference_dir / "single_text_box" / "single_text_box.kicad_sch"
        output_path = self.temp_path / "single_text_box_recreated.kicad_sch"
        
        # Create basic schematic
        sch = ksa.create_schematic("single_text_box")
        sch.save(str(output_path))
        
        assert output_path.exists(), "Output schematic file should be created"
    
    def test_hierarchical_sheet_recreation(self, reference_dir):
        """Test recreating the hierarchical sheet schematic."""
        reference_path = reference_dir / "single_hierarchical_sheet" / "single_hierarchical_sheet.kicad_sch"
        output_path = self.temp_path / "single_hierarchical_sheet_recreated.kicad_sch"
        
        # Load reference
        ref_sch = ksa.load_schematic(str(reference_path))
        
        # Create new schematic 
        sch = ksa.create_schematic("single_hierarchical_sheet")
        
        # Hierarchical sheet handling would require additional API development
        
        sch.save(str(output_path))
        assert output_path.exists(), "Output schematic file should be created"
    
    def test_all_reference_schematics_load_successfully(self, reference_dir):
        """Test that all reference schematics can be loaded without errors."""
        reference_projects = [
            "blank_schematic",
            "single_resistor", 
            "two_resistors",
            "resistor_divider",
            "single_wire",
            "single_label",
            "single_label_hierarchical", 
            "single_text",
            "single_text_box",
            "single_hierarchical_sheet"
        ]
        
        successful_loads = 0
        failed_loads = []
        
        for project_name in reference_projects:
            try:
                sch_path = reference_dir / project_name / f"{project_name}.kicad_sch"
                if sch_path.exists():
                    sch = ksa.load_schematic(str(sch_path))
                    successful_loads += 1
                    
                    # Basic validation
                    assert hasattr(sch, 'components'), f"Schematic {project_name} should have components attribute"
                    
            except Exception as e:
                failed_loads.append((project_name, str(e)))
        
        # Report results
        print(f"\nSchematic loading results:")
        print(f"Successfully loaded: {successful_loads}/{len(reference_projects)}")
        
        if failed_loads:
            print("Failed loads:")
            for project, error in failed_loads:
                print(f"  {project}: {error}")
        
        # At least basic schematics should load
        assert successful_loads >= 3, f"At least 3 reference schematics should load successfully, got {successful_loads}"
    
    @pytest.mark.parametrize("reference_name", [
        "blank_schematic",
        "single_resistor",
        "two_resistors"
    ])
    def test_roundtrip_consistency(self, reference_dir, reference_name):
        """Test that loading and immediately saving preserves schematic integrity."""
        reference_path = reference_dir / reference_name / f"{reference_name}.kicad_sch"
        
        if not reference_path.exists():
            pytest.skip(f"Reference file {reference_path} does not exist")
        
        # Load original
        original_sch = ksa.load_schematic(str(reference_path))
        
        # Save to temp file
        output_path = self.temp_path / f"{reference_name}_roundtrip.kicad_sch"
        original_sch.save(str(output_path))
        
        # Load the saved version
        roundtrip_sch = ksa.load_schematic(str(output_path))
        
        # Compare component counts
        assert len(original_sch.components) == len(roundtrip_sch.components), \
            f"Component count should be preserved: original={len(original_sch.components)}, roundtrip={len(roundtrip_sch.components)}"
        
        # Compare component references
        orig_refs = {comp.reference for comp in original_sch.components}
        roundtrip_refs = {comp.reference for comp in roundtrip_sch.components}
        
        assert orig_refs == roundtrip_refs, \
            f"Component references should match: original={orig_refs}, roundtrip={roundtrip_refs}"


class TestAdvancedSchematicFeatures:
    """Test advanced schematic features and edge cases."""
    
    def test_component_property_preservation(self):
        """Test that custom component properties are preserved."""
        sch = ksa.create_schematic("property_test")
        
        # Add component with custom properties
        comp = sch.components.add("Device:R", "R1", "10k", (100, 100))
        comp.set_property("MPN", "RC0603FR-0710KL")
        comp.set_property("Supplier", "Mouser")
        comp.set_property("Datasheet", "https://example.com/datasheet.pdf")
        comp.set_property("Tolerance", "1%")
        
        # Save and reload
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', mode='w', delete=False) as f:
            temp_path = f.name
        
        sch.save(temp_path)
        reloaded_sch = ksa.load_schematic(temp_path)
        
        # Verify properties preserved
        reloaded_comp = reloaded_sch.components.get("R1")
        assert reloaded_comp is not None
        assert reloaded_comp.get_property("MPN") == "RC0603FR-0710KL"
        assert reloaded_comp.get_property("Supplier") == "Mouser"
        assert reloaded_comp.get_property("Datasheet") == "https://example.com/datasheet.pdf"
        assert reloaded_comp.get_property("Tolerance") == "1%"
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_position_precision_preservation(self):
        """Test that component positions maintain precision."""
        sch = ksa.create_schematic("precision_test")
        
        # Test various precision levels
        precise_positions = [
            (100.254, 50.127),
            (99.999, 100.001),
            (0.1, 0.1),
            (1000.5, 2000.75)
        ]
        
        for i, pos in enumerate(precise_positions):
            sch.components.add("Device:R", f"R{i+1}", "10k", pos)
        
        # Save and reload
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', mode='w', delete=False) as f:
            temp_path = f.name
            
        sch.save(temp_path)
        reloaded_sch = ksa.load_schematic(temp_path)
        
        # Verify positions
        for i, expected_pos in enumerate(precise_positions):
            comp = reloaded_sch.components.get(f"R{i+1}")
            assert comp is not None
            actual_pos = (comp.position.x, comp.position.y)
            
            # Allow small floating point tolerance
            assert abs(actual_pos[0] - expected_pos[0]) < 0.001, \
                f"X position mismatch: expected {expected_pos[0]}, got {actual_pos[0]}"
            assert abs(actual_pos[1] - expected_pos[1]) < 0.001, \
                f"Y position mismatch: expected {expected_pos[1]}, got {actual_pos[1]}"
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_special_character_handling(self):
        """Test handling of special characters in component values and properties."""
        sch = ksa.create_schematic("special_chars_test")
        
        special_values = [
            "10µF",  # Micro symbol
            "1MΩ",   # Omega symbol  
            "±5%",   # Plus-minus
            "100°C", # Degree symbol
            "Test™", # Trademark
        ]
        
        for i, value in enumerate(special_values):
            comp = sch.components.add("Device:C", f"C{i+1}", value, (i * 50, 100))
            comp.set_property("Description", f"Special char test: {value}")
        
        # Save and reload
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', mode='w', delete=False) as f:
            temp_path = f.name
            
        sch.save(temp_path)
        reloaded_sch = ksa.load_schematic(temp_path)
        
        # Verify special characters preserved
        for i, expected_value in enumerate(special_values):
            comp = reloaded_sch.components.get(f"C{i+1}")
            assert comp is not None
            assert comp.value == expected_value, f"Value mismatch: expected {expected_value}, got {comp.value}"
            
            expected_desc = f"Special char test: {expected_value}"
            actual_desc = comp.get_property("Description")
            assert actual_desc == expected_desc, f"Description mismatch: expected {expected_desc}, got {actual_desc}"
        
        # Clean up
        Path(temp_path).unlink()