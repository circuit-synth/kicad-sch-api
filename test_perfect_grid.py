#!/usr/bin/env python3
"""
Perfect KiCAD Grid Alignment Test.

This test places components so their PINS are exactly on the 1.27mm grid,
ensuring perfect electrical connectivity.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.core.wire_routing import snap_to_kicad_grid, get_resistor_grid_position

def test_perfect_grid_alignment():
    """Test with perfect grid alignment of component pins."""
    print("⚡ Perfect KiCAD Grid Alignment Test")
    print("=" * 60)
    print("   Component positions calculated so PINS are on 1.27mm grid")
    print()
    
    # Create schematic
    sch = ksa.create_schematic("Perfect Grid")
    
    # Define target pin positions on exact grid points
    r1_pin1_target = snap_to_kicad_grid(Point(50.8, 55.88))  # 40, 44 grid units
    r1_pin2_target = snap_to_kicad_grid(Point(50.8, 48.26))  # 40, 38 grid units  
    
    r2_pin1_target = snap_to_kicad_grid(Point(101.6, 55.88)) # 80, 44 grid units
    r2_pin2_target = snap_to_kicad_grid(Point(101.6, 48.26)) # 80, 38 grid units
    
    print(f"🎯 Target pin positions (on grid):")
    print(f"   R1 pin 1 target: {r1_pin1_target} (grid: {r1_pin1_target.x/1.27:.0f}, {r1_pin1_target.y/1.27:.0f})")
    print(f"   R1 pin 2 target: {r1_pin2_target} (grid: {r1_pin2_target.x/1.27:.0f}, {r1_pin2_target.y/1.27:.0f})")
    print(f"   R2 pin 1 target: {r2_pin1_target} (grid: {r2_pin1_target.x/1.27:.0f}, {r2_pin1_target.y/1.27:.0f})")
    print(f"   R2 pin 2 target: {r2_pin2_target} (grid: {r2_pin2_target.x/1.27:.0f}, {r2_pin2_target.y/1.27:.0f})")
    
    # Calculate component positions to achieve target pin positions
    r1_pos = get_resistor_grid_position(r1_pin1_target)
    r2_pos = get_resistor_grid_position(r2_pin1_target)
    
    print(f"\n📍 Calculated component positions:")
    print(f"   R1 center: {r1_pos}")
    print(f"   R2 center: {r2_pos}")
    
    # Add components
    r1 = sch.components.add("Device:R", "R1", "1k", r1_pos)
    r2 = sch.components.add("Device:R", "R2", "2k", r2_pos)
    
    # Verify actual pin positions
    r1_pin1_actual = sch.get_component_pin_position("R1", "1")
    r1_pin2_actual = sch.get_component_pin_position("R1", "2")
    r2_pin1_actual = sch.get_component_pin_position("R2", "1")
    r2_pin2_actual = sch.get_component_pin_position("R2", "2")
    
    print(f"\n📐 Actual pin positions:")
    print(f"   R1 pin 1: {r1_pin1_actual} (grid: {r1_pin1_actual.x/1.27:.1f}, {r1_pin1_actual.y/1.27:.1f})")
    print(f"   R1 pin 2: {r1_pin2_actual} (grid: {r1_pin2_actual.x/1.27:.1f}, {r1_pin2_actual.y/1.27:.1f})")
    print(f"   R2 pin 1: {r2_pin1_actual} (grid: {r2_pin1_actual.x/1.27:.1f}, {r2_pin1_actual.y/1.27:.1f})")
    print(f"   R2 pin 2: {r2_pin2_actual} (grid: {r2_pin2_actual.x/1.27:.1f}, {r2_pin2_actual.y/1.27:.1f})")
    
    # Verify pins are exactly on target positions
    pin1_match = (r1_pin1_actual.x == r1_pin1_target.x and r1_pin1_actual.y == r1_pin1_target.y)
    pin2_match = (r1_pin2_actual.x == r1_pin2_target.x and r1_pin2_actual.y == r1_pin2_target.y)
    pin3_match = (r2_pin1_actual.x == r2_pin1_target.x and r2_pin1_actual.y == r2_pin1_target.y)
    pin4_match = (r2_pin2_actual.x == r2_pin2_target.x and r2_pin2_actual.y == r2_pin2_target.y)
    
    print(f"\n✅ Pin position verification:")
    print(f"   R1 pin 1 exact match: {pin1_match}")
    print(f"   R1 pin 2 exact match: {pin2_match}")
    print(f"   R2 pin 1 exact match: {pin3_match}")
    print(f"   R2 pin 2 exact match: {pin4_match}")
    
    # Test 1: Direct wire connection between aligned pins
    print(f"\n🔗 Test 1: Direct Wire Connection")
    connected_before = sch.are_pins_connected("R1", "2", "R2", "1")
    print(f"   Before: R1 pin 2 ↔ R2 pin 1 = {connected_before}")
    
    wire_uuid = sch.auto_route_pins("R1", "2", "R2", "1")
    print(f"   Auto routed wire: {wire_uuid}")
    
    connected_after = sch.are_pins_connected("R1", "2", "R2", "1")
    print(f"   After: R1 pin 2 ↔ R2 pin 1 = {connected_after}")
    
    # Test 2: Label connections with perfect positioning
    print(f"\n🏷️  Test 2: Perfect Label Positioning")
    
    # Create VCC connection for R1 pin 1
    vcc_endpoint = snap_to_kicad_grid(Point(38.1, r1_pin1_actual.y))  # 30 grid units from left
    
    print(f"   VCC endpoint: {vcc_endpoint} (grid: {vcc_endpoint.x/1.27:.0f}, {vcc_endpoint.y/1.27:.0f})")
    
    # Add wire and label at exact positions
    sch.add_wire(r1_pin1_actual, vcc_endpoint)
    sch.add_label("VCC", position=vcc_endpoint)  # EXACT position on wire endpoint
    
    # Create GND connection for R2 pin 2  
    gnd_endpoint = snap_to_kicad_grid(Point(127.0, r2_pin2_actual.y))  # 100 grid units from left
    
    sch.add_wire(r2_pin2_actual, gnd_endpoint)
    sch.add_label("GND", position=gnd_endpoint)  # EXACT position on wire endpoint
    
    print(f"   GND endpoint: {gnd_endpoint} (grid: {gnd_endpoint.x/1.27:.0f}, {gnd_endpoint.y/1.27:.0f})")
    
    # Test connectivity
    print(f"\n🔍 Connectivity Tests:")
    direct_wire = sch.are_pins_connected("R1", "2", "R2", "1")  # Should be True (direct wire)
    vcc_to_r1 = sch.are_pins_connected("R1", "1", "R1", "1")    # Should be True (same pin)
    unconnected = sch.are_pins_connected("R1", "1", "R2", "2")  # Should be False (VCC vs GND)
    different_nets = sch.are_pins_connected("R1", "2", "R2", "2") # Should be False (wire vs GND)
    
    print(f"   Direct wire (R1-2 ↔ R2-1): {direct_wire}")
    print(f"   Same pin (R1-1 ↔ R1-1): {vcc_to_r1}") 
    print(f"   Unconnected (VCC ↔ GND): {unconnected}")
    print(f"   Different nets (wire ↔ GND): {different_nets}")
    
    # Save for inspection
    sch.save("test_perfect_grid.kicad_sch")
    print(f"\n💾 Saved: test_perfect_grid.kicad_sch")
    
    # Results summary
    all_pins_aligned = pin1_match and pin2_match and pin3_match and pin4_match
    connectivity_correct = direct_wire and vcc_to_r1 and not unconnected and not different_nets
    
    print(f"\n📊 Results Summary:")
    print(f"   All pins perfectly aligned: {all_pins_aligned}")
    print(f"   Direct wire connectivity: {direct_wire}")
    print(f"   All connectivity tests correct: {connectivity_correct}")
    
    if all_pins_aligned and connectivity_correct:
        print(f"\n   🎉 PERFECT SUCCESS! KiCAD precision connectivity working flawlessly!")
        print(f"      • All pins exactly on 1.27mm grid")
        print(f"      • Direct wire routing works")
        print(f"      • Labels placed exactly on wire endpoints") 
        print(f"      • Zero tolerance connectivity detection works")
    else:
        print(f"\n   ❌ Issues detected - check positioning or connectivity logic")
    
    print(f"\n💡 Open test_perfect_grid.kicad_sch in KiCAD to verify perfect alignment!")


if __name__ == "__main__":
    test_perfect_grid_alignment()