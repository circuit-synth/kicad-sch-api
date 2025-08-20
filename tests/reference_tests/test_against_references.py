#!/usr/bin/env python3
"""
Test framework that runs test scripts and compares output against reference KiCAD projects.

This framework:
1. Executes each test_*.py file from the reference_tests directory
2. Compares generated .kicad_sch files against reference projects
3. Reports exact format preservation and functional correctness
"""

import difflib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest


class TestAgainstReferences:
    """Test suite that validates generated schematics against KiCAD references."""

    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent.parent.parent
        cls.test_dir = Path(__file__).parent  # reference_tests directory
        cls.reference_dir = Path(__file__).parent / "reference_kicad_projects"
        cls.test_scripts = list(cls.test_dir.glob("test_*.py"))

        # Mapping of test script names to reference project names
        cls.test_to_reference = {
            "test_single_resistor.py": "single_resistor",
            "test_two_resistors.py": "two_resistors",
            "test_resistor_divider.py": "resistor_divider",
            "test_single_wire.py": "single_wire",
            "test_single_label.py": "single_label",
            "test_single_label_hierarchical.py": "single_label_hierarchical",
            "test_single_text.py": "single_text",
            "test_single_text_box.py": "single_text_box",
            "test_single_hierarchical_sheet.py": "single_hierarchical_sheet",
            "test_blank_schematic.py": "blank_schematic",
            "test_multi_component.py": None,  # No reference for this yet
        }

    def _run_test_script(self, script_path: Path) -> Tuple[bool, str, Optional[Path]]:
        """
        Run a test script and return success status, output, and generated file path.

        Args:
            script_path: Path to the test script

        Returns:
            (success, output, generated_file_path)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Modify the script to output to temp directory
            script_name = script_path.stem
            output_file = Path(tmpdir) / f"{script_name}.kicad_sch"

            # Read the script and modify the output path
            with open(script_path, "r") as f:
                script_content = f.read()

            # Replace the save path to use temp directory
            modified_script = script_content.replace(
                f'"{script_name}.kicad_sch"', f'"{output_file}"'
            )

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
                    # Copy the content for comparison
                    with open(output_file, "r") as f:
                        generated_content = f.read()

                    # Save to a temporary file that persists after tmpdir is deleted
                    persistent_file = Path(tmpdir).parent / f"{script_name}_generated.kicad_sch"
                    with open(persistent_file, "w") as f:
                        f.write(generated_content)

                    return success, output, persistent_file
                else:
                    return success, output, None

            except subprocess.TimeoutExpired:
                return False, "Test script timed out", None
            except Exception as e:
                return False, f"Error running script: {e}", None

    def _compare_schematics(self, generated_path: Path, reference_path: Path) -> Tuple[bool, str]:
        """
        Compare generated schematic with reference.

        Args:
            generated_path: Path to generated schematic
            reference_path: Path to reference schematic

        Returns:
            (is_identical, diff_output)
        """
        with open(generated_path, "r") as f:
            generated = f.read()

        with open(reference_path, "r") as f:
            reference = f.read()

        if generated == reference:
            return True, "Files are identical"

        # Generate diff
        diff = difflib.unified_diff(
            reference.splitlines(keepends=True),
            generated.splitlines(keepends=True),
            fromfile=str(reference_path),
            tofile=str(generated_path),
            n=3,
        )

        diff_output = "".join(diff)
        return False, diff_output

    def _normalize_for_comparison(self, content: str) -> str:
        """
        Normalize schematic content for semantic comparison.

        This removes elements that can vary but don't affect functionality:
        - UUIDs
        - Timestamps
        - Generator version details
        """
        lines = content.split("\n")
        normalized = []

        for line in lines:
            # Skip UUID lines (they're auto-generated)
            if "uuid" in line.lower():
                continue
            # Skip generator version lines
            if "generator_version" in line:
                continue
            # Keep everything else
            normalized.append(line)

        return "\n".join(normalized)

    def test_single_resistor(self):
        """Test single resistor generation against reference."""
        script_path = self.test_dir / "test_single_resistor.py"
        reference_name = self.test_to_reference[script_path.name]

        if not reference_name:
            pytest.skip(f"No reference project for {script_path.name}")

        reference_path = self.reference_dir / reference_name / f"{reference_name}.kicad_sch"

        # Run the test script
        success, output, generated_path = self._run_test_script(script_path)

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Compare with reference
        is_identical, diff = self._compare_schematics(generated_path, reference_path)

        if not is_identical:
            # Try semantic comparison (ignoring UUIDs, etc)
            with open(generated_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(reference_path, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print(f"✅ {script_path.name}: Semantically equivalent (UUIDs differ)")
            else:
                print(f"❌ {script_path.name}: Files differ")
                print("Diff output:")
                print(diff[:2000])  # Show first 2000 chars of diff
                pytest.fail("Generated schematic differs from reference")
        else:
            print(f"✅ {script_path.name}: Exact match with reference")

        # Clean up
        if generated_path and generated_path.exists():
            generated_path.unlink()

    def test_two_resistors(self):
        """Test two resistors generation against reference."""
        script_path = self.test_dir / "test_two_resistors.py"
        reference_name = self.test_to_reference[script_path.name]

        if not reference_name:
            pytest.skip(f"No reference project for {script_path.name}")

        reference_path = self.reference_dir / reference_name / f"{reference_name}.kicad_sch"

        # Run the test script
        success, output, generated_path = self._run_test_script(script_path)

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Compare with reference
        is_identical, diff = self._compare_schematics(generated_path, reference_path)

        if not is_identical:
            # Try semantic comparison
            with open(generated_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(reference_path, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print(f"✅ {script_path.name}: Semantically equivalent (UUIDs differ)")
            else:
                print(f"❌ {script_path.name}: Files differ")
                print("Diff output:")
                print(diff[:2000])
                pytest.fail("Generated schematic differs from reference")
        else:
            print(f"✅ {script_path.name}: Exact match with reference")

        # Clean up
        if generated_path and generated_path.exists():
            generated_path.unlink()

    def test_blank_schematic(self):
        """Test blank schematic generation against reference."""
        script_path = self.test_dir / "test_blank_schematic.py"
        reference_name = self.test_to_reference[script_path.name]

        if not reference_name:
            pytest.skip(f"No reference project for {script_path.name}")

        reference_path = self.reference_dir / reference_name / f"{reference_name}.kicad_sch"

        # Run the test script
        success, output, generated_path = self._run_test_script(script_path)

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Compare with reference
        is_identical, diff = self._compare_schematics(generated_path, reference_path)

        if not is_identical:
            # Try semantic comparison
            with open(generated_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(reference_path, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print(f"✅ {script_path.name}: Semantically equivalent (UUIDs differ)")
            else:
                print(f"❌ {script_path.name}: Files differ")
                print("Diff output:")
                print(diff[:2000])
                pytest.fail("Generated schematic differs from reference")
        else:
            print(f"✅ {script_path.name}: Exact match with reference")

        # Clean up
        if generated_path and generated_path.exists():
            generated_path.unlink()

    # TODO: Add more test methods for other test scripts as they're implemented

    def test_single_wire(self):
        """Test single wire generation against reference."""
        script_path = self.test_dir / "test_single_wire.py"
        reference_name = self.test_to_reference[script_path.name]

        if not reference_name:
            pytest.skip(f"No reference project for {script_path.name}")

        reference_path = self.reference_dir / reference_name / f"{reference_name}.kicad_sch"

        # Run the test script
        success, output, generated_path = self._run_test_script(script_path)

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Compare with reference
        is_identical, diff = self._compare_schematics(generated_path, reference_path)

        if not is_identical:
            # Try semantic comparison
            with open(generated_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(reference_path, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print(f"✅ {script_path.name}: Semantically equivalent (UUIDs differ)")
            else:
                print(f"❌ {script_path.name}: Files differ")
                print("Diff output:")
                print(diff[:2000])
                pytest.fail("Generated schematic differs from reference")
        else:
            print(f"✅ {script_path.name}: Exact match with reference")

        # Clean up
        if generated_path and generated_path.exists():
            generated_path.unlink()

    def test_single_label(self):
        """Test single label generation against reference."""
        script_path = self.test_dir / "test_single_label.py"
        reference_name = self.test_to_reference[script_path.name]

        if not reference_name:
            pytest.skip(f"No reference project for {script_path.name}")

        reference_path = self.reference_dir / reference_name / f"{reference_name}.kicad_sch"

        # Run the test script
        success, output, generated_path = self._run_test_script(script_path)

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Compare with reference
        is_identical, diff = self._compare_schematics(generated_path, reference_path)

        if not is_identical:
            # Try semantic comparison
            with open(generated_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(reference_path, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print(f"✅ {script_path.name}: Semantically equivalent (UUIDs differ)")
            else:
                print(f"❌ {script_path.name}: Files differ")
                print("Diff output:")
                print(diff[:2000])
                pytest.fail("Generated schematic differs from reference")
        else:
            print(f"✅ {script_path.name}: Exact match with reference")

        # Clean up
        if generated_path and generated_path.exists():
            generated_path.unlink()

    def test_single_hierarchical_sheet(self):
        """Test hierarchical sheet generation against reference."""
        script_path = self.test_dir / "test_single_hierarchical_sheet.py"
        reference_name = self.test_to_reference[script_path.name]

        if not reference_name:
            pytest.skip(f"No reference project for {script_path.name}")

        reference_path = self.reference_dir / reference_name / f"{reference_name}.kicad_sch"

        # Run the test script
        success, output, generated_path = self._run_test_script(script_path)

        assert success, f"Test script failed: {output}"
        assert generated_path and generated_path.exists(), "No output file generated"

        # Compare with reference
        is_identical, diff = self._compare_schematics(generated_path, reference_path)

        if not is_identical:
            # Try semantic comparison
            with open(generated_path, "r") as f:
                gen_normalized = self._normalize_for_comparison(f.read())
            with open(reference_path, "r") as f:
                ref_normalized = self._normalize_for_comparison(f.read())

            if gen_normalized == ref_normalized:
                print(f"✅ {script_path.name}: Semantically equivalent (UUIDs differ)")
            else:
                print(f"❌ {script_path.name}: Files differ")
                print("Diff output:")
                print(diff[:2000])
                pytest.fail("Generated schematic differs from reference")
        else:
            print(f"✅ {script_path.name}: Exact match with reference")

        # Clean up
        if generated_path and generated_path.exists():
            generated_path.unlink()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
