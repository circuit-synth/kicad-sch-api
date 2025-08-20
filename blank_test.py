#!/usr/bin/env python3
"""
Create a blank schematic for testing basic functionality.
"""

import kicad_sch_api as ksa

def main():
    print("🔧 Creating blank schematic...")
    
    # Create minimal schematic
    sch = ksa.create_schematic("Blank Test")
    
    # Save without any graphics elements
    filename = "blank_test.kicad_sch"
    sch.save(filename)
    print(f"💾 Saved blank schematic: {filename}")
    
    # Try to open it
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print(f"📖 Opening {filename} in KiCAD...")
        print("✅ If this opens without errors, the basic schematic format is working")
    except Exception as e:
        print(f"⚠️  Could not auto-open: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()