#!/usr/bin/env python3
"""
Test that property rotations are preserved through load/save cycles.

This tests Issue #74 - property rotations should not be reset to 0°.
"""

import re
import tempfile
from pathlib import Path

import kicad_sch_api as ksa


def test_property_rotation_preservation():
    """Test that property rotations are preserved through load/save."""

    # Create a test schematic with rotated properties
    test_schematic = """(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "12345678-1234-1234-1234-123456789abc")
	(paper "A4")
	(title_block
		(title "Property Rotation Test")
	)
	(lib_symbols
		(symbol "Device:R"
			(pin_numbers
				(hide yes)
			)
			(pin_names
				(offset 0)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "R"
				(at 2.032 0 90)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "R"
				(at 0 0 90)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at -1.778 0 90)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Datasheet" "~"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(property "Description" "Resistor"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "R_0_1"
				(rectangle
					(start -1.016 -2.54)
					(end 1.016 2.54)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
			(symbol "R_1_1"
				(pin passive line
					(at 0 3.81 270)
					(length 1.27)
					(name "~"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin passive line
					(at 0 -3.81 90)
					(length 1.27)
					(name "~"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
		)
	)
	(symbol
		(lib_id "Device:R")
		(at 100 100 90)
		(unit 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(fields_autoplaced yes)
		(uuid "aaaaaaaa-1111-2222-3333-444444444444")
		(property "Reference" "R1"
			(at 102 98 45)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Value" "10k"
			(at 102 102 135)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left)
			)
		)
		(property "Footprint" "Resistor_SMD:R_0603_1608Metric"
			(at 98 100 90)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(pin "1"
			(uuid "11111111-1111-1111-1111-111111111111")
		)
		(pin "2"
			(uuid "22222222-2222-2222-2222-222222222222")
		)
		(instances
			(project "Property Rotation Test"
				(path "/12345678-1234-1234-1234-123456789abc"
					(reference "R1")
					(unit 1)
				)
			)
		)
	)
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
)
"""

    # Create temp file with the test schematic
    with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
        f.write(test_schematic)
        temp_path = f.name

    try:
        # Extract original rotations
        ref_rot_before = extract_property_rotation(test_schematic, "Reference")
        val_rot_before = extract_property_rotation(test_schematic, "Value")

        # Load and save
        sch = ksa.Schematic.load(temp_path)
        sch.save(temp_path)

        # Read saved content
        with open(temp_path) as f:
            saved_content = f.read()

        # Extract rotations after save
        ref_rot_after = extract_property_rotation(saved_content, "Reference")
        val_rot_after = extract_property_rotation(saved_content, "Value")

        # Check if rotations were preserved
        assert (
            ref_rot_before == ref_rot_after
        ), f"Reference rotation changed from {ref_rot_before}° to {ref_rot_after}°"
        assert (
            val_rot_before == val_rot_after
        ), f"Value rotation changed from {val_rot_before}° to {val_rot_after}°"

    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


def extract_property_rotation(content: str, prop_name: str) -> int:
    """Extract rotation angle from a property in S-expression format."""
    # First, find the symbol instance (not lib_symbols)
    # Look for the section after lib_symbols
    parts = content.split("(lib_symbols")
    if len(parts) < 2:
        return 0

    # Get the part after lib_symbols section ends
    after_lib_symbols = parts[1].split("\n\t(symbol")[1] if "\n\t(symbol" in parts[1] else ""

    # Now search for the property in the component instance
    pattern = rf'\(property "{prop_name}"[^)]*?"([^"]*)"[^)]*?\(at\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
    match = re.search(pattern, after_lib_symbols, re.DOTALL)
    if match:
        return int(float(match.group(4)))
    return 0  # Default if not found


if __name__ == "__main__":
    test_property_rotation_preservation()
