#!/usr/bin/env python3
"""
Simple script to try direct routing between components.
Creates a basic resistor divider circuit with direct wires.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    print("🔧 Creating Direct Routing Example...")
    
    # Create schematic
    sch = ksa.create_schematic("Direct Routing Demo")
    
    # Add components in a line
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(50.8, 50.8))  
    r3 = sch.components.add("Device:R", "R3", "3k", Point(76.2, 50.8))
    
    print(f"📍 Added components:")
    print(f"   R1 (1k) at {r1.position}")
    print(f"   R2 (2k) at {r2.position}")
    print(f"   R3 (3k) at {r3.position}")
    
    # Connect with direct routing (goes straight through)
    wire1 = sch.auto_route_pins("R1", "2", "R3", "1")  # Default: direct routing
    
    if wire1:
        print(f"✅ Connected R1-pin2 to R3-pin1: {wire1}")
    else:
        print(f"❌ Failed to connect R1 to R3")
    
    # Add another direct connection
    wire2 = sch.auto_route_pins("R1", "1", "R2", "1", routing_mode="direct")
    
    if wire2:
        print(f"✅ Connected R1-pin1 to R2-pin1: {wire2}")
    else:
        print(f"❌ Failed to connect R1 to R2")
    
    # Save and open
    filename = "direct_routing_demo.kicad_sch"
    sch.save(filename)
    print(f"💾 Saved: {filename}")
    
    # Open in KiCAD
    import subprocess
    try:
        subprocess.run(["open", filename], check=True)
        print("📖 Opening in KiCAD...")
    except Exception as e:
        print(f"⚠️  Could not auto-open KiCAD: {e}")
        print(f"📁 Manually open: {filename}")

if __name__ == "__main__":
    main()