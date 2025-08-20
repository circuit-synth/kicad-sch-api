#!/usr/bin/env python3
"""
Simplified test runner that validates test scripts.

This test runner:
1. Executes each test_*.py file from the reference_tests directory
2. Validates that they produce valid KiCAD schematic files
3. Performs basic structural validation
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
import sexpdata


class TestRunner:
    """Test runner that validates generated schematics."""

    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent.parent.parent
        cls.test_dir = Path(__file__).parent  # reference_tests directory
        cls.test_scripts = [
            "test_single_resistor.py",
            "test_two_resistors.py",
            "test_blank_schematic.py",
            "test_resistor_divider.py",
            "test_single_label_hierarchical.py",  # Now implemented!
            "test_single_wire.py",  # Now implemented!
            "test_power_symbols.py",  # Now implemented!
            "test_single_label.py",  # Now implemented!
            "test_single_hierarchical_sheet.py",  # Now implemented!
            "test_single_text.py",  # Now implemented!
            "test_single_text_box.py",  # Now implemented!
            # These require APIs not yet implemented:
            # "test_multi_component.py",
        ]

    def _run_test_script(self, script_name: str) -> Tuple[bool, str, Optional[Path]]:
        """
        Run a test script and return success status, output, and generated file path.

        Args:
            script_name: Name of the test script

        Returns:
            (success, output, generated_file_path)
        """
        script_path = self.test_dir / script_name

        if not script_path.exists():
            return False, f"Script not found: {script_path}", None

        with tempfile.TemporaryDirectory() as tmpdir:
            # Determine output filename
            output_name = script_name.replace(".py", ".kicad_sch")
            output_file = Path(tmpdir) / output_name

            # Read the script and modify the output path
            with open(script_path, "r") as f:
                script_content = f.read()

            # Replace the save path to use temp directory
            modified_script = script_content.replace(f'"{output_name}"', f'"{output_file}"')

            # Remove the subprocess.run line that opens the file
            lines = modified_script.split("\n")
            filtered_lines = [line for line in lines if 'subprocess.run(["open"' not in line]
            modified_script = "\n".join(filtered_lines)

            # Write modified script to temp file
            temp_script = Path(tmpdir) / "test_script.py"
            with open(temp_script, "w") as f:
                f.write(modified_script)

            # Run the script
            try:
                result = subprocess.run(
                    [sys.executable, str(temp_script)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=str(self.project_root),
                )

                success = result.returncode == 0
                output = result.stdout + result.stderr

                # Check if output file was created
                if output_file.exists():
                    # Copy to persistent location for validation
                    persistent_file = Path(tmpdir).parent / output_name
                    with open(output_file, "r") as f:
                        content = f.read()
                    with open(persistent_file, "w") as f:
                        f.write(content)

                    return success, output, persistent_file
                else:
                    return success, output + "\nNo output file generated", None

            except subprocess.TimeoutExpired:
                return False, "Test script timed out", None
            except Exception as e:
                return False, f"Error running script: {e}", None

    def _validate_schematic(self, schematic_path: Path) -> Tuple[bool, str]:
        """
        Validate that a schematic file is valid KiCAD format.

        Args:
            schematic_path: Path to schematic file

        Returns:
            (is_valid, validation_message)
        """
        try:
            with open(schematic_path, "r") as f:
                content = f.read()

            # Parse as S-expression
            parsed = sexpdata.loads(content)

            # Basic structural validation
            if not isinstance(parsed, list):
                return False, "Not a valid S-expression list"

            if len(parsed) == 0 or str(parsed[0]) != "kicad_sch":
                return False, "Not a KiCAD schematic file"

            # Check for required elements
            has_version = False
            has_generator = False
            has_uuid = False
            has_paper = False

            for item in parsed[1:]:
                if isinstance(item, list) and len(item) > 0:
                    key = str(item[0])
                    if key == "version":
                        has_version = True
                    elif key == "generator":
                        has_generator = True
                    elif key == "uuid":
                        has_uuid = True
                    elif key == "paper":
                        has_paper = True

            missing = []
            if not has_version:
                missing.append("version")
            if not has_generator:
                missing.append("generator")
            # UUID is optional (not required for blank schematics)
            if not has_paper:
                missing.append("paper")

            if missing:
                return False, f"Missing required elements: {', '.join(missing)}"

            return True, "Valid KiCAD schematic structure"

        except Exception as e:
            return False, f"Failed to parse schematic: {e}"

    def _count_components(self, schematic_path: Path) -> int:
        """Count the number of components in a schematic."""
        try:
            with open(schematic_path, "r") as f:
                content = f.read()

            parsed = sexpdata.loads(content)

            # Count symbol elements (components)
            component_count = 0
            for item in parsed[1:]:
                if isinstance(item, list) and len(item) > 0:
                    if str(item[0]) == "symbol":
                        # Check if it's not a library symbol definition
                        for subitem in item[1:]:
                            if isinstance(subitem, list) and len(subitem) > 1:
                                if str(subitem[0]) == "lib_id":
                                    component_count += 1
                                    break

            return component_count

        except Exception:
            return -1

    def test_single_resistor(self):
        """Test single resistor generation."""
        success, output, generated_path = self._run_test_script("test_single_resistor.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count
        component_count = self._count_components(generated_path)
        assert component_count == 1, f"Expected 1 component, found {component_count}"

        print(f"✅ test_single_resistor.py: Generated valid schematic with 1 component")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_two_resistors(self):
        """Test two resistors generation."""
        success, output, generated_path = self._run_test_script("test_two_resistors.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count
        component_count = self._count_components(generated_path)
        assert component_count == 2, f"Expected 2 components, found {component_count}"

        print(f"✅ test_two_resistors.py: Generated valid schematic with 2 components")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_blank_schematic(self):
        """Test blank schematic generation."""
        success, output, generated_path = self._run_test_script("test_blank_schematic.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (should be 0 for blank)
        component_count = self._count_components(generated_path)
        assert component_count == 0, f"Expected 0 components, found {component_count}"

        print(f"✅ test_blank_schematic.py: Generated valid blank schematic")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_resistor_divider(self):
        """Test resistor divider generation."""
        success, output, generated_path = self._run_test_script("test_resistor_divider.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (2 resistors + 2 power symbols)
        component_count = self._count_components(generated_path)
        assert component_count == 4, f"Expected 4 components, found {component_count}"

        # Check for wires, junction, and label in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert "wire" in content, "Wires not found in output"
        assert "junction" in content, "Junction not found in output"
        assert 'label "VOUT"' in content, "VOUT label not found in output"
        assert "at 91.44 81.28" in content, "Expected junction position not found"
        assert "xy 100.33 81.28" in content, "Expected wire coordinate not found"

        print(
            f"✅ test_resistor_divider.py: Generated complete resistor divider with components, wires, junction, and VOUT label"
        )

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_single_label_hierarchical(self):
        """Test hierarchical label generation."""
        success, output, generated_path = self._run_test_script("test_single_label_hierarchical.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (should be 0 for hierarchical label only)
        component_count = self._count_components(generated_path)
        assert component_count == 0, f"Expected 0 components, found {component_count}"

        # Check for hierarchical label in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert "hierarchical_label" in content, "Hierarchical label not found in output"
        assert "HIERARCHICAL_LABEL_1" in content, "Expected label text not found"

        print(
            f"✅ test_single_label_hierarchical.py: Generated valid schematic with hierarchical label"
        )

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_single_wire(self):
        """Test single wire generation."""
        success, output, generated_path = self._run_test_script("test_single_wire.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (should be 0 for wire only)
        component_count = self._count_components(generated_path)
        assert component_count == 0, f"Expected 0 components, found {component_count}"

        # Check for wire in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert "wire" in content, "Wire not found in output"
        assert "xy 114.3 63.5" in content, "Expected wire start point not found"
        assert "xy 135.89 63.5" in content, "Expected wire end point not found"

        print(f"✅ test_single_wire.py: Generated valid schematic with wire")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_power_symbols(self):
        """Test power symbols generation."""
        success, output, generated_path = self._run_test_script("test_power_symbols.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (3 power symbols)
        component_count = self._count_components(generated_path)
        assert component_count == 3, f"Expected 3 components, found {component_count}"

        # Check for power symbols in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert "power:+3.3V" in content, "+3.3V power symbol not found"
        assert "power:GND" in content, "GND power symbol not found"
        assert "power:VDD" in content, "VDD power symbol not found"
        assert "(hide yes)" in content, "References should be hidden"

        print(f"✅ test_power_symbols.py: Generated valid schematic with 3 power symbols")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_single_label(self):
        """Test local label generation."""
        success, output, generated_path = self._run_test_script("test_single_label.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (should be 0 for label only)
        component_count = self._count_components(generated_path)
        assert component_count == 0, f"Expected 0 components, found {component_count}"

        # Check for label in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert 'label "LABEL_1"' in content, "Local label not found in output"
        assert "at 130.81 73.66" in content, "Expected label position not found"
        assert "justify left bottom" in content, "Expected label justification not found"

        print(f"✅ test_single_label.py: Generated valid schematic with local label")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_single_hierarchical_sheet(self):
        """Test hierarchical sheet generation."""
        success, output, generated_path = self._run_test_script("test_single_hierarchical_sheet.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (should be 0 for sheet only)
        component_count = self._count_components(generated_path)
        assert component_count == 0, f"Expected 0 components, found {component_count}"

        # Check for sheet in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert "sheet" in content, "Hierarchical sheet not found in output"
        assert "subcircuit1" in content, "Sheet name not found"
        assert "subcircuit1.kicad_sch" in content, "Sheet filename not found"
        assert "at 137.16 69.85" in content, "Expected sheet position not found"
        assert "size 26.67 34.29" in content, "Expected sheet size not found"

        print(
            f"✅ test_single_hierarchical_sheet.py: Generated valid schematic with hierarchical sheet"
        )

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_single_text(self):
        """Test text element generation."""
        success, output, generated_path = self._run_test_script("test_single_text.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (should be 0 for text only)
        component_count = self._count_components(generated_path)
        assert component_count == 0, f"Expected 0 components, found {component_count}"

        # Check for text in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert 'text "Text here"' in content, "Text element not found in output"
        assert "at 127.254 76.454" in content, "Expected text position not found"

        print(f"✅ test_single_text.py: Generated valid schematic with text element")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_single_text_box(self):
        """Test text box element generation."""
        success, output, generated_path = self._run_test_script("test_single_text_box.py")

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Validate schematic structure
        is_valid, msg = self._validate_schematic(generated_path)
        assert is_valid, f"Invalid schematic: {msg}"

        # Check component count (should be 0 for text box only)
        component_count = self._count_components(generated_path)
        assert component_count == 0, f"Expected 0 components, found {component_count}"

        # Check for text box in content
        with open(generated_path, "r") as f:
            content = f.read()
        assert 'text_box "Text box goes here"' in content, "Text box element not found in output"
        assert "at 116.84 71.12" in content, "Expected text box position not found"
        assert "size 59.69 35.56" in content, "Expected text box size not found"
        assert "margins 0.9525" in content, "Expected text box margins not found"

        print(f"✅ test_single_text_box.py: Generated valid schematic with text box element")

        # Clean up
        if generated_path.exists():
            generated_path.unlink()

    def test_all_scripts_exist(self):
        """Verify all expected test scripts exist."""
        missing = []
        for script_name in self.test_scripts:
            script_path = self.test_dir / script_name
            if not script_path.exists():
                missing.append(script_name)

        assert len(missing) == 0, f"Missing test scripts: {', '.join(missing)}"
        print(f"✅ All {len(self.test_scripts)} test scripts found")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
