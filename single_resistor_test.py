#!/usr/bin/env python3
"""Simple test: Create a new schematic and add a resistor."""

import kicad_sch_api as ksa

def main():
    """Create a new schematic and add a resistor."""
    # Create a new schematic
    sch = ksa.create_schematic("Simple Circuit")
    
    # Add a resistor  
    resistor = sch.components.add(
        lib_id="Device:R",
        reference="R1", 
        value="10k",
        position=(100, 100),
        footprint="Resistor_SMD:R_0603_1608Metric",
        datasheet="~",
        description="Resistor"
    )
    
    print(f"✅ Added {resistor.reference}: {resistor.value}")
    
    # Save the schematic
    sch.save("simple_circuit.kicad_sch")
    print(f"✅ Saved schematic")

if __name__ == "__main__":
    main()