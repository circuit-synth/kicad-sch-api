"""
Round-Trip Tests: The Ultimate Validation

These tests verify the complete workflow:
1. Load original KiCad schematic
2. Export to Python code
3. Execute generated Python code
4. Save regenerated schematic
5. Load regenerated schematic
6. Compare original vs regenerated

This is the gold standard test for the export feature.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa


class TestRoundTrip:
    """Round-trip tests: KiCad → Python → KiCad"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp)

    def test_round_trip_rotated_resistor(self, temp_dir):
        """
        Test complete round-trip with rotated resistor schematic.

        This is the definitive test that proves the feature works.
        """
        # Step 1: Load original schematic
        original_path = Path(
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )

        if not original_path.exists():
            pytest.skip(f"Reference schematic not found: {original_path}")

        original_sch = ksa.Schematic.load(original_path)
        original_components = list(original_sch.components)
        original_wires = list(original_sch.wires)
        original_labels = list(original_sch.labels)

        # Step 2: Export to Python
        python_file = temp_dir / "exported.py"
        original_sch.export_to_python(python_file, format_code=False)

        assert python_file.exists()

        # Step 3: Execute generated Python code
        code = python_file.read_text()
        exec_globals = {}
        exec(compile(code, str(python_file), "exec"), exec_globals)

        # Find the create function
        create_func = None
        for name, obj in exec_globals.items():
            if callable(obj) and name.startswith("create_"):
                create_func = obj
                break

        assert create_func is not None, "No create_* function found"

        # Step 4: Create schematic from generated code
        regenerated_sch = create_func()
        regenerated_components = list(regenerated_sch.components)
        regenerated_wires = list(regenerated_sch.wires)
        regenerated_labels = list(regenerated_sch.labels)

        # Step 5: Save regenerated schematic
        regenerated_path = temp_dir / "regenerated.kicad_sch"
        regenerated_sch.save(regenerated_path)

        assert regenerated_path.exists()

        # Step 6: Re-load regenerated schematic
        reloaded_sch = ksa.Schematic.load(regenerated_path)
        reloaded_components = list(reloaded_sch.components)
        reloaded_wires = list(reloaded_sch.wires)
        reloaded_labels = list(reloaded_sch.labels)

        # Step 7: Compare counts
        assert len(original_components) == len(
            reloaded_components
        ), f"Component count mismatch: {len(original_components)} → {len(reloaded_components)}"

        assert len(original_wires) == len(
            reloaded_wires
        ), f"Wire count mismatch: {len(original_wires)} → {len(reloaded_wires)}"

        assert len(original_labels) == len(
            reloaded_labels
        ), f"Label count mismatch: {len(original_labels)} → {len(reloaded_labels)}"

        # Step 8: Compare component details
        for orig_comp, regen_comp in zip(original_components, reloaded_components):
            assert (
                orig_comp.reference == regen_comp.reference
            ), f"Reference mismatch: {orig_comp.reference} → {regen_comp.reference}"

            assert (
                orig_comp.value == regen_comp.value
            ), f"Value mismatch: {orig_comp.value} → {regen_comp.value}"

            assert (
                orig_comp.lib_id == regen_comp.lib_id
            ), f"Lib ID mismatch: {orig_comp.lib_id} → {regen_comp.lib_id}"

        # Step 9: Compare wire positions
        for orig_wire, regen_wire in zip(original_wires, reloaded_wires):
            assert (
                orig_wire.start.x == regen_wire.start.x
            ), f"Wire start X mismatch: {orig_wire.start.x} → {regen_wire.start.x}"

            assert (
                orig_wire.start.y == regen_wire.start.y
            ), f"Wire start Y mismatch: {orig_wire.start.y} → {regen_wire.start.y}"

            assert (
                orig_wire.end.x == regen_wire.end.x
            ), f"Wire end X mismatch: {orig_wire.end.x} → {regen_wire.end.x}"

            assert (
                orig_wire.end.y == regen_wire.end.y
            ), f"Wire end Y mismatch: {orig_wire.end.y} → {regen_wire.end.y}"

    def test_round_trip_with_utility_function(self, temp_dir):
        """Test round-trip using the utility function."""
        original_path = Path(
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )

        if not original_path.exists():
            pytest.skip(f"Reference schematic not found: {original_path}")

        # Load original
        original_sch = ksa.Schematic.load(original_path)
        original_comp_count = len(list(original_sch.components))

        # Export using utility function
        python_file = temp_dir / "utility_export.py"
        ksa.schematic_to_python(str(original_path), str(python_file))

        # Execute
        code = python_file.read_text()
        exec_globals = {}
        exec(compile(code, str(python_file), "exec"), exec_globals)

        # Find and call create function
        create_func = next(
            (
                obj
                for name, obj in exec_globals.items()
                if callable(obj) and name.startswith("create_")
            ),
            None,
        )

        assert create_func is not None

        # Create and verify
        regenerated_sch = create_func()
        regenerated_comp_count = len(list(regenerated_sch.components))

        assert original_comp_count == regenerated_comp_count

    def test_round_trip_preserves_wire_connectivity(self, temp_dir):
        """Test that wire connectivity is preserved through round-trip."""
        original_path = Path(
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )

        if not original_path.exists():
            pytest.skip(f"Reference schematic not found: {original_path}")

        # Export and execute
        python_file = temp_dir / "wire_test.py"
        ksa.schematic_to_python(str(original_path), str(python_file))

        code = python_file.read_text()
        exec_globals = {}
        exec(compile(code, str(python_file), "exec"), exec_globals)

        create_func = next(
            (
                obj
                for name, obj in exec_globals.items()
                if callable(obj) and name.startswith("create_")
            ),
            None,
        )

        regenerated_sch = create_func()

        # Save and reload
        output_path = temp_dir / "wire_output.kicad_sch"
        regenerated_sch.save(output_path)
        reloaded_sch = ksa.Schematic.load(output_path)

        # Verify wires exist
        wires = list(reloaded_sch.wires)
        assert len(wires) > 0, "No wires found after round-trip"

        # Verify wire positions are valid (not all zeros)
        for wire in wires:
            assert not (
                wire.start.x == 0 and wire.start.y == 0 and wire.end.x == 0 and wire.end.y == 0
            ), "Wire has all-zero coordinates"

    def test_round_trip_generated_code_is_idempotent(self, temp_dir):
        """
        Test that running generated code multiple times produces same result.

        This verifies that the generated code is deterministic.
        """
        original_path = Path(
            "tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch"
        )

        if not original_path.exists():
            pytest.skip(f"Reference schematic not found: {original_path}")

        # Export once
        python_file = temp_dir / "idempotent_test.py"
        ksa.schematic_to_python(str(original_path), str(python_file))

        code = python_file.read_text()

        # Execute twice
        exec_globals_1 = {}
        exec(compile(code, str(python_file), "exec"), exec_globals_1)

        exec_globals_2 = {}
        exec(compile(code, str(python_file), "exec"), exec_globals_2)

        # Get create functions
        create_func_1 = next(
            (
                obj
                for name, obj in exec_globals_1.items()
                if callable(obj) and name.startswith("create_")
            ),
            None,
        )

        create_func_2 = next(
            (
                obj
                for name, obj in exec_globals_2.items()
                if callable(obj) and name.startswith("create_")
            ),
            None,
        )

        # Create schematics
        sch1 = create_func_1()
        sch2 = create_func_2()

        # Compare
        assert len(list(sch1.components)) == len(list(sch2.components))
        assert len(list(sch1.wires)) == len(list(sch2.wires))
        assert len(list(sch1.labels)) == len(list(sch2.labels))
