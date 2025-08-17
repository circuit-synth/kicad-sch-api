#!/usr/bin/env python3
"""Test: Two resistors matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Two Resistors")
    
    sch.components.add(
        lib_id="Device:R",
        reference="R1", 
        value="10k",
        position=(100, 100),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    sch.components.add(
        lib_id="Device:R",
        reference="R2", 
        value="1k",
        position=(150, 100),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    sch.save("test_two_resistors.kicad_sch")
    print("✅ Created two resistors")
    
    import subprocess
    subprocess.run(["open", "test_two_resistors.kicad_sch"])

if __name__ == "__main__":
    main()