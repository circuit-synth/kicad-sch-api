#!/usr/bin/env python3
"""
Test colored and styled bounding box rectangles.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.core.component_bounds import get_component_bounding_box

def main():
    print("🎨 Colored Rectangle Test")
    print("=" * 30)
    
    # Create schematic
    sch = ksa.create_schematic("Colored Rectangle Test")
    
    # Add some components
    print("📍 Adding components...")
    r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(100, 50))
    r3 = sch.components.add("Device:R", "R3", "3k", Point(150, 50))
    
    print(f"   Added {r1.reference}, {r2.reference}, {r3.reference}")
    
    # Test 1: Red dashed rectangle (1mm width)
    print("\n🔴 Drawing red dashed bounding box...")
    bbox1 = get_component_bounding_box(r1, include_properties=False)
    rect1_uuid = sch.draw_bounding_box(
        bbox1,
        stroke_width=1,        # 1mm width like your manual example
        stroke_color="red",    # Red color
        stroke_type="dash"     # Dashed lines
    )
    print(f"   Drew red dashed rectangle: {rect1_uuid}")
    
    # Test 2: Blue dotted rectangle (0.5mm width)
    print("\n🔵 Drawing blue dotted bounding box...")
    bbox2 = get_component_bounding_box(r2, include_properties=False)
    rect2_uuid = sch.draw_bounding_box(
        bbox2,
        stroke_width=0.5,      # 0.5mm width
        stroke_color="blue",   # Blue color
        stroke_type="dot"      # Dotted lines
    )
    print(f"   Drew blue dotted rectangle: {rect2_uuid}")
    
    # Test 3: Green solid rectangle (2mm width)
    print("\n🟢 Drawing green solid bounding box...")
    bbox3 = get_component_bounding_box(r3, include_properties=False)
    rect3_uuid = sch.draw_bounding_box(
        bbox3,
        stroke_width=2,        # 2mm width (thick)
        stroke_color="green",  # Green color
        stroke_type="default"  # Solid lines
    )
    print(f"   Drew green solid rectangle: {rect3_uuid}")
    
    # Test 4: Multiple colors for all components at once
    print("\n🌈 Drawing all component bounding boxes with mixed styles...")
    bbox_uuids = sch.draw_component_bounding_boxes(
        include_properties=True,  # Include property labels
        stroke_width=0.75,        # 0.75mm width
        stroke_color="magenta",   # Magenta color
        stroke_type="dash_dot"    # Dash-dot pattern (KiCAD format)
    )
    print(f"   Drew {len(bbox_uuids)} magenta dash-dot rectangles including properties")
    
    # Add descriptive text
    print("\n📝 Adding legend...")
    sch.add_text("Color & Stroke Style Test", Point(30, 80), size=2.0)
    sch.add_text("Red Dash (1mm) - Component body", Point(30, 75), size=1.0)
    sch.add_text("Blue Dot (0.5mm) - Component body", Point(30, 72), size=1.0)
    sch.add_text("Green Solid (2mm) - Component body", Point(30, 69), size=1.0)
    sch.add_text("Magenta DashDot (0.75mm) - With properties", Point(30, 66), size=1.0)
    
    # Save
    filename = "colored_rectangles_test.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("🔍 You should see:")
        print("   • Red dashed rectangles (1mm width)")
        print("   • Blue dotted rectangles (0.5mm width)")  
        print("   • Green solid rectangles (2mm width)")
        print("   • Magenta dash-dot rectangles (0.75mm width)")
        print("   • Different sized boxes (body vs. with properties)")
    except Exception as e:
        print(f"⚠️  Could not auto-open: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()