#!/usr/bin/env python3
"""
Demo: KiCad Schematic to Python Export

This example demonstrates the new kicad-to-python export functionality
introduced in Issue #129.

The feature allows you to convert existing KiCad schematic files (.kicad_sch)
into executable Python code that uses the kicad-sch-api to recreate the schematic.
"""

from pathlib import Path
import kicad_sch_api as ksa


def demo_export_api_method():
    """Demonstrate using the Schematic.export_to_python() method."""
    print("=" * 70)
    print("Demo 1: Using Schematic.export_to_python() API Method")
    print("=" * 70)
    print()

    # Load an existing schematic
    input_path = Path("tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch")

    if not input_path.exists():
        print(f"⚠️  Skipping - reference schematic not found: {input_path}")
        return

    print(f"📖 Loading schematic: {input_path}")
    sch = ksa.Schematic.load(input_path)
    print(f"   Components: {len(list(sch.components))}")
    print(f"   Wires: {len(list(sch.wires))}")
    print()

    # Export to Python using API method
    output_path = Path("/tmp/exported_via_api.py")
    print(f"🔨 Exporting to Python: {output_path}")
    result = sch.export_to_python(
        output_path,
        template='default',
        format_code=True,
        add_comments=True
    )
    print(f"✅ Generated: {result}")
    print(f"   Lines: {len(result.read_text().split(chr(10)))}")
    print()


def demo_utility_function():
    """Demonstrate using the schematic_to_python() utility function."""
    print("=" * 70)
    print("Demo 2: Using ksa.schematic_to_python() Utility Function")
    print("=" * 70)
    print()

    input_path = Path("tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch")

    if not input_path.exists():
        print(f"⚠️  Skipping - reference schematic not found: {input_path}")
        return

    output_path = Path("/tmp/exported_via_utility.py")

    print(f"🔨 Converting: {input_path} → {output_path}")

    # One-line conversion
    result = ksa.schematic_to_python(
        str(input_path),
        str(output_path),
        template='minimal'
    )

    print(f"✅ Generated: {result}")
    print()


def demo_execute_generated_code():
    """Demonstrate executing the generated Python code."""
    print("=" * 70)
    print("Demo 3: Executing Generated Python Code")
    print("=" * 70)
    print()

    # Generate code
    input_path = Path("tests/reference_kicad_projects/rotated_resistor_0deg/rotated_resistor_0deg.kicad_sch")

    if not input_path.exists():
        print(f"⚠️  Skipping - reference schematic not found: {input_path}")
        return

    output_path = Path("/tmp/executable_demo.py")

    print(f"📖 Generating Python code from: {input_path}")
    ksa.schematic_to_python(str(input_path), str(output_path))

    # Execute the generated code
    print(f"🔨 Executing generated code...")
    code = output_path.read_text()
    exec_globals = {}
    exec(compile(code, str(output_path), 'exec'), exec_globals)

    # Call the generated function
    if 'create_simple_circuit' in exec_globals:
        print(f"✅ Calling create_simple_circuit()...")
        regenerated_sch = exec_globals['create_simple_circuit']()
        print(f"   Created schematic with {len(list(regenerated_sch.components))} components")
        print(f"   Wires: {len(list(regenerated_sch.wires))}")
    print()


def demo_cli_usage():
    """Demonstrate CLI command usage."""
    print("=" * 70)
    print("Demo 4: CLI Command Usage")
    print("=" * 70)
    print()

    print("The kicad-to-python CLI command provides a simple interface:")
    print()
    print("Basic usage:")
    print("  $ kicad-to-python input.kicad_sch output.py")
    print()
    print("With options:")
    print("  $ kicad-to-python input.kicad_sch output.py --template minimal")
    print("  $ kicad-to-python input.kicad_sch output.py --verbose")
    print("  $ kicad-to-python input.kicad_sch output.py --no-format")
    print()
    print("Available templates:")
    print("  - minimal:    Compact code without comments")
    print("  - default:    Balanced verbosity (recommended)")
    print("  - verbose:    Detailed with extra information")
    print("  - documented: Full docstrings and comments")
    print()


def main():
    """Run all demos."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          KiCad-to-Python Export Feature Demo                      ║")
    print("║                    Issue #129                                      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    demo_export_api_method()
    demo_utility_function()
    demo_execute_generated_code()
    demo_cli_usage()

    print("=" * 70)
    print("✅ All demos complete!")
    print("=" * 70)
    print()
    print("Use Cases:")
    print("  • Learning: See how to recreate schematics programmatically")
    print("  • Migration: Convert existing designs to code")
    print("  • Templates: Extract reusable patterns")
    print("  • Documentation: Generate working code examples")
    print()


if __name__ == '__main__':
    main()
