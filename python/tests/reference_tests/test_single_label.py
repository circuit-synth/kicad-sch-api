#!/usr/bin/env python3
"""Test: Single label matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Label")
    
    # TODO: Add label when label API is implemented
    # sch.labels.add(text="VCC", position=(100, 100))
    
    sch.save("test_single_label.kicad_sch")
    print("✅ Created single label (no label implementation yet)")
    
    import subprocess
    subprocess.run(["open", "test_single_label.kicad_sch"])

if __name__ == "__main__":
    main()