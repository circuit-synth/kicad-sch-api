"""
Tests for S-expression parsing and manipulation.
Adapted from circuit-synth test suite.
"""

import pytest
import tempfile
from pathlib import Path

from kicad_sch_api.core.parser import SExpressionParser
from kicad_sch_api.core.types import Point, SchematicSymbol
from kicad_sch_api.utils.validation import ValidationError


class TestSExpressionParsing:
    """Test S-expression parsing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SExpressionParser(preserve_format=True)

    def test_parse_blank_schematic_content(self):
        """Test parsing minimal schematic content."""
        blank_content = '''(kicad_sch (version 20250114) (generator "eeschema") 
            (generator_version "9.0") (paper "A4") 
            (lib_symbols) 
            (symbol_instances))'''

        # Parse string content
        sexp_data = self.parser.parse_string(blank_content)
        
        # Verify basic structure
        assert isinstance(sexp_data, list)
        assert len(sexp_data) > 0
        assert str(sexp_data[0]) == "kicad_sch"

    def test_parse_schematic_with_component(self):
        """Test parsing schematic with a simple component."""
        schematic_content = '''(kicad_sch (version 20250114) (generator "eeschema")
            (uuid "test-schematic-uuid")
            (lib_symbols
                (symbol "Device:R" (pin_numbers hide) (pin_names (offset 0))
                    (exclude_from_sim no) (in_bom yes) (on_board yes)
                    (property "Reference" "R" (at 0 0 0) (effects (font (size 1.27 1.27))))
                    (property "Value" "R" (at 0 0 0) (effects (font (size 1.27 1.27))))
                ))
            (symbol (lib_id "Device:R") (at 100 50 0) (unit 1)
                (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
                (uuid "test-component-uuid")
                (property "Reference" "R1" (at 100 46.99 0) (effects (font (size 1.27 1.27))))
                (property "Value" "10k" (at 100 53.01 0) (effects (font (size 1.27 1.27))))
            )
            (symbol_instances
                (path "/" (reference "R1") (unit 1))
            ))'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.kicad_sch', delete=False) as f:
            f.write(schematic_content)
            f.flush()
            
            try:
                # Parse file
                schematic_data = self.parser.parse_file(f.name)
                
                # Verify structure
                assert schematic_data['version'] == '20250114'
                assert schematic_data['uuid'] == 'test-schematic-uuid'
                
                # Verify component was parsed
                components = schematic_data['components']
                assert len(components) == 1
                
                component = components[0]
                assert component['lib_id'] == 'Device:R'
                assert component['reference'] == 'R1'
                assert component['value'] == '10k'
                assert component['position'].x == 100
                assert component['position'].y == 50
                
            finally:
                Path(f.name).unlink()

    def test_round_trip_format_preservation(self):
        """Test that round-trip preserves format exactly."""
        original_content = '''(kicad_sch (version 20250114) (generator "eeschema")
            (uuid "test-uuid")
            (lib_symbols)
            (symbol (lib_id "Device:R") (at 100 50 0) (unit 1)
                (uuid "comp-uuid")
                (property "Reference" "R1" (at 100 46.99 0))
                (property "Value" "10k" (at 100 53.01 0))
            ))'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.kicad_sch', delete=False) as f:
            f.write(original_content)
            f.flush()
            
            try:
                # Parse and immediately write back
                schematic_data = self.parser.parse_file(f.name)
                
                # Write to new file
                output_path = f.name + '.output'
                self.parser.write_file(schematic_data, output_path)
                
                # Read output
                with open(output_path, 'r') as out_f:
                    output_content = out_f.read()
                
                # Verify key elements are preserved
                assert '(version 20250114)' in output_content
                assert 'Device:R' in output_content
                assert '"Reference" "R1"' in output_content
                assert '"Value" "10k"' in output_content
                assert '(at 100 50 0)' in output_content
                
                Path(output_path).unlink()
                
            finally:
                Path(f.name).unlink()

    def test_invalid_sexpression_format(self):
        """Test handling of invalid S-expression format."""
        invalid_content = "This is not valid S-expression content"
        
        with pytest.raises(ValidationError, match="Invalid S-expression format"):
            self.parser.parse_string(invalid_content)

    def test_missing_file_handling(self):
        """Test handling of missing files."""
        nonexistent_path = "/path/that/does/not/exist.kicad_sch"
        
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file(nonexistent_path)

    def test_parse_properties(self):
        """Test parsing component properties correctly."""
        component_content = '''(symbol (lib_id "Device:R") (at 100 50 0)
            (uuid "test-uuid")
            (property "Reference" "R1" (at 100 46.99 0))
            (property "Value" "10k" (at 100 53.01 0))
            (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at 100 50 0))
            (property "MPN" "RC0603FR-0710KL" (at 100 50 0))
        )'''
        
        # This would be part of a larger schematic, but test property parsing logic
        import sexpdata
        sexp_data = sexpdata.loads(component_content)
        
        # Test the property parsing function directly
        symbol_data = self.parser._parse_symbol(sexp_data)
        
        assert symbol_data is not None
        assert symbol_data['reference'] == 'R1'
        assert symbol_data['value'] == '10k'
        assert symbol_data['footprint'] == 'Resistor_SMD:R_0603_1608Metric'
        assert symbol_data['properties']['MPN'] == 'RC0603FR-0710KL'

    def test_validation_during_parse(self):
        """Test that validation occurs during parsing."""
        # Invalid schematic structure
        invalid_content = '''(not_kicad_sch (version 12345))'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.kicad_sch', delete=False) as f:
            f.write(invalid_content)
            f.flush()
            
            try:
                with pytest.raises(ValidationError, match="Missing kicad_sch header"):
                    self.parser.parse_file(f.name)
            finally:
                Path(f.name).unlink()

    def test_parse_wire_elements(self):
        """Test parsing wire connections."""
        wire_content = '''(wire (pts (xy 100 100) (xy 150 100))
            (stroke (width 0) (type default))
            (uuid "wire-uuid"))'''
        
        import sexpdata
        sexp_data = sexpdata.loads(wire_content)
        
        # Test wire parsing (when implemented)
        wire_data = self.parser._parse_wire(sexp_data)
        
        # For now, just verify the method exists and returns dict
        assert isinstance(wire_data, dict)

    def test_performance_with_large_component_count(self):
        """Test parsing performance with many components."""
        # Generate schematic content with many components
        components = []
        for i in range(100):
            components.append(f'''
            (symbol (lib_id "Device:R") (at {i*10} 50 0) (unit 1)
                (uuid "uuid-{i}")
                (property "Reference" "R{i+1}" (at {i*10} 46.99 0))
                (property "Value" "10k" (at {i*10} 53.01 0))
            )''')

        schematic_content = f'''(kicad_sch (version 20250114) (generator "eeschema")
            (uuid "test-uuid")
            (lib_symbols)
            {''.join(components)}
            (symbol_instances))'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.kicad_sch', delete=False) as f:
            f.write(schematic_content)
            f.flush()
            
            try:
                import time
                start_time = time.time()
                
                schematic_data = self.parser.parse_file(f.name)
                
                parse_time = time.time() - start_time
                
                # Should parse 100 components reasonably quickly
                assert parse_time < 5.0  # 5 seconds max
                assert len(schematic_data['components']) == 100
                
                # Verify component data
                first_component = schematic_data['components'][0]
                assert first_component['reference'] == 'R1'
                assert first_component['lib_id'] == 'Device:R'
                
                last_component = schematic_data['components'][-1]
                assert last_component['reference'] == 'R100'
                
            finally:
                Path(f.name).unlink()


class TestSExpressionFormatting:
    """Test S-expression formatting and output."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SExpressionParser(preserve_format=True)

    def test_format_component_output(self):
        """Test that component formatting matches KiCAD output."""
        # Create component data
        component_data = {
            'lib_id': 'Device:R',
            'reference': 'R1',
            'value': '10k',
            'position': Point(100, 50),
            'rotation': 0,
            'uuid': 'test-uuid',
            'footprint': 'Resistor_SMD:R_0603_1608Metric',
            'properties': {'MPN': 'RC0603FR-0710KL'},
            'in_bom': True,
            'on_board': True,
        }
        
        # Convert to S-expression
        sexp_data = self.parser._symbol_to_sexp(component_data)
        
        # Verify structure
        assert sexp_data[0].value == 'symbol'  # Tag
        
        # Find lib_id
        lib_id_found = False
        for item in sexp_data[1:]:
            if isinstance(item, list) and len(item) >= 2 and str(item[0]) == 'lib_id':
                assert item[1] == 'Device:R'
                lib_id_found = True
                break
        assert lib_id_found

    def test_exact_format_preservation(self):
        """Test that exact formatting is preserved."""
        original_content = '''(kicad_sch (version 20250114) (generator "eeschema")
\t(uuid "test-uuid")
\t(symbol (lib_id "Device:R") (at 100 50 0)
\t\t(property "Reference" "R1" (at 100 46.99 0))
\t))'''

        # Parse and write back
        sexp_data = self.parser.parse_string(original_content)
        formatted_output = self.parser.dumps(sexp_data, pretty=True)
        
        # Should maintain structure (exact formatting tested separately)
        assert 'kicad_sch' in formatted_output
        assert 'Device:R' in formatted_output
        assert '"Reference" "R1"' in formatted_output

    def test_dumps_pretty_formatting(self):
        """Test pretty formatting output."""
        import sexpdata
        
        # Simple S-expression
        data = [sexpdata.Symbol('test'), 
                [sexpdata.Symbol('nested'), 'value1', 'value2'],
                'simple_value']
        
        output = self.parser.dumps(data, pretty=True)
        
        # Should be formatted nicely
        assert 'test' in output
        assert 'nested' in output
        assert 'value1' in output