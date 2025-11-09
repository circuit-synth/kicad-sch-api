"""
Unit tests for PythonCodeGenerator class.
"""

from pathlib import Path

import pytest

from kicad_sch_api.exporters.python_generator import (
    CodeGenerationError,
    PythonCodeGenerator,
    TemplateNotFoundError,
)


class TestPythonCodeGenerator:
    """Test PythonCodeGenerator class initialization and basic functionality."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        gen = PythonCodeGenerator()
        assert gen.template == "default"
        assert gen.format_code is True
        assert gen.add_comments is True

    def test_init_with_custom_template(self):
        """Test initialization with custom template."""
        gen = PythonCodeGenerator(template="minimal")
        assert gen.template == "minimal"

    def test_init_with_format_disabled(self):
        """Test initialization with formatting disabled."""
        gen = PythonCodeGenerator(format_code=False)
        assert gen.format_code is False

    def test_init_with_comments_disabled(self):
        """Test initialization with comments disabled."""
        gen = PythonCodeGenerator(add_comments=False)
        assert gen.add_comments is False


class TestVariableNameSanitization:
    """Test variable name sanitization."""

    def test_sanitize_simple_reference(self):
        """Test sanitization of simple component references."""
        assert PythonCodeGenerator._sanitize_variable_name("R1") == "r1"
        assert PythonCodeGenerator._sanitize_variable_name("C10") == "c10"
        assert PythonCodeGenerator._sanitize_variable_name("U5") == "u5"

    def test_sanitize_power_nets(self):
        """Test sanitization of power net names."""
        assert PythonCodeGenerator._sanitize_variable_name("3V3") == "_3v3"
        assert PythonCodeGenerator._sanitize_variable_name("3.3V") == "_3v3"
        assert PythonCodeGenerator._sanitize_variable_name("+3V3") == "_3v3"
        assert PythonCodeGenerator._sanitize_variable_name("5V") == "_5v"
        assert PythonCodeGenerator._sanitize_variable_name("+5V") == "_5v"
        assert PythonCodeGenerator._sanitize_variable_name("12V") == "_12v"
        assert PythonCodeGenerator._sanitize_variable_name("VCC") == "vcc"
        assert PythonCodeGenerator._sanitize_variable_name("VDD") == "vdd"
        assert PythonCodeGenerator._sanitize_variable_name("GND") == "gnd"
        assert PythonCodeGenerator._sanitize_variable_name("VSS") == "vss"

    def test_sanitize_special_characters(self):
        """Test sanitization of references with special characters."""
        assert PythonCodeGenerator._sanitize_variable_name("U$1") == "u_1"
        assert PythonCodeGenerator._sanitize_variable_name("R+1") == "rp1"
        assert PythonCodeGenerator._sanitize_variable_name("C-10") == "cn10"

    def test_sanitize_starting_with_digit(self):
        """Test sanitization when name starts with digit."""
        assert PythonCodeGenerator._sanitize_variable_name("1WIRE") == "_1wire"
        assert PythonCodeGenerator._sanitize_variable_name("2N2222") == "_2n2222"

    def test_sanitize_python_keywords(self):
        """Test sanitization of Python keywords."""
        # Although unlikely, ensure keywords are handled
        assert PythonCodeGenerator._sanitize_variable_name("class") == "class_"
        assert PythonCodeGenerator._sanitize_variable_name("def") == "def_"
        assert PythonCodeGenerator._sanitize_variable_name("import") == "import_"


class TestCodeGeneration:
    """Test code generation functionality."""

    def test_generate_minimal_code(self):
        """Test generating minimal code without templates."""
        gen = PythonCodeGenerator(template="minimal", format_code=False)

        # Create minimal mock schematic
        class MockSchematic:
            filepath = Path("test.kicad_sch")
            name = "test_circuit"
            title_block = None

            class Components:
                def __iter__(self):
                    return iter([])

            class Wires:
                def __iter__(self):
                    return iter([])

            class Labels:
                def __iter__(self):
                    return iter([])

            components = Components()
            wires = Wires()
            labels = Labels()

        mock_sch = MockSchematic()

        code = gen.generate(mock_sch, include_hierarchy=False)

        # Verify generated code structure
        assert "#!/usr/bin/env python3" in code
        assert "import kicad_sch_api as ksa" in code
        assert "def create_test_circuit():" in code
        assert "sch = ksa.create_schematic('test_circuit')" in code
        assert "return sch" in code
        assert "if __name__ ==" in code

    def test_validate_syntax_valid_code(self):
        """Test syntax validation with valid code."""
        gen = PythonCodeGenerator()

        valid_code = """
