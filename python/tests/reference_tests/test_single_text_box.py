#!/usr/bin/env python3
"""Test: Single text box matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Text Box")
    
    # TODO: Add text box when text box API is implemented
    
    sch.save("test_single_text_box.kicad_sch")
    print("✅ Created single text box (no text box implementation yet)")
    
    import subprocess
    subprocess.run(["open", "test_single_text_box.kicad_sch"])

if __name__ == "__main__":
    main()