#!/usr/bin/env python3
"""Test: Resistor divider with wire connections matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Resistor Divider")
    
    # Add power symbols (matching reference positions)
    pwr_3v3 = sch.components.add(
        lib_id="power:+3.3V",
        reference="#PWR02", 
        value="+3.3V",
        position=(91.44, 69.85),
        footprint="",
        datasheet="",
        description="Power symbol creates a global label with name \"+3.3V\""
    )
    
    gnd = sch.components.add(
        lib_id="power:GND",
        reference="#PWR01", 
        value="GND",
        position=(91.44, 95.25),
        footprint="",
        datasheet="",
        description="Power symbol creates a global label with name \"GND\" , ground"
    )
    
    # Add resistors (matching reference positions)
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1", 
        value="10k",
        position=(91.44, 73.66),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2", 
        value="10k",
        position=(91.44, 91.44),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    # Add wire connections (matching reference)
    # Wire 1: Output wire to VOUT label point
    sch.wires.add(
        start=(100.33, 81.28),
        end=(91.44, 81.28)
    )
    
    # Wire 2: Junction to R1 bottom pin
    sch.wires.add(
        start=(91.44, 81.28),
        end=(91.44, 77.47)
    )
    
    # Wire 3: R2 top pin to junction
    sch.wires.add(
        start=(91.44, 87.63),
        end=(91.44, 81.28)
    )
    
    # TODO: Add junction at (91.44, 81.28) when junction API is implemented
    # TODO: Add VOUT label at (100.33, 81.28) when local label API is implemented
    
    sch.save("test_resistor_divider.kicad_sch")
    print("✅ Created resistor divider with wires")
    
    import subprocess
    subprocess.run(["open", "test_resistor_divider.kicad_sch"])

if __name__ == "__main__":
    main()