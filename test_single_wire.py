#!/usr/bin/env python3
"""Test: Single wire matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Wire")
    
    # TODO: Add wire when wire API is implemented
    # sch.wires.add(start=(100, 100), end=(150, 100))
    
    sch.save("test_single_wire.kicad_sch")
    print("✅ Created single wire (no wire implementation yet)")
    
    import subprocess
    subprocess.run(["open", "test_single_wire.kicad_sch"])

if __name__ == "__main__":
    main()