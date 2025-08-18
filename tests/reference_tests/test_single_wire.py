#!/usr/bin/env python3
"""Test: Single wire matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Wire")
    
    # Add wire matching the reference schematic
    sch.wires.add(
        start=(114.3, 63.5),
        end=(135.89, 63.5)
    )
    
    sch.save("test_single_wire.kicad_sch")
    print("✅ Created single wire")
    
    import subprocess
    subprocess.run(["open", "test_single_wire.kicad_sch"])

if __name__ == "__main__":
    main()