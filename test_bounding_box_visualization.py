#!/usr/bin/env python3
"""
Test script to visualize component bounding boxes in KiCAD schematics.

This demonstrates the new bounding box drawing functionality that shows
accurate component boundaries for Manhattan routing obstacle avoidance.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    print("🎯 Bounding Box Visualization Test")
    print("=" * 50)
    
    # Create test schematic
    sch = ksa.create_schematic("Bounding Box Visualization")
    
    # Add various components to test different bounding box sizes
    print("📍 Adding components...")
    
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(50.8, 50.8))
    r3 = sch.components.add("Device:R", "R3", "3k", Point(76.2, 50.8))
    
    # Add components at different positions for variety
    r4 = sch.components.add("Device:R", "R4", "4k", Point(25.4, 25.4))
    r5 = sch.components.add("Device:R", "R5", "5k", Point(76.2, 76.2))
    
    components = [r1, r2, r3, r4, r5]
    for comp in components:
        print(f"   {comp.reference} ({comp.value}) at {comp.position}")
    
    # Test 1: Draw bounding boxes without properties
    print(f"\n📦 Drawing component-only bounding boxes...")
    bbox_uuids_1 = sch.draw_component_bounding_boxes(
        include_properties=False,
        stroke_width=0.254,
        stroke_color="red"
    )
    print(f"   Drew {len(bbox_uuids_1)} red rectangles (component bodies only)")
    
    # Test 2: Draw bounding boxes with properties (labels) 
    print(f"\n📋 Drawing bounding boxes with properties...")
    bbox_uuids_2 = sch.draw_component_bounding_boxes(
        include_properties=True,
        stroke_width=0.1524,
        stroke_color="blue"
    )
    print(f"   Drew {len(bbox_uuids_2)} blue rectangles (including labels)")
    
    # Test 3: Individual bounding box drawing
    print(f"\n🎨 Drawing individual custom bounding box...")
    from kicad_sch_api.core.component_bounds import get_component_bounding_box
    
    # Get R3's bounding box and draw it with expanded boundary  
    r3_bbox = get_component_bounding_box(r3, include_properties=False)
    custom_uuid = sch.draw_bounding_box(
        r3_bbox.expand(2.54),  # Expand by 2 grid units for visibility
        stroke_width=0.508,    # Thick line
        stroke_color="green"   # Green color
    )
    print(f"   Drew custom expanded bounding box around R3: {custom_uuid}")
    
    # Add some connecting wires for context
    print(f"\n🔗 Adding context wires...")
    wire1 = sch.auto_route_pins("R1", "2", "R2", "1", routing_mode="manhattan")
    wire2 = sch.auto_route_pins("R2", "2", "R3", "1", routing_mode="manhattan")
    wire3 = sch.auto_route_pins("R4", "1", "R5", "2", routing_mode="manhattan")
    
    if wire1 and wire2 and wire3:
        print(f"   Added Manhattan routed wires for comparison")
    
    # Add legend text
    print(f"\n📝 Adding legend...")
    sch.add_text("LEGEND:", Point(15, 90), size=1.5)
    sch.add_text("Red = Component bounds", Point(15, 87), size=1.0)
    sch.add_text("Blue = With properties", Point(15, 84), size=1.0)  
    sch.add_text("Green = Custom expanded", Point(15, 81), size=1.0)
    sch.add_text("Wires = Manhattan routing", Point(15, 78), size=1.0)
    
    # Print bounding box details
    print(f"\n📏 Bounding Box Details:")
    from kicad_sch_api.core.component_bounds import get_component_bounding_box
    
    for comp in components:
        bbox = get_component_bounding_box(comp, include_properties=False)
        bbox_with_props = get_component_bounding_box(comp, include_properties=True)
        
        print(f"   {comp.reference}:")
        print(f"     Body: {bbox.width:.2f}×{bbox.height:.2f}mm")
        print(f"     +Props: {bbox_with_props.width:.2f}×{bbox_with_props.height:.2f}mm")
        print(f"     Center: ({bbox.center.x:.1f}, {bbox.center.y:.1f})")
    
    # Save and open
    filename = "bounding_box_visualization.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("🔍 You should see:")
        print("   • Red rectangles around component bodies")
        print("   • Blue rectangles including label space")
        print("   • Green expanded rectangle around R3")
        print("   • Manhattan routed wires avoiding obstacles")
        print("   • All visualizations overlaid for comparison")
    except Exception as e:
        print(f"⚠️  Could not auto-open KiCAD: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()