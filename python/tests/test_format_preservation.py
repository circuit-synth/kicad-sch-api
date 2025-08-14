"""
Tests specifically for exact format preservation.
Critical for ensuring professional output quality.
"""

import pytest
import tempfile
from pathlib import Path

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.parser import SExpressionParser
from kicad_sch_api.core.formatter import ExactFormatter


class TestFormatPreservation:
    """Test exact format preservation capabilities."""

    def test_round_trip_preserves_structure(self, sample_schematic_file):
        """Test that loading and saving preserves schematic structure."""
        # Load original
        sch = Schematic.load(sample_schematic_file)
        
        # Save without modifications
        output_path = sample_schematic_file.with_suffix('.output.kicad_sch')
        sch.save(output_path, preserve_format=True)
        
        # Compare structures
        with open(sample_schematic_file, 'r') as f:
            original = f.read()
        with open(output_path, 'r') as f:
            output = f.read()
        
        # Key structural elements should be preserved
        assert original.count('(symbol') == output.count('(symbol')
        assert original.count('(property') == output.count('(property')
        assert original.count('(lib_symbols') == output.count('(lib_symbols')
        assert original.count('(symbol_instances') == output.count('(symbol_instances')
        
        # Content should be preserved
        assert '(version 20250114)' in output
        assert '(generator "eeschema")' in output
        assert '"Reference" "R1"' in output
        assert '"Value" "10k"' in output

    def test_add_component_preserves_formatting(self, blank_schematic_file):
        """Test that adding components preserves existing formatting."""
        # Load blank schematic
        sch = Schematic.load(blank_schematic_file)
        
        # Add component
        sch.components.add("Device:R", "R1", "10k", (100, 50))
        sch.save(preserve_format=True)
        
        # Check output formatting
        with open(blank_schematic_file, 'r') as f:
            content = f.read()
        
        # Should maintain KiCAD's standard formatting
        lines = content.split('\n')
        
        # Find component section
        symbol_line = None
        for i, line in enumerate(lines):
            if '(symbol (lib_id "Device:R")' in line:
                symbol_line = i
                break
        
        assert symbol_line is not None
        
        # Check indentation is consistent
        property_lines = []
        for i in range(symbol_line + 1, len(lines)):
            if '(property' in lines[i]:
                property_lines.append(lines[i])
            elif lines[i].strip() == ')' and len(property_lines) > 0:
                break
        
        # Properties should be properly indented
        for line in property_lines:
            assert line.startswith('\t\t(property')  # Double tab indentation

    def test_formatter_exact_output(self):
        """Test that formatter produces exact KiCAD-compatible output."""
        formatter = ExactFormatter()
        
        # Test property formatting (critical for KiCAD compatibility)
        import sexpdata
        property_data = [
            sexpdata.Symbol('property'),
            'Reference',
            'R1',
            [sexpdata.Symbol('at'), 100, 50, 0],
            [sexpdata.Symbol('effects'), 
                [sexpdata.Symbol('font'), 
                    [sexpdata.Symbol('size'), 1.27, 1.27]]]
        ]
        
        formatted = formatter._format_property(property_data, 2)
        
        # Should match KiCAD's property format
        assert '(property "Reference" "R1"' in formatted
        assert '(at 100 50 0)' in formatted
        assert '(effects' in formatted
        assert '(font' in formatted

    def test_sexpression_quoting_rules(self):
        """Test that S-expression quoting follows KiCAD conventions."""
        formatter = ExactFormatter()
        
        # Test strings that need quoting
        assert formatter._needs_quoting("Device:R") is False  # No spaces
        assert formatter._needs_quoting("Reference") is False  # Simple identifier
        assert formatter._needs_quoting("My Component") is True  # Has space
        assert formatter._needs_quoting("") is True  # Empty string
        assert formatter._needs_quoting("R(1)") is True  # Has parentheses

    def test_indentation_consistency(self):
        """Test that indentation follows KiCAD conventions."""
        formatter = ExactFormatter()
        
        # Test nested structure indentation
        import sexpdata
        nested_data = [
            sexpdata.Symbol('symbol'),
            [sexpdata.Symbol('lib_id'), 'Device:R'],
            [sexpdata.Symbol('property'), 'Reference', 'R1',
                [sexpdata.Symbol('at'), 100, 50, 0]
            ]
        ]
        
        formatted = formatter.format(nested_data)
        lines = formatted.split('\n')
        
        # Check indentation levels
        for line in lines:
            if '(lib_id' in line:
                assert line.startswith('\t')  # First level indent
            elif '(at 100 50 0)' in line:
                assert line.startswith('\t\t')  # Second level indent

    def test_format_preservation_with_modifications(self, sample_schematic_file):
        """Test format preservation when making modifications."""
        # Read original
        with open(sample_schematic_file, 'r') as f:
            original_content = f.read()
        
        # Load, modify, and save
        sch = Schematic.load(sample_schematic_file)
        
        # Make a simple modification
        comp = sch.components.get("R1")
        if comp:
            comp.value = "22k"  # Change value
        
        sch.save(preserve_format=True)
        
        # Read modified content
        with open(sample_schematic_file, 'r') as f:
            modified_content = f.read()
        
        # Should preserve overall structure
        assert modified_content.count('\n') == original_content.count('\n') or \
               abs(modified_content.count('\n') - original_content.count('\n')) <= 2
        
        # Should have updated value
        assert '"Value" "22k"' in modified_content
        assert '"Value" "10k"' not in modified_content

    def test_complex_schematic_format_preservation(self, temp_dir):
        """Test format preservation with complex schematic operations."""
        # Create complex schematic
        sch = Schematic.create("Complex Test")
        
        # Add multiple components with various properties
        for i in range(5):
            comp = sch.components.add(
                lib_id="Device:R",
                reference=f"R{i+1}",
                value=f"{(i+1)*10}k",
                position=(i*30, 50),
                footprint="Resistor_SMD:R_0603_1608Metric"
            )
            comp.set_property("MPN", f"RC0603FR-07{i+1}0KL")
            comp.set_property("Tolerance", "1%")
        
        # Save and reload
        sch_path = temp_dir / "complex.kicad_sch"
        sch.save(sch_path)
        
        # Reload and verify
        sch2 = Schematic.load(sch_path)
        
        assert len(sch2.components) == 5
        
        # Verify properties preserved
        for i in range(5):
            comp = sch2.components.get(f"R{i+1}")
            assert comp is not None
            assert comp.value == f"{(i+1)*10}k"
            assert comp.get_property("MPN") == f"RC0603FR-07{i+1}0KL"
            assert comp.get_property("Tolerance") == "1%"

    def test_parser_error_recovery(self):
        """Test parser error handling and recovery."""
        parser = SExpressionParser()
        
        # Test invalid S-expression
        with pytest.raises(Exception):  # Should be ValidationError
            parser.parse_string("invalid content")
        
        # Test malformed schematic
        malformed = "(kicad_sch (version invalid) (missing closing paren"
        with pytest.raises(Exception):
            parser.parse_string(malformed)

    def test_validation_integration(self, temp_dir):
        """Test integration between parsing and validation."""
        # Create schematic with validation issues
        sch = Schematic.create("Validation Test")
        
        # This should work fine
        sch.components.add("Device:R", "R1", "10k")
        
        # Validate
        issues = sch.validate()
        errors = [issue for issue in issues if issue.level.value in ('error', 'critical')]
        
        # Should be no errors with valid schematic
        assert len(errors) == 0
        
        # Save should succeed
        sch_path = temp_dir / "validation_test.kicad_sch"
        sch.save(sch_path)  # Should not raise ValidationError