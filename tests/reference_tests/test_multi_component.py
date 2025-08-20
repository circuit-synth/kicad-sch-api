#!/usr/bin/env python3
"""Test: Multiple components with different types."""

import kicad_sch_api as ksa


def main():
    sch = ksa.create_schematic("Multi Component Test")

    # Multiple resistors (test lib_symbols reuse)
    sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100, 100),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor",
    )

    sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="1k",
        position=(150, 100),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor",
    )

    # Add capacitor (test different component type)
    sch.components.add(
        lib_id="Device:C",
        reference="C1",
        value="100nF",
        position=(100, 150),
        footprint="Capacitor_SMD:C_0603_1608Metric",
        datasheet="~",
        description="Unpolarized capacitor",
    )

    print(f"✅ Created {len(sch.components)} components")

    sch.save("test_multi_component.kicad_sch")
    print("✅ Saved multi component test")

    import subprocess

    subprocess.run(["open", "test_multi_component.kicad_sch"])


if __name__ == "__main__":
    main()
