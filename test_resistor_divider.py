#!/usr/bin/env python3
"""Test: Resistor divider with wire connections matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Resistor Divider")
    
    # Add resistors
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1", 
        value="10k",
        position=(100, 80),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2", 
        value="10k",
        position=(100, 120),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    # TODO: Add wire connections when wire API is implemented
    
    sch.save("test_resistor_divider.kicad_sch")
    print("✅ Created resistor divider")
    
    import subprocess
    subprocess.run(["open", "test_resistor_divider.kicad_sch"])

if __name__ == "__main__":
    main()