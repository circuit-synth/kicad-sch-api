#!/usr/bin/env python3
"""Test: Single hierarchical sheet matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Hierarchical Sheet")
    
    # TODO: Add hierarchical sheet when hierarchical sheet API is implemented
    
    sch.save("test_single_hierarchical_sheet.kicad_sch")
    print("✅ Created single hierarchical sheet (no hierarchical sheet implementation yet)")
    
    import subprocess
    subprocess.run(["open", "test_single_hierarchical_sheet.kicad_sch"])

if __name__ == "__main__":
    main()