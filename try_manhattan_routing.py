#!/usr/bin/env python3
"""
Simple script to try Manhattan routing with obstacle avoidance.
Creates components that block direct paths to test Manhattan routing.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    print("🛣️  Creating Manhattan Routing Example...")
    
    # Create schematic
    sch = ksa.create_schematic("Manhattan Routing Demo")
    
    # Create obstacle configuration
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))    # Start (left)
    r_obs = sch.components.add("Device:R", "ROBS", "100", Point(50.8, 50.8)) # Obstacle (center)
    r2 = sch.components.add("Device:R", "R2", "2k", Point(76.2, 50.8))    # End (right)
    
    # Add components at different heights for more interesting routing
    r3 = sch.components.add("Device:R", "R3", "3k", Point(25.4, 25.4))    # Bottom left
    r4 = sch.components.add("Device:R", "R4", "4k", Point(76.2, 76.2))    # Top right
    
    print(f"📍 Component layout:")
    print(f"   R1 (1k) at {r1.position} - Start point")
    print(f"   ROBS (100Ω) at {r_obs.position} - Obstacle")  
    print(f"   R2 (2k) at {r2.position} - End point")
    print(f"   R3 (3k) at {r3.position} - Bottom connection")
    print(f"   R4 (4k) at {r4.position} - Top connection")
    
    # Test Manhattan routing around obstacles
    print(f"\n🔧 Testing Manhattan routing...")
    
    # Route 1: R1 to R2 (must go around ROBS)
    wire1 = sch.auto_route_pins("R1", "2", "R2", "1", 
                               routing_mode="manhattan", 
                               clearance=2.54)
    
    if wire1:
        print(f"✅ R1→R2 Manhattan route: {wire1}")
    else:
        print(f"❌ Failed Manhattan routing R1→R2")
    
    # Route 2: R1 to R3 (vertical routing)
    wire2 = sch.auto_route_pins("R1", "1", "R3", "1", 
                               routing_mode="manhattan")
    
    if wire2:
        print(f"✅ R1→R3 Manhattan route: {wire2}")
    else:
        print(f"❌ Failed Manhattan routing R1→R3")
    
    # Route 3: R2 to R4 (diagonal with Manhattan)
    wire3 = sch.auto_route_pins("R2", "2", "R4", "1", 
                               routing_mode="manhattan",
                               clearance=5.08)  # Larger clearance
    
    if wire3:
        print(f"✅ R2→R4 Manhattan route: {wire3}")
    else:
        print(f"❌ Failed Manhattan routing R2→R4")
    
    # Add bounding box visualization
    print(f"\n📦 Adding bounding box visualization...")
    
    # Draw actual bounding box rectangles
    bbox_uuids = sch.draw_component_bounding_boxes(
        include_properties=False,
        stroke_width=0.254,
        stroke_color="red"
    )
    print(f"   Drew {len(bbox_uuids)} red bounding box rectangles")
    
    # Also add corner text markers for reference
    from kicad_sch_api.core.component_bounds import get_component_bounding_box
    
    for comp in [r1, r_obs, r2, r3, r4]:
        bbox = get_component_bounding_box(comp, include_properties=False)
        
        # Add small corner markers
        sch.add_text(f"{comp.reference[:2]}", Point(bbox.min_x-1, bbox.max_y+1), size=0.5)
        print(f"   {comp.reference}: {bbox.width:.1f}×{bbox.height:.1f}mm")
    
    # Save and open
    filename = "manhattan_routing_demo.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("🔍 Look for L-shaped wires that avoid the center obstacle!")
    except Exception as e:
        print(f"⚠️  Could not auto-open KiCAD: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()