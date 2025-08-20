#!/usr/bin/env python3
"""
Demo script showing the new pin-to-pin wire drawing functionality.

This example demonstrates how to use the new wire drawing methods that 
automatically connect to component pins.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    """Demonstrate pin-to-pin wiring functionality."""
    print("🔧 Pin-to-Pin Wiring Demo")
    print("=" * 40)
    
    # Create a new schematic
    sch = ksa.create_schematic("Pin-to-Pin Wiring Demo")
    print(f"✅ Created schematic with {len(sch.components)} components")
    
    # Add some components
    print("\n📦 Adding components...")
    r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
    r2 = sch.components.add("Device:R", "R2", "20k", (200, 100))
    r3 = sch.components.add("Device:R", "R3", "30k", (150, 150))
    
    print(f"   R1: {r1.reference} at ({r1.position.x:.1f}, {r1.position.y:.1f})")
    print(f"   R2: {r2.reference} at ({r2.position.x:.1f}, {r2.position.y:.1f})")
    print(f"   R3: {r3.reference} at ({r3.position.x:.1f}, {r3.position.y:.1f})")
    
    # Show pin positions
    print("\n📍 Pin positions:")
    for comp_ref in ["R1", "R2", "R3"]:
        for pin_num in ["1", "2"]:
            pin_pos = sch.get_component_pin_position(comp_ref, pin_num)
            if pin_pos:
                print(f"   {comp_ref} pin {pin_num}: ({pin_pos.x:.2f}, {pin_pos.y:.2f})")
    
    # Draw wires between component pins
    print("\n🔗 Drawing wires between pins...")
    
    # Wire 1: Connect R1 pin 2 to R2 pin 1 (horizontal connection)
    wire1_uuid = sch.add_wire_between_pins("R1", "2", "R2", "1")
    print(f"   ✅ Connected R1 pin 2 → R2 pin 1 (UUID: {wire1_uuid[:8]}...)")
    
    # Wire 2: Connect R2 pin 2 to R3 pin 1 (diagonal connection) 
    wire2_uuid = sch.add_wire_between_pins("R2", "2", "R3", "1")
    print(f"   ✅ Connected R2 pin 2 → R3 pin 1 (UUID: {wire2_uuid[:8]}...)")
    
    # Wire 3: Connect arbitrary point to R1 pin 1
    start_point = Point(50, 100)
    wire3_uuid = sch.add_wire_to_pin(start_point, "R1", "1")
    print(f"   ✅ Connected external point ({start_point.x}, {start_point.y}) → R1 pin 1 (UUID: {wire3_uuid[:8]}...)")
    
    # Wire 4: Connect R3 pin 2 to an external point using tuple coordinates
    wire4_uuid = sch.add_wire_to_pin((150, 200), "R3", "2")  # Using tuple instead of Point
    print(f"   ✅ Connected R3 pin 2 → external point (150, 200) (UUID: {wire4_uuid[:8]}...)")
    
    # Show wire statistics
    print(f"\n📊 Wire statistics:")
    wire_stats = sch.wires.get_statistics()
    print(f"   Total wires: {wire_stats['total_wires']}")
    print(f"   Simple wires: {wire_stats['simple_wires']}")
    print(f"   Total length: {wire_stats['total_length']:.2f} mm")
    print(f"   Average length: {wire_stats['avg_length']:.2f} mm")
    
    # Show wire details
    print(f"\n🔍 Wire details:")
    for i, wire in enumerate(sch.wires, 1):
        start = wire.points[0]
        end = wire.points[1]
        length = start.distance_to(end)
        print(f"   Wire {i}: ({start.x:.2f}, {start.y:.2f}) → ({end.x:.2f}, {end.y:.2f}) [length: {length:.2f}mm]")
    
    # Demonstrate error handling
    print(f"\n❌ Error handling examples:")
    
    # Try to connect to non-existent component
    bad_wire1 = sch.add_wire_between_pins("R999", "1", "R1", "1")
    print(f"   Non-existent component R999: {bad_wire1} (should be None)")
    
    # Try to connect to non-existent pin
    bad_wire2 = sch.add_wire_between_pins("R1", "999", "R2", "1")
    print(f"   Non-existent pin 999: {bad_wire2} (should be None)")
    
    # Save the schematic
    output_file = "pin_to_pin_demo.kicad_sch"
    sch.save(output_file)
    print(f"\n💾 Saved schematic to: {output_file}")
    
    # Show final summary
    print(f"\n🎉 Demo complete!")
    print(f"   Components: {len(sch.components)}")
    print(f"   Wires: {len(sch.wires)}")
    print(f"   Modified: {sch.modified}")

if __name__ == "__main__":
    main()