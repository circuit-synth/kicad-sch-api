#!/usr/bin/env python3
"""Test: Two resistors matching reference."""

import kicad_sch_api as ksa


def main():
    # Create schematic and set exact UUID from reference
    sch = ksa.create_schematic("two_resistors")  # Use exact project name
    sch._data["uuid"] = "675cd405-6611-430b-b7ae-e05fb6c61af8"

    # Add R1 with coordinates that match grid snapping
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(102.87, 68.58),  # Grid-snapped coordinates
        footprint="Resistor_SMD:R_0603_1608Metric",
        component_uuid="093e2630-093e-44f6-acb1-51c617677d7c",
    )
    r1.set_property("Datasheet", "~")
    r1.set_property("Description", "Resistor")

    # Add R2 with exact coordinates and UUID from reference
    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="10k",  # Reference shows 10k, not 1k
        position=(118.11, 68.58),
        footprint="Resistor_SMD:R_0603_1608Metric",
        component_uuid="95d400df-5f8d-4212-bfa8-dec6b2c6cda6",
    )
    r2.set_property("Datasheet", "~")
    r2.set_property("Description", "Resistor")

    sch.save("test_two_resistors.kicad_sch")
    print("✅ Created two resistors")

    import subprocess

    subprocess.run(["open", "test_two_resistors.kicad_sch"])


if __name__ == "__main__":
    main()
