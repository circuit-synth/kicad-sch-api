#!/usr/bin/env python3
"""Test: Single extended component (Device:Filter_EMI_CommonMode extends Filter_EMI_LL)."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Extended Component")
    
    # Add Device:Filter_EMI_CommonMode which extends Device:Filter_EMI_LL
    # The extends logic should automatically include parent symbol graphics
    sch.components.add(
        lib_id="Device:Filter_EMI_CommonMode",
        reference="FL1", 
        value="Filter_EMI_CommonMode",
        position=(124.46, 88.9),
        footprint="Inductor_SMD:L_CommonMode_Wurth_WE-CNSW-1206",
        datasheet="~",
        description="EMI 2-inductor common mode filter"
    )
    
    sch.save("test_extends_component.kicad_sch")
    print("✅ Created extends component test")
    
    import subprocess
    subprocess.run(["open", "test_extends_component.kicad_sch"])

if __name__ == "__main__":
    main()