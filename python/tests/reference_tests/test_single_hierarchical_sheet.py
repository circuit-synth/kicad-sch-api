#!/usr/bin/env python3
"""Test: Single hierarchical sheet matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Hierarchical Sheet")
    
    # Add hierarchical sheet matching the reference
    sch.add_sheet(
        name="subcircuit1",
        filename="subcircuit1.kicad_sch",
        position=(137.16, 69.85),
        size=(26.67, 34.29),
        stroke_width=0.1524,
        stroke_type="solid",
        project_name="single_hierarchical_sheet",
        page_number="2"
    )
    
    sch.save("test_single_hierarchical_sheet.kicad_sch")
    
    # Create the referenced sub-schematic file so KiCAD can load it
    sub_sch = ksa.create_schematic("subcircuit1")
    sub_sch.save("subcircuit1.kicad_sch")
    
    print("✅ Created single hierarchical sheet with sub-schematic")
    
    import subprocess
    subprocess.run(["open", "test_single_hierarchical_sheet.kicad_sch"])

if __name__ == "__main__":
    main()