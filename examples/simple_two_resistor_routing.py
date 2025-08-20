#!/usr/bin/env python3
"""
Simple two-resistor routing demonstration.

This example shows the new wire routing capabilities for automatically
placing two resistors at random locations and routing wires between them
using different strategies.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.wire_routing import SimpleWireRouter, RoutingStrategy

def main():
    """Demonstrate automatic wire routing between two randomly placed resistors."""
    print("🔧 Two-Resistor Auto Routing Demo")
    print("=" * 50)
    
    # Create schematic
    sch = ksa.create_schematic("Auto Routing Demo")
    
    # Initialize router
    router = SimpleWireRouter()
    
    # Generate random positions for components
    print("📍 Placing components randomly...")
    positions = router.place_components_randomly(board_size=(200.0, 150.0))
    
    # Add two resistors at the random positions
    r1 = sch.components.add("Device:R", "R1", "1k", positions[0])
    r2 = sch.components.add("Device:R", "R2", "2k", positions[1])
    
    print(f"   R1: {r1.reference} ({r1.value}) at ({r1.position.x:.1f}, {r1.position.y:.1f})")
    print(f"   R2: {r2.reference} ({r2.value}) at ({r2.position.x:.1f}, {r2.position.y:.1f})")
    
    # Get pin positions for routing
    r1_pin1_pos = sch.get_component_pin_position("R1", "1")
    r1_pin2_pos = sch.get_component_pin_position("R1", "2") 
    r2_pin1_pos = sch.get_component_pin_position("R2", "1")
    r2_pin2_pos = sch.get_component_pin_position("R2", "2")
    
    print(f"\n📐 Pin positions:")
    print(f"   R1 pin 1: ({r1_pin1_pos.x:.2f}, {r1_pin1_pos.y:.2f})")
    print(f"   R1 pin 2: ({r1_pin2_pos.x:.2f}, {r1_pin2_pos.y:.2f})")
    print(f"   R2 pin 1: ({r2_pin1_pos.x:.2f}, {r2_pin1_pos.y:.2f})")
    print(f"   R2 pin 2: ({r2_pin2_pos.x:.2f}, {r2_pin2_pos.y:.2f})")
    
    # Route between resistors using different strategies
    print(f"\n🔗 Routing wires between resistors...")
    
    # Strategy 1: Direct routing (R1 pin 2 to R2 pin 1)
    print(f"   Strategy 1: Direct routing")
    direct_path = router.route_between_pins(r1_pin2_pos, r2_pin1_pos, RoutingStrategy.DIRECT)
    direct_wire_segments = []
    
    for i in range(len(direct_path) - 1):
        wire_uuid = sch.add_wire(direct_path[i], direct_path[i + 1])
        direct_wire_segments.append(wire_uuid)
        print(f"      Wire segment: ({direct_path[i].x:.1f}, {direct_path[i].y:.1f}) → ({direct_path[i + 1].x:.1f}, {direct_path[i + 1].y:.1f})")
    
    # Strategy 2: Manhattan routing (R1 pin 1 to external point, R2 pin 2 to external point)
    print(f"   Strategy 2: Manhattan routing to external points")
    
    # External connection points
    from kicad_sch_api.core.types import Point
    vin_point = Point(25.0, r1_pin1_pos.y)  # Left side input
    gnd_point = Point(175.0, r2_pin2_pos.y)  # Right side ground
    
    # Route to VIN
    vin_path = router.route_between_pins(vin_point, r1_pin1_pos, RoutingStrategy.MANHATTAN)
    print(f"      VIN connection ({len(vin_path)} points): {vin_point} → {r1_pin1_pos}")
    for i in range(len(vin_path) - 1):
        wire_uuid = sch.add_wire(vin_path[i], vin_path[i + 1])
        print(f"         Segment: ({vin_path[i].x:.1f}, {vin_path[i].y:.1f}) → ({vin_path[i + 1].x:.1f}, {vin_path[i + 1].y:.1f})")
    
    # Route to GND
    gnd_path = router.route_between_pins(r2_pin2_pos, gnd_point, RoutingStrategy.MANHATTAN)
    print(f"      GND connection ({len(gnd_path)} points): {r2_pin2_pos} → {gnd_point}")
    for i in range(len(gnd_path) - 1):
        wire_uuid = sch.add_wire(gnd_path[i], gnd_path[i + 1])
        print(f"         Segment: ({gnd_path[i].x:.1f}, {gnd_path[i].y:.1f}) → ({gnd_path[i + 1].x:.1f}, {gnd_path[i + 1].y:.1f})")
    
    # Add labels for clarity
    print(f"\n🏷️  Adding net labels...")
    sch.add_label("VIN", position=(vin_point.x - 10, vin_point.y + 3))
    sch.add_label("VOUT", position=((r1_pin2_pos.x + r2_pin1_pos.x) / 2, (r1_pin2_pos.y + r2_pin1_pos.y) / 2 + 5))
    sch.add_label("GND", position=(gnd_point.x + 5, gnd_point.y + 3))
    
    # Show circuit summary
    print(f"\n📊 Circuit Summary:")
    print(f"   Components: {len(sch.components)}")
    print(f"   Wires: {len(sch.wires)}")
    print(f"   Labels: 3 (VIN, VOUT, GND)")
    
    # Calculate total wire length
    total_length = 0
    for wire in sch.wires:
        if len(wire.points) >= 2:
            length = wire.points[0].distance_to(wire.points[1])
            total_length += length
    
    print(f"   Total wire length: {total_length:.2f} mm")
    
    # Demonstrate routing path analysis
    print(f"\n🔍 Routing Analysis:")
    print(f"   Direct path points: {len(direct_path)}")
    print(f"   Manhattan VIN path points: {len(vin_path)}")  
    print(f"   Manhattan GND path points: {len(gnd_path)}")
    
    # Save the schematic
    output_file = "two_resistor_routing_demo.kicad_sch"
    sch.save(output_file)
    print(f"\n💾 Saved to: {output_file}")
    
    print(f"\n✨ Two-resistor routing demonstration complete!")
    print(f"   This demonstrates:")
    print(f"   - Random component placement with collision avoidance")
    print(f"   - Direct routing strategy for component-to-component connections")
    print(f"   - Manhattan routing strategy for external connections")
    print(f"   - Grid-aligned wire placement")
    print(f"   - Professional schematic layout generation")

if __name__ == "__main__":
    main()