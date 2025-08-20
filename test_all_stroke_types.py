#!/usr/bin/env python3
"""
Test all valid KiCAD stroke types for colored rectangles.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.core.component_bounds import get_component_bounding_box

def main():
    print("🎨 All KiCAD Stroke Types Test")
    print("=" * 35)
    
    # Create schematic
    sch = ksa.create_schematic("All Stroke Types Test")
    
    # Add components for each stroke type
    print("📍 Adding components...")
    components = []
    for i in range(6):
        comp = sch.components.add("Device:R", f"R{i+1}", f"{(i+1)}k", Point(50 + i*30, 50))
        components.append(comp)
    
    print(f"   Added {len(components)} components")
    
    # All valid KiCAD stroke types
    stroke_types = ["default", "solid", "dash", "dot", "dash_dot", "dash_dot_dot"]
    colors = ["black", "red", "blue", "green", "magenta", "cyan"]
    
    # Test each stroke type
    print("\n🎨 Drawing rectangles with all stroke types...")
    for i, (comp, stroke_type, color) in enumerate(zip(components, stroke_types, colors)):
        bbox = get_component_bounding_box(comp, include_properties=False)
        rect_uuid = sch.draw_bounding_box(
            bbox,
            stroke_width=0.8,         # 0.8mm width for visibility
            stroke_color=color,       # Different color for each
            stroke_type=stroke_type   # Test each stroke type
        )
        print(f"   {stroke_type:<12} ({color:<7}): {rect_uuid}")
    
    # Add legend
    print("\n📝 Adding legend...")
    sch.add_text("KiCAD Stroke Types", Point(20, 90), size=2.0)
    
    y_pos = 85
    for stroke_type, color in zip(stroke_types, colors):
        sch.add_text(f"{stroke_type:<12} - {color}", Point(20, y_pos), size=1.2)
        y_pos -= 3
    
    # Add note about usage
    sch.add_text("All rectangles are 0.8mm width", Point(20, 25), size=1.0)
    sch.add_text("These are the only valid KiCAD stroke types", Point(20, 22), size=1.0)
    
    # Save
    filename = "all_stroke_types_test.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("🔍 You should see all 6 stroke types:")
        for stroke_type, color in zip(stroke_types, colors):
            print(f"   • {stroke_type} ({color})")
    except Exception as e:
        print(f"⚠️  Could not auto-open: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()