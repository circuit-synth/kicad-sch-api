"""
Integration tests for Python export functionality.

These tests use real KiCad reference schematics to verify end-to-end
export functionality.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

import kicad_sch_api as ksa


class TestPythonExportIntegration:
    """Integration tests for schematic to Python export."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_export_simple_schematic(self, temp_dir):
        """Test exporting a simple rotated resistor schematic."""
        # Load reference schematic
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        sch = ksa.Schematic.load(ref_path)

        # Export to Python
        output_path = temp_dir / 'exported.py'
        result = sch.export_to_python(output_path, format_code=False)

        # Verify file was created
        assert result.exists()
        assert result == output_path

        # Read generated code
        code = output_path.read_text()

        # Verify code structure
        assert '#!/usr/bin/env python3' in code
        assert 'import kicad_sch_api as ksa' in code
        assert 'def create_' in code
        assert 'sch = ksa.create_schematic' in code
        assert 'return sch' in code
        assert 'if __name__ ==' in code

    def test_export_with_utility_function(self, temp_dir):
        """Test export using the schematic_to_python utility function."""
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        output_path = temp_dir / 'utility_exported.py'

        # Use utility function
        result = ksa.schematic_to_python(str(ref_path), str(output_path))

        # Verify file was created
        assert result.exists()

        # Verify code is valid Python
        code = output_path.read_text()
        compile(code, str(output_path), 'exec')

    def test_generated_code_is_executable(self, temp_dir):
        """Test that generated Python code can be executed."""
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        # Export
        output_path = temp_dir / 'executable_test.py'
        ksa.schematic_to_python(str(ref_path), str(output_path), format_code=False)

        # Try to execute the generated code
        code = output_path.read_text()

        # Execute in isolated namespace
        exec_globals = {}
        try:
            exec(compile(code, str(output_path), 'exec'), exec_globals)
        except Exception as e:
            pytest.fail(f"Generated code failed to execute: {e}")

    def test_export_with_components(self, temp_dir):
        """Test export of schematic with components."""
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        sch = ksa.Schematic.load(ref_path)
        output_path = temp_dir / 'with_components.py'

        # Export
        sch.export_to_python(output_path, format_code=False)

        # Read code and check for component creation
        code = output_path.read_text()

        # Should have component addition code
        assert '.components.add(' in code or 'components.add(' in code

    def test_export_minimal_template(self, temp_dir):
        """Test export using minimal template."""
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        sch = ksa.Schematic.load(ref_path)
        output_path = temp_dir / 'minimal.py'

        # Export with minimal template
        sch.export_to_python(output_path, template='minimal', format_code=False)

        # Verify file exists and is valid Python
        assert output_path.exists()

        code = output_path.read_text()
        compile(code, str(output_path), 'exec')

    def test_export_without_formatting(self, temp_dir):
        """Test export with formatting disabled."""
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        sch = ksa.Schematic.load(ref_path)
        output_path = temp_dir / 'unformatted.py'

        # Export without formatting
        sch.export_to_python(output_path, format_code=False)

        assert output_path.exists()

    def test_export_preserves_component_properties(self, temp_dir):
        """Test that component properties are preserved in export."""
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        # Load schematic and check what properties exist
        sch = ksa.Schematic.load(ref_path)

        output_path = temp_dir / 'with_props.py'
        sch.export_to_python(output_path, format_code=False)

        code = output_path.read_text()

        # Should have position information
        assert 'position=' in code

    def test_export_file_permissions(self, temp_dir):
        """Test that exported file has executable permissions on Unix."""
        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        sch = ksa.Schematic.load(ref_path)
        output_path = temp_dir / 'executable.py'

        sch.export_to_python(output_path)

        # Check file exists
        assert output_path.exists()

        # On Unix systems, should be executable
        import sys
        if sys.platform != 'win32':
            import stat
            st = output_path.stat()
            # Check if file has execute permission for owner
            assert st.st_mode & stat.S_IXUSR


class TestCLIIntegration:
    """Integration tests for kicad-to-python CLI command."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_cli_basic_usage(self, temp_dir):
        """Test basic CLI usage."""
        from kicad_sch_api.cli.kicad_to_python import main

        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        output_path = temp_dir / 'cli_output.py'

        # Call CLI main function
        args = [str(ref_path), str(output_path)]
        exit_code = main(args)

        # Should succeed
        assert exit_code == 0

        # File should exist
        assert output_path.exists()

        # Should be valid Python
        code = output_path.read_text()
        compile(code, str(output_path), 'exec')

    def test_cli_with_verbose_flag(self, temp_dir):
        """Test CLI with verbose flag."""
        from kicad_sch_api.cli.kicad_to_python import main

        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        output_path = temp_dir / 'verbose_output.py'

        # Call with verbose flag
        args = [str(ref_path), str(output_path), '--verbose']
        exit_code = main(args)

        assert exit_code == 0
        assert output_path.exists()

    def test_cli_with_invalid_input(self, temp_dir):
        """Test CLI with invalid input file."""
        from kicad_sch_api.cli.kicad_to_python import main

        output_path = temp_dir / 'output.py'

        # Call with non-existent file
        args = ['/nonexistent/file.kicad_sch', str(output_path)]
        exit_code = main(args)

        # Should fail
        assert exit_code != 0

    def test_cli_template_selection(self, temp_dir):
        """Test CLI with template selection."""
        from kicad_sch_api.cli.kicad_to_python import main

        ref_path = Path('tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch')

        if not ref_path.exists():
            pytest.skip(f"Reference schematic not found: {ref_path}")

        output_path = temp_dir / 'template_output.py'

        # Call with minimal template
        args = [str(ref_path), str(output_path), '--template', 'minimal']
        exit_code = main(args)

        assert exit_code == 0
        assert output_path.exists()
