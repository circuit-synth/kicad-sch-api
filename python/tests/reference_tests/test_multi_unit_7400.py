#!/usr/bin/env python3
"""Test: 74xx:7400 extends 74xx:74LS00 - Multi-unit NAND gate (for future multi-unit work)."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Extends 7400 NAND Gate")
    
    # Add 74xx:7400 which extends 74xx:74LS00
    # This should automatically inherit the parent symbol graphics
    sch.components.add(
        lib_id="74xx:7400",
        reference="U1", 
        value="7400",
        position=(100, 100),
        footprint="Package_DIP:DIP-14_W7.62mm",
        datasheet="https://www.ti.com/lit/ds/symlink/sn74ls00.pdf",
        description="Quad 2-input NAND gate"
    )
    
    sch.save("test_extends_7400.kicad_sch")
    print("✅ Created 7400 NAND gate with extends logic")
    
    import subprocess
    subprocess.run(["open", "test_extends_7400.kicad_sch"])

if __name__ == "__main__":
    main()