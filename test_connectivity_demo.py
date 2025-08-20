#!/usr/bin/env python3
"""
Practical connectivity detection test - directly observable results.

This test creates real circuits and shows exactly what the connectivity 
detection finds. You can open the generated .kicad_sch files in KiCAD
to verify the results visually.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

def test_direct_wire_connections():
    """Test 1: Direct wire connections - most basic case."""
    print("=" * 60)
    print("🔌 TEST 1: Direct Wire Connections")
    print("=" * 60)
    
    # Create schematic with two resistors
    sch = ksa.create_schematic("Direct Wire Test")
    
    # Add components at specific positions
    r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(100, 50))
    
    print(f"📍 Component positions:")
    print(f"   R1 at {r1.position}")
    print(f"   R2 at {r2.position}")
    
    # Get pin positions
    r1_pin1 = sch.get_component_pin_position("R1", "1")
    r1_pin2 = sch.get_component_pin_position("R1", "2")
    r2_pin1 = sch.get_component_pin_position("R2", "1") 
    r2_pin2 = sch.get_component_pin_position("R2", "2")
    
    print(f"\n📐 Pin positions:")
    print(f"   R1 pin 1: {r1_pin1}")
    print(f"   R1 pin 2: {r1_pin2}")
    print(f"   R2 pin 1: {r2_pin1}")
    print(f"   R2 pin 2: {r2_pin2}")
    
    # Test connectivity BEFORE connecting
    print(f"\n🔍 BEFORE connecting:")
    connected_before = sch.are_pins_connected("R1", "2", "R2", "1")
    print(f"   R1 pin 2 ↔ R2 pin 1: {connected_before}")
    
    # Auto route between R1 pin 2 and R2 pin 1
    print(f"\n🔗 Creating direct wire connection...")
    wire_uuid = sch.auto_route_pins("R1", "2", "R2", "1")
    print(f"   Wire UUID: {wire_uuid}")
    
    # Test connectivity AFTER connecting  
    print(f"\n🔍 AFTER connecting:")
    connected_after = sch.are_pins_connected("R1", "2", "R2", "1")
    print(f"   R1 pin 2 ↔ R2 pin 1: {connected_after}")
    
    # Test other pin combinations
    print(f"\n🔍 Other pin combinations:")
    print(f"   R1 pin 1 ↔ R1 pin 2: {sch.are_pins_connected('R1', '1', 'R1', '2')}")
    print(f"   R1 pin 1 ↔ R2 pin 1: {sch.are_pins_connected('R1', '1', 'R2', '1')}")
    print(f"   R1 pin 1 ↔ R2 pin 2: {sch.are_pins_connected('R1', '1', 'R2', '2')}")
    print(f"   R2 pin 1 ↔ R2 pin 2: {sch.are_pins_connected('R2', '1', 'R2', '2')}")
    
    # Save for visual verification
    filename = "test_direct_wire_connections.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved to: {filename}")
    print(f"   Open in KiCAD to verify the wire connection visually!")
    
    return connected_before, connected_after


def test_label_connections():
    """Test 2: Local label connections."""
    print("\n\n" + "=" * 60)
    print("🏷️  TEST 2: Local Label Connections")
    print("=" * 60)
    
    # Create schematic with components
    sch = ksa.create_schematic("Label Connection Test")
    
    # Add components - spread them out so no direct wires
    r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(150, 50))
    r3 = sch.components.add("Device:R", "R3", "3k", Point(50, 100))
    
    print(f"📍 Component positions:")
    print(f"   R1 at {r1.position}")
    print(f"   R2 at {r2.position}") 
    print(f"   R3 at {r3.position}")
    
    # Connect R1 pin 1 to a short wire with VCC label
    r1_pin1 = sch.get_component_pin_position("R1", "1")
    vcc_point = Point(r1_pin1.x - 10, r1_pin1.y)
    sch.add_wire(r1_pin1, vcc_point)
    sch.add_label("VCC", position=Point(vcc_point.x - 2, vcc_point.y + 1))  # Closer to wire
    
    # Connect R2 pin 1 to a short wire with VCC label  
    r2_pin1 = sch.get_component_pin_position("R2", "1")
    vcc_point2 = Point(r2_pin1.x - 10, r2_pin1.y)
    sch.add_wire(r2_pin1, vcc_point2)
    sch.add_label("VCC", position=Point(vcc_point2.x - 2, vcc_point2.y + 1))  # Closer to wire
    
    # Connect R3 pin 1 to a short wire with GND label (different net)
    r3_pin1 = sch.get_component_pin_position("R3", "1")
    gnd_point = Point(r3_pin1.x - 10, r3_pin1.y)
    sch.add_wire(r3_pin1, gnd_point)
    sch.add_label("GND", position=Point(gnd_point.x - 2, gnd_point.y + 1))  # Closer to wire
    
    print(f"\n🏷️  Added labels:")
    print(f"   R1 pin 1 → VCC label")
    print(f"   R2 pin 1 → VCC label")
    print(f"   R3 pin 1 → GND label")
    
    # Test connectivity via labels
    print(f"\n🔍 Label connectivity tests:")
    r1_r2_connected = sch.are_pins_connected("R1", "1", "R2", "1")
    r1_r3_connected = sch.are_pins_connected("R1", "1", "R3", "1")
    r2_r3_connected = sch.are_pins_connected("R2", "1", "R3", "1")
    
    print(f"   R1 pin 1 ↔ R2 pin 1 (both VCC): {r1_r2_connected}")
    print(f"   R1 pin 1 ↔ R3 pin 1 (VCC vs GND): {r1_r3_connected}")
    print(f"   R2 pin 1 ↔ R3 pin 1 (VCC vs GND): {r2_r3_connected}")
    
    # Save for visual verification
    filename = "test_label_connections.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved to: {filename}")
    print(f"   Open in KiCAD to see the VCC and GND labels!")
    
    return r1_r2_connected, r1_r3_connected, r2_r3_connected


def test_wire_network_connections():
    """Test 3: Multi-wire network connections."""
    print("\n\n" + "=" * 60)
    print("🕸️  TEST 3: Wire Network Connections")
    print("=" * 60)
    
    # Create schematic
    sch = ksa.create_schematic("Wire Network Test")
    
    # Add components in a line
    r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(100, 50))
    r3 = sch.components.add("Device:R", "R3", "3k", Point(150, 50))
    
    print(f"📍 Component positions:")
    print(f"   R1 at {r1.position}")
    print(f"   R2 at {r2.position}")
    print(f"   R3 at {r3.position}")
    
    # Create wire network: R1 pin 2 → junction → R2 pin 1 → R3 pin 1
    r1_pin2 = sch.get_component_pin_position("R1", "2")
    r2_pin1 = sch.get_component_pin_position("R2", "1")
    r2_pin2 = sch.get_component_pin_position("R2", "2")
    r3_pin1 = sch.get_component_pin_position("R3", "1")
    
    # Wire 1: R1 pin 2 to junction point
    junction = Point((r1_pin2.x + r2_pin1.x) / 2, r1_pin2.y)
    wire1 = sch.add_wire(r1_pin2, junction)
    
    # Wire 2: junction to R2 pin 1
    wire2 = sch.add_wire(junction, r2_pin1)
    
    # Wire 3: R2 pin 2 to R3 pin 1 (separate network)
    wire3 = sch.add_wire(r2_pin2, r3_pin1)
    
    print(f"\n🔗 Wire network created:")
    print(f"   Wire 1: R1 pin 2 → junction")
    print(f"   Wire 2: junction → R2 pin 1")  
    print(f"   Wire 3: R2 pin 2 → R3 pin 1 (separate)")
    
    # Test network connectivity
    print(f"\n🔍 Wire network connectivity tests:")
    r1_r2_net1 = sch.are_pins_connected("R1", "2", "R2", "1")  # Same network
    r2_r3_net2 = sch.are_pins_connected("R2", "2", "R3", "1")  # Same network  
    r1_r3_cross = sch.are_pins_connected("R1", "2", "R3", "1")  # Different networks
    r1_r2_different = sch.are_pins_connected("R1", "2", "R2", "2")  # Different networks
    
    print(f"   R1 pin 2 ↔ R2 pin 1 (same network): {r1_r2_net1}")
    print(f"   R2 pin 2 ↔ R3 pin 1 (same network): {r2_r3_net2}")
    print(f"   R1 pin 2 ↔ R3 pin 1 (cross networks): {r1_r3_cross}")
    print(f"   R1 pin 2 ↔ R2 pin 2 (cross networks): {r1_r2_different}")
    
    # Save for visual verification  
    filename = "test_wire_network_connections.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved to: {filename}")
    print(f"   Open in KiCAD to see the wire network topology!")
    
    return r1_r2_net1, r2_r3_net2, r1_r3_cross


def run_all_tests():
    """Run all connectivity tests with clear results."""
    print("🧪 KiCAD Connectivity Detection Test Suite")
    print("🧪 " + "=" * 50)
    print("   This test creates real KiCAD schematics you can open and verify!")
    print("")
    
    # Run all tests
    test1_results = test_direct_wire_connections()
    test2_results = test_label_connections() 
    test3_results = test_wire_network_connections()
    
    # Summary
    print("\n\n" + "🎯 " + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("🎯 " + "=" * 50)
    
    print(f"\n📊 Test 1 - Direct Wire Connections:")
    print(f"   Before connecting: {test1_results[0]} (expected: False)")
    print(f"   After connecting:  {test1_results[1]} (expected: True)")
    print(f"   ✅ PASS" if not test1_results[0] and test1_results[1] else "❌ FAIL")
    
    print(f"\n📊 Test 2 - Label Connections:")  
    print(f"   VCC ↔ VCC: {test2_results[0]} (expected: True)")
    print(f"   VCC ↔ GND: {test2_results[1]} (expected: False)")
    print(f"   VCC ↔ GND: {test2_results[2]} (expected: False)")
    expected_2 = test2_results[0] and not test2_results[1] and not test2_results[2]
    print(f"   ✅ PASS" if expected_2 else "❌ FAIL")
    
    print(f"\n📊 Test 3 - Wire Network Connections:")
    print(f"   Same network 1: {test3_results[0]} (expected: True)")
    print(f"   Same network 2: {test3_results[1]} (expected: True)")  
    print(f"   Cross networks: {test3_results[2]} (expected: False)")
    expected_3 = test3_results[0] and test3_results[1] and not test3_results[2]
    print(f"   ✅ PASS" if expected_3 else "❌ FAIL")
    
    print(f"\n🎉 Generated Files:")
    print(f"   • test_direct_wire_connections.kicad_sch")
    print(f"   • test_label_connections.kicad_sch")  
    print(f"   • test_wire_network_connections.kicad_sch")
    print(f"\n💡 Open these files in KiCAD to verify the connections visually!")


if __name__ == "__main__":
    run_all_tests()