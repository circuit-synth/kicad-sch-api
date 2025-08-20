#!/usr/bin/env python3
"""
Create a blank schematic for testing colored rectangle functionality.
"""

import kicad_sch_api as ksa

def main():
    print("🎨 Creating blank schematic for colored rectangle testing...")
    
    # Create minimal schematic
    sch = ksa.create_schematic("Colored Rectangle Test")
    
    # Save without any graphics elements
    filename = "blank_colored_rectangle_test.kicad_sch"
    sch.save(filename)
    print(f"💾 Saved blank schematic: {filename}")
    
    # Try to open it
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print(f"📖 Opening {filename} in KiCAD...")
        print("✅ You can now manually add a colored rectangle using KiCAD's drawing tools")
        print("🎨 Please add a rectangle with a non-default color (e.g., red, blue, green)")
        print("💾 Save the file after adding the rectangle so we can examine the format")
    except Exception as e:
        print(f"⚠️  Could not auto-open: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()