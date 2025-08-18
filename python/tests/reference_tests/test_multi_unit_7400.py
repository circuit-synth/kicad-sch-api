#!/usr/bin/env python3
"""Test: 74xx:7400 extends 74xx:74LS00 - Multi-unit NAND gate (for future multi-unit work)."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Multi-Unit 7400 NAND Gates")
    
    # Place individual units of the 74xx:7400 quad NAND gate
    # Each unit should display as a separate NAND gate (U1A, U1B, U1C, U1D)
    
    # Unit 1 - Gate A
    sch.components.add(
        lib_id="74xx:7400",
        reference="U1A", 
        value="7400",
        unit=1,
        position=(100, 80),
        footprint="Package_DIP:DIP-14_W7.62mm",
        datasheet="https://www.ti.com/lit/ds/symlink/sn74ls00.pdf",
        description="Quad 2-input NAND gate"
    )
    
    # Unit 2 - Gate B  
    sch.components.add(
        lib_id="74xx:7400",
        reference="U1B",
        value="7400", 
        unit=2,
        position=(100, 120),
        footprint="Package_DIP:DIP-14_W7.62mm",
        datasheet="https://www.ti.com/lit/ds/symlink/sn74ls00.pdf",
        description="Quad 2-input NAND gate"
    )
    
    # Unit 3 - Gate C
    sch.components.add(
        lib_id="74xx:7400",
        reference="U1C",
        value="7400",
        unit=3, 
        position=(100, 160),
        footprint="Package_DIP:DIP-14_W7.62mm",
        datasheet="https://www.ti.com/lit/ds/symlink/sn74ls00.pdf",
        description="Quad 2-input NAND gate"
    )
    
    # Unit 4 - Gate D
    sch.components.add(
        lib_id="74xx:7400",
        reference="U1D",
        value="7400",
        unit=4,
        position=(100, 200),
        footprint="Package_DIP:DIP-14_W7.62mm", 
        datasheet="https://www.ti.com/lit/ds/symlink/sn74ls00.pdf",
        description="Quad 2-input NAND gate"
    )
    
    # Unit 5 - Power unit (VCC/GND)
    sch.components.add(
        lib_id="74xx:7400",
        reference="U1E",
        value="7400",
        unit=5,
        position=(60, 240),
        footprint="Package_DIP:DIP-14_W7.62mm",
        datasheet="https://www.ti.com/lit/ds/symlink/sn74ls00.pdf", 
        description="Quad 2-input NAND gate"
    )
    
    sch.save("test_multi_unit_7400.kicad_sch")
    print("✅ Created multi-unit 7400 NAND gates (all 5 units)")
    
    import subprocess
    subprocess.run(["open", "test_multi_unit_7400.kicad_sch"])

if __name__ == "__main__":
    main()