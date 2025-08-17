#!/usr/bin/env python3
"""Test: Single resistor matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Resistor")
    
    sch.components.add(
        lib_id="Device:R",
        reference="R1", 
        value="10k",
        position=(93.98, 81.28),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    sch.save("test_single_resistor.kicad_sch")
    print("✅ Created single resistor")
    
    import subprocess
    subprocess.run(["open", "test_single_resistor.kicad_sch"])

if __name__ == "__main__":
    main()