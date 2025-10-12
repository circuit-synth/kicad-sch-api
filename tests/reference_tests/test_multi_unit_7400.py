#!/usr/bin/env python3
"""Test: 74xx:7400 extends 74xx:74LS00 - Multi-unit NAND gate (for future multi-unit work)."""

import kicad_sch_api as ksa


def main():
    sch = ksa.create_schematic("Multi-Unit 7400 NAND Gates")

    # Simple approach: Auto-place all units with one call
    ic = sch.components.add_ic(
        lib_id="74xx:7400",
        reference_prefix="U1",
        position=(100, 100),
        value="7400",
        footprint="Package_DIP:DIP-14_W7.62mm",
        datasheet="https://www.ti.com/lit/ds/symlink/sn74ls00.pdf",
        description="Quad 2-input NAND gate",
    )

    # Optional: Override specific unit positions
    ic.place_unit(1, position=(150, 80))  # Move Gate A
    ic.place_unit(2, position=(150, 120))  # Move Gate B
    # Units 3, 4, 5 keep auto-layout positions

    sch.save("test_multi_unit_7400.kicad_sch")
    print("✅ Created multi-unit 7400 NAND gates (all 5 units)")

    import subprocess

    subprocess.run(["open", "test_multi_unit_7400.kicad_sch"])


if __name__ == "__main__":
    main()
