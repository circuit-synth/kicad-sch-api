#!/usr/bin/env python3
"""
Test simple rectangle creation matching KiCAD format exactly.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.core.component_bounds import BoundingBox

def main():
    print("🎯 Simple Rectangle Test")
    print("=" * 30)
    
    # Create test schematic
    sch = ksa.create_schematic("Simple Rectangle Test")
    
    # Create a simple bounding box
    bbox = BoundingBox(
        min_x=100.0, 
        min_y=50.0,
        max_x=130.0, 
        max_y=80.0
    )
    
    # Draw rectangle with KiCAD default parameters
    print("📦 Drawing simple rectangle...")
    rect_uuid = sch.draw_bounding_box(bbox)
    print(f"   Created rectangle: {rect_uuid}")
    
    # Save
    filename = "simple_rectangle.kicad_sch"
    sch.save(filename)
    print(f"💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("🔍 Check if rectangle appears without parse errors")
    except Exception as e:
        print(f"⚠️  Could not auto-open: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()