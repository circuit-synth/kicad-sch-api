#!/usr/bin/env python3
"""
Compare direct vs Manhattan routing side by side.
Shows the difference between routing strategies.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    print("⚖️  Creating Routing Comparison Example...")
    
    # Create schematic
    sch = ksa.create_schematic("Direct vs Manhattan Routing")
    
    # Left side: Direct routing example
    print(f"\n📍 Left side: Direct routing")
    r1_direct = sch.components.add("Device:R", "R1", "1k", Point(20, 60))
    r2_direct = sch.components.add("Device:R", "R2", "100", Point(35, 60))  # Obstacle
    r3_direct = sch.components.add("Device:R", "R3", "2k", Point(50, 60))
    
    # Right side: Manhattan routing example  
    print(f"📍 Right side: Manhattan routing")
    r4_manhattan = sch.components.add("Device:R", "R4", "1k", Point(70, 60))
    r5_manhattan = sch.components.add("Device:R", "R5", "100", Point(85, 60))  # Obstacle
    r6_manhattan = sch.components.add("Device:R", "R6", "2k", Point(100, 60))
    
    # Add labels
    sch.add_text("DIRECT ROUTING", Point(35, 70), size=1.5)
    sch.add_text("(goes through obstacles)", Point(35, 67), size=1.0)
    
    sch.add_text("MANHATTAN ROUTING", Point(85, 70), size=1.5)  
    sch.add_text("(avoids obstacles)", Point(85, 67), size=1.0)
    
    # Route with direct method (left side)
    wire_direct = sch.auto_route_pins("R1", "2", "R3", "1", routing_mode="direct")
    if wire_direct:
        print(f"✅ Direct route: {wire_direct}")
    
    # Route with Manhattan method (right side)
    wire_manhattan = sch.auto_route_pins("R4", "2", "R6", "1", 
                                       routing_mode="manhattan", 
                                       clearance=2.54)
    if wire_manhattan:
        print(f"✅ Manhattan route: {wire_manhattan}")
    
    # Add some vertical connections to show L-shapes better
    r7 = sch.components.add("Device:R", "R7", "3k", Point(85, 40))
    wire_l_shape = sch.auto_route_pins("R5", "1", "R7", "1", 
                                     routing_mode="manhattan")
    if wire_l_shape:
        print(f"✅ L-shaped route: {wire_l_shape}")
    
    # Test connectivity
    print(f"\n🔍 Testing connectivity:")
    direct_connected = sch.are_pins_connected("R1", "2", "R3", "1")
    manhattan_connected = sch.are_pins_connected("R4", "2", "R6", "1")
    l_shape_connected = sch.are_pins_connected("R5", "1", "R7", "1")
    
    print(f"   Direct routing connected: {direct_connected}")
    print(f"   Manhattan routing connected: {manhattan_connected}")
    print(f"   L-shape routing connected: {l_shape_connected}")
    
    # Save and open
    filename = "routing_comparison_demo.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
        print("👀 Compare the routing styles side by side!")
    except Exception as e:
        print(f"⚠️  Could not auto-open KiCAD: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()