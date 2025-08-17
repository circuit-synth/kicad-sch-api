#!/usr/bin/env python3
"""Test: Single text matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Text")
    
    # TODO: Add text when text API is implemented
    
    sch.save("test_single_text.kicad_sch")
    print("✅ Created single text (no text implementation yet)")
    
    import subprocess
    subprocess.run(["open", "test_single_text.kicad_sch"])

if __name__ == "__main__":
    main()