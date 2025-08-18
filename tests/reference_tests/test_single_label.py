#!/usr/bin/env python3
"""Test: Single label matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Label")
    
    # Add local label matching the reference
    sch.add_label(
        text="LABEL_1",
        position=(130.81, 73.66),
        rotation=0,
        size=1.27
    )
    
    sch.save("test_single_label.kicad_sch")
    print("✅ Created single label")
    
    import subprocess
    subprocess.run(["open", "test_single_label.kicad_sch"])

if __name__ == "__main__":
    main()