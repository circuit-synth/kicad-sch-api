#!/usr/bin/env python3
"""Test: Single resistor matching reference."""

import kicad_sch_api as ksa


def main():
    # Create schematic and set exact UUID from reference
    sch = ksa.create_schematic("single_resistor")  # Use exact project name
    sch._data["uuid"] = "d80ef055-e33f-44b7-9702-8ce9cf922ab9"

    # Add component with exact UUID and position from reference
    component = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(93.98, 81.28),
        footprint="Resistor_SMD:R_0603_1608Metric",
        component_uuid="a9fd95f7-6e8c-4e46-ba2c-21946a035fdb",
    )

    # Set exact property positions to match reference
    component.set_property("Datasheet", "~")
    component.set_property("Description", "Resistor")

    sch.save("test_single_resistor.kicad_sch")
    print("✅ Created single resistor")

    import subprocess

    subprocess.run(["open", "test_single_resistor.kicad_sch"])


if __name__ == "__main__":
    main()
