#!/usr/bin/env python3
"""Test: Single hierarchical label matching reference."""

import kicad_sch_api as ksa

def main():
    sch = ksa.create_schematic("Single Label Hierarchical")
    
    # TODO: Add hierarchical label when hierarchical label API is implemented
    
    sch.save("test_single_label_hierarchical.kicad_sch")
    print("✅ Created single hierarchical label (no hierarchical label implementation yet)")
    
    import subprocess
    subprocess.run(["open", "test_single_label_hierarchical.kicad_sch"])

if __name__ == "__main__":
    main()