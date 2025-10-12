#!/usr/bin/env python3
"""Test: Power symbols matching reference."""

import kicad_sch_api as ksa


def main():
    sch = ksa.create_schematic("Power Symbols")

    # Add power symbols matching the reference positions
    # +3.3V power symbol
    sch.components.add(
        lib_id="power:+3.3V",
        reference="#PWR01",
        value="+3.3V",
        position=(78.74, 64.77),
        footprint="",
        datasheet="",
        description="Power symbol creates a global label with name +3.3V",
    )

    # GND power symbol
    sch.components.add(
        lib_id="power:GND",
        reference="#PWR02",
        value="GND",
        position=(154.94, 69.85),
        footprint="",
        datasheet="",
        description="Power symbol creates a global label with name GND, ground",
    )

    # VDD power symbol
    sch.components.add(
        lib_id="power:VDD",
        reference="#PWR03",
        value="VDD",
        position=(113.03, 115.57),
        footprint="",
        datasheet="",
        description="Power symbol creates a global label with name VDD",
    )

    sch.save("test_power_symbols.kicad_sch")
    print("✅ Created power symbols")

    import subprocess

    subprocess.run(["open", "test_power_symbols.kicad_sch"])


if __name__ == "__main__":
    main()