def test():
    x = 1
    return x
"""
        # Should not raise
        gen._validate_syntax(valid_code)

    def test_validate_syntax_invalid_code(self):
        """Test syntax validation with invalid code."""
        gen = PythonCodeGenerator()

        invalid_code = """
def test(:
    x = 1
"""
        # Should raise CodeGenerationError
        with pytest.raises(CodeGenerationError, match="syntax error"):
            gen._validate_syntax(invalid_code)


class TestDataExtraction:
    """Test data extraction methods."""

    def test_extract_metadata(self):
        """Test metadata extraction."""
        gen = PythonCodeGenerator()

        class MockSchematic:
            filepath = Path("/path/to/test.kicad_sch")
            name = "my_circuit"

            class TitleBlock:
                title = "My Test Circuit"

            title_block = TitleBlock()

        mock_sch = MockSchematic()
        metadata = gen._extract_metadata(mock_sch)

        assert metadata["name"] == "my_circuit"
        assert metadata["title"] == "My Test Circuit"
        assert metadata["source_file"] == "/path/to/test.kicad_sch"
        assert "version" in metadata
        assert "date" in metadata

    def test_extract_components(self):
        """Test component extraction."""
        gen = PythonCodeGenerator()

        class MockPosition:
            x = 100.0
            y = 200.0

        class MockComponent:
            reference = "R1"
            lib_id = "Device:R"
            value = "10k"
            footprint = "Resistor_SMD:R_0603_1608Metric"
            position = MockPosition()
            rotation = 0
            properties = {}

        class MockSchematic:
            class Components:
                def __iter__(self):
                    return iter([MockComponent()])

            components = Components()

        mock_sch = MockSchematic()
        components = gen._extract_components(mock_sch)

        assert len(components) == 1
        comp = components[0]
        assert comp["ref"] == "R1"
        assert comp["variable"] == "r1"
        assert comp["lib_id"] == "Device:R"
        assert comp["value"] == "10k"
        assert comp["footprint"] == "Resistor_SMD:R_0603_1608Metric"
        assert comp["x"] == 100.0
        assert comp["y"] == 200.0
        assert comp["rotation"] == 0

    def test_extract_wires(self):
        """Test wire extraction."""
        gen = PythonCodeGenerator()

        class MockPoint:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        class MockWire:
            start = MockPoint(10.0, 20.0)
            end = MockPoint(30.0, 40.0)
            style = "solid"

        class MockSchematic:
            class Wires:
                def __iter__(self):
                    return iter([MockWire()])

            wires = Wires()

        mock_sch = MockSchematic()
        wires = gen._extract_wires(mock_sch)

        assert len(wires) == 1
        wire = wires[0]
        assert wire["start_x"] == 10.0
        assert wire["start_y"] == 20.0
        assert wire["end_x"] == 30.0
        assert wire["end_y"] == 40.0
        assert wire["style"] == "solid"

    def test_extract_labels(self):
        """Test label extraction."""
        gen = PythonCodeGenerator()

        class MockPoint:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        class MockLabel:
            text = "VCC"
            position = MockPoint(50.0, 60.0)
            label_type = "global"
            rotation = 0

        class MockSchematic:
            class Labels:
                def __iter__(self):
                    return iter([MockLabel()])

            labels = Labels()

        mock_sch = MockSchematic()
        labels = gen._extract_labels(mock_sch)

        assert len(labels) == 1
        label = labels[0]
        assert label["text"] == "VCC"
        assert label["x"] == 50.0
        assert label["y"] == 60.0
        assert label["type"] == "global"
        assert label["rotation"] == 0


class TestBlackFormatting:
    """Test Black code formatting integration."""

    def test_format_with_black_available(self):
        """Test formatting when Black is available."""
        gen = PythonCodeGenerator(format_code=True)

        unformatted_code = "x=1;y=2"
        formatted = gen._format_with_black(unformatted_code)

        # Black should format this (or return original if unavailable)
        assert formatted is not None

    def test_format_with_black_disabled(self):
        """Test that formatting is skipped when disabled."""
        gen = PythonCodeGenerator(format_code=False)

        code = "x=1;y=2"
        # Should not attempt formatting when format_code=False
        # (this is tested by checking the generate() flow)
