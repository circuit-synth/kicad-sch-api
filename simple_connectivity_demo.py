#!/usr/bin/env python3
"""
Simple connectivity detection demonstration.

Shows the two main features:
1. Auto route between 2 pins 
2. Detect when 2 pins are connected via wires or labels
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def main():
    print("🔌 Simple KiCAD Connectivity Demo")
    print("=" * 40)
    
    # Create schematic
    sch = ksa.create_schematic("Simple Demo")
    
    # Add two resistors
    r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(100, 50))
    
    print(f"📍 Added R1 and R2")
    
    # Test 1: Auto routing between pins
    print(f"\n🔗 Test 1: Auto routing")
    connected_before = sch.are_pins_connected("R1", "2", "R2", "1")
    print(f"   Before: R1 pin 2 ↔ R2 pin 1 = {connected_before}")
    
    wire_uuid = sch.auto_route_pins("R1", "2", "R2", "1")
    print(f"   Auto routed wire: {wire_uuid}")
    
    connected_after = sch.are_pins_connected("R1", "2", "R2", "1") 
    print(f"   After: R1 pin 2 ↔ R2 pin 1 = {connected_after}")
    
    # Test 2: Label-based connectivity
    print(f"\n🏷️  Test 2: Label connectivity")
    
    # Add VCC labels to both R1 pin 1 and R2 pin 2
    r1_pin1 = sch.get_component_pin_position("R1", "1")
    r2_pin2 = sch.get_component_pin_position("R2", "2")
    
    # Short wires with VCC labels
    vcc1_point = Point(r1_pin1.x - 8, r1_pin1.y)
    vcc2_point = Point(r2_pin2.x + 8, r2_pin2.y)
    
    sch.add_wire(r1_pin1, vcc1_point)
    sch.add_wire(r2_pin2, vcc2_point)
    
    sch.add_label("VCC", position=Point(vcc1_point.x - 2, vcc1_point.y + 1))
    sch.add_label("VCC", position=Point(vcc2_point.x + 2, vcc2_point.y + 1))
    
    print(f"   Added VCC labels to R1 pin 1 and R2 pin 2")
    
    vcc_connected = sch.are_pins_connected("R1", "1", "R2", "2")
    print(f"   R1 pin 1 ↔ R2 pin 2 (both VCC) = {vcc_connected}")
    
    # Test 3: Mixed connectivity (wire + label)
    direct_and_label = sch.are_pins_connected("R1", "2", "R2", "2") 
    print(f"   R1 pin 2 ↔ R2 pin 2 (wire vs label) = {direct_and_label}")
    
    # Save result
    sch.save("simple_connectivity_demo.kicad_sch")
    print(f"\n💾 Saved: simple_connectivity_demo.kicad_sch")
    
    print(f"\n✨ Demo complete! Open the file in KiCAD to see:")
    print(f"   • Direct wire from R1 pin 2 to R2 pin 1")
    print(f"   • VCC labels connecting R1 pin 1 and R2 pin 2")
    print(f"   • Mixed connectivity detection working correctly")


if __name__ == "__main__":
    main()