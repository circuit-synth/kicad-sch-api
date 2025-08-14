"""
KiCAD Visual Compatibility Tests

These tests validate that generated schematics actually render properly
in KiCAD, not just that they have correct semantic data.
"""

import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from kicad_sch_api.core.schematic import Schematic


class TestKiCADVisualCompatibility:
    """Test that generated schematics render properly in KiCAD."""
    
    def test_lib_symbols_section_completeness(self):
        """Test that lib_symbols section contains complete symbol definitions."""
        # Create schematic with components
        sch = Schematic.create("Visual Test")
        sch.components.add('Device:R', reference='R1', value='10k', position=(100, 100))
        sch.components.add('Device:C', reference='C1', value='0.1uF', position=(150, 100))
        
        # Save and analyze
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        sch.save(temp_path)
        
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # CRITICAL: Validate lib_symbols section has substantial content
        assert '(lib_symbols' in content, "Should have lib_symbols section"
        
        # Count lib_symbols lines
        lines = content.split('\n')
        lib_symbols_lines = []
        in_lib_symbols = False
        
        for line in lines:
            if '(lib_symbols' in line:
                in_lib_symbols = True
                lib_symbols_lines.append(line)
            elif in_lib_symbols:
                lib_symbols_lines.append(line)
                if line.strip() == ')' and not line.startswith('\t\t'):
                    break
        
        # CRITICAL: lib_symbols should have substantial content, not be empty
        assert len(lib_symbols_lines) > 10, f"lib_symbols too small: {len(lib_symbols_lines)} lines"
        
        # CRITICAL: Should contain actual symbol definitions
        device_r_symbol = '(symbol "Device:R"'
        device_c_symbol = '(symbol "Device:C"'
        assert device_r_symbol in content, "Should contain Device:R symbol definition"
        assert device_c_symbol in content, "Should contain Device:C symbol definition"
        
        # CRITICAL: Should contain essential symbol elements
        assert '(pin_numbers' in content, "Should have pin numbering definitions"
        assert '(property "Reference"' in content, "Should have reference property templates"
        assert '(property "Value"' in content, "Should have value property templates"
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_symbol_definition_content_quality(self):
        """Test that symbol definitions have sufficient detail for KiCAD rendering."""
        sch = Schematic.create("Content Quality Test")
        sch.components.add('Device:R', reference='R1', value='10k')
        
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        sch.save(temp_path)
        
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # Find the Device:R symbol definition
        lines = content.split('\n')
        symbol_lines = []
        in_device_r = False
        
        for line in lines:
            if '(symbol "Device:R"' in line:
                in_device_r = True
                symbol_lines.append(line)
            elif in_device_r:
                symbol_lines.append(line)
                if line.strip() == ')' and len(symbol_lines) > 5:
                    break
        
        symbol_content = '\n'.join(symbol_lines)
        
        # Validate essential elements for KiCAD compatibility
        required_elements = [
            '(pin_numbers',      # Pin numbering configuration
            '(pin_names',        # Pin naming configuration  
            '(exclude_from_sim', # Simulation settings
            '(in_bom',           # BOM inclusion
            '(on_board',         # Board inclusion
            '(property "Reference"', # Reference property template
            '(property "Value"',     # Value property template
            '(property "Footprint"', # Footprint property template
            '(property "Datasheet"', # Datasheet property template
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in symbol_content:
                missing_elements.append(element)
        
        assert len(missing_elements) == 0, f"Missing required symbol elements: {missing_elements}"
        
        print(f"✅ Device:R symbol definition has {len(symbol_lines)} lines with all required elements")
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_recreated_vs_reference_lib_symbols_comparison(self):
        """Test that recreated lib_symbols sections match reference quality."""
        # Load reference
        ref_path = Path(__file__).parent / "reference_tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch"
        ref_sch = Schematic.load(str(ref_path))
        
        # Create recreation  
        rec_sch = Schematic.create("lib_symbols_test")
        for ref_comp in ref_sch.components:
            rec_sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=(ref_comp.position.x, ref_comp.position.y),
                footprint=ref_comp.footprint
            )
        
        # Save recreation
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        rec_sch.save(temp_path)
        
        # Compare lib_symbols sections
        with open(ref_path, 'r') as f:
            ref_content = f.read()
        
        with open(temp_path, 'r') as f:
            rec_content = f.read()
        
        # Both should have substantial lib_symbols sections
        assert '(lib_symbols' in ref_content, "Reference should have lib_symbols"
        assert '(lib_symbols' in rec_content, "Recreation should have lib_symbols"
        
        # Both should have Device:R symbol definitions
        assert '(symbol "Device:R"' in ref_content, "Reference should have Device:R symbol"
        assert '(symbol "Device:R"' in rec_content, "Recreation should have Device:R symbol"
        
        print("✅ Both reference and recreation have lib_symbols sections")
        print("⚠️ Note: This test previously would have passed even with empty lib_symbols")
        print("⚠️ Demonstrating the gap in our original testing approach")
        
        # Clean up
        Path(temp_path).unlink()
    
    def test_empty_lib_symbols_detection(self):
        """Test that would catch the original empty lib_symbols bug."""
        # Create schematic
        sch = Schematic.create("Empty Detection Test") 
        sch.components.add('Device:R', reference='R1', value='10k')
        
        # Manually break the lib_symbols to simulate the original bug
        sch._data['lib_symbols'] = {}  # Force empty like the original bug
        
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        sch.save(temp_path)
        
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # This test should FAIL if lib_symbols is truly empty (like the original bug)
        lines = content.split('\n')
        lib_symbols_lines = []
        in_lib = False
        
        for line in lines:
            if '(lib_symbols' in line:
                in_lib = True
                lib_symbols_lines.append(line)
            elif in_lib:
                lib_symbols_lines.append(line)
                if line.strip() == ')' and not line.startswith('\t\t'):
                    break
        
        # CRITICAL TEST: This should catch empty lib_symbols
        is_essentially_empty = len(lib_symbols_lines) <= 2  # Just (lib_symbols) and )
        
        if is_essentially_empty:
            print(f"❌ DETECTED: Empty lib_symbols section ({len(lib_symbols_lines)} lines)")
            print("❌ This would cause ?? symbols in KiCAD")
            pytest.fail("Empty lib_symbols detected - would cause ?? symbols in KiCAD")
        else:
            print(f"✅ lib_symbols section has content ({len(lib_symbols_lines)} lines)")
        
        # Clean up
        Path(temp_path).unlink()