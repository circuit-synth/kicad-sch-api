#!/usr/bin/env python3
"""
Generate a schematic with a resistor and its bounding box visualization.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    print("🎯 Resistor with Bounding Box")
    print("=" * 35)
    
    # Create schematic
    sch = ksa.create_schematic("Resistor with Bounding Box")
    
    # Add a resistor
    print("📍 Adding resistor...")
    resistor = sch.components.add("Device:R", "R1", "10k", Point(100, 100))
    print(f"   Added {resistor.reference} ({resistor.value}) at {resistor.position}")
    
    # Draw bounding box around the resistor
    print("📦 Drawing bounding box...")
    from kicad_sch_api.core.component_bounds import get_component_bounding_box
    
    # Get component bounding box (body only)
    bbox = get_component_bounding_box(resistor, include_properties=False)
    rect_uuid = sch.draw_bounding_box(bbox)
    print(f"   Drew bounding box: {rect_uuid}")
    print(f"   Bounding box size: {bbox.width:.2f}×{bbox.height:.2f}mm")
    print(f"   Bounding box center: ({bbox.center.x:.1f}, {bbox.center.y:.1f})")
    
    # Add some descriptive text
    print("📝 Adding description...")
    sch.add_text("10kΩ Resistor", Point(80, 80), size=1.5)
    sch.add_text("Bounding box shows component outline", Point(80, 120), size=1.0)
    
    # Save
    filename = "resistor_with_bounding_box.kicad_sch"
    sch.save(filename)
    print(f"💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("🔍 You should see:")
        print("   • R1 resistor component") 
        print("   • Rectangle outline around the resistor body")
        print("   • Descriptive text labels")
    except Exception as e:
        print(f"⚠️  Could not auto-open: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()