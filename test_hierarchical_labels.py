#!/usr/bin/env python3
"""
Test hierarchical label connectivity detection.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point, HierarchicalLabelShape

def test_hierarchical_labels():
    print("🏗️  Hierarchical Label Connectivity Test")
    print("=" * 50)
    
    # Create schematic
    sch = ksa.create_schematic("Hierarchical Test")
    
    # Add components
    r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))  
    r2 = sch.components.add("Device:R", "R2", "2k", Point(150, 50))
    
    print(f"📍 Added R1 at {r1.position}")
    print(f"📍 Added R2 at {r2.position}")
    
    # Get pin positions
    r1_pin1 = sch.get_component_pin_position("R1", "1")
    r2_pin1 = sch.get_component_pin_position("R2", "1")
    
    # Add wires to hierarchical label points
    hier1_point = Point(r1_pin1.x - 10, r1_pin1.y)
    hier2_point = Point(r2_pin1.x + 10, r2_pin1.y)
    
    sch.add_wire(r1_pin1, hier1_point)
    sch.add_wire(r2_pin1, hier2_point)
    
    # Add hierarchical labels with same name
    sch.add_hierarchical_label("CLK", position=Point(hier1_point.x - 3, hier1_point.y + 1), shape=HierarchicalLabelShape.INPUT)
    sch.add_hierarchical_label("CLK", position=Point(hier2_point.x + 3, hier2_point.y + 1), shape=HierarchicalLabelShape.OUTPUT)
    
    print(f"\n🏗️  Added hierarchical labels:")
    print(f"   R1 pin 1 → CLK (input)")  
    print(f"   R2 pin 1 → CLK (output)")
    
    # Test connectivity
    print(f"\n🔍 Hierarchical connectivity test:")
    connected = sch.are_pins_connected("R1", "1", "R2", "1")
    print(f"   R1 pin 1 ↔ R2 pin 1 (via CLK labels): {connected}")
    
    # Test with different hierarchical label names
    r1_pin2 = sch.get_component_pin_position("R1", "2")
    r2_pin2 = sch.get_component_pin_position("R2", "2")
    
    hier3_point = Point(r1_pin2.x - 10, r1_pin2.y)
    hier4_point = Point(r2_pin2.x + 10, r2_pin2.y)
    
    sch.add_wire(r1_pin2, hier3_point)
    sch.add_wire(r2_pin2, hier4_point)
    
    sch.add_hierarchical_label("DATA", position=Point(hier3_point.x - 3, hier3_point.y + 1), shape=HierarchicalLabelShape.BIDIRECTIONAL)
    sch.add_hierarchical_label("RESET", position=Point(hier4_point.x + 3, hier4_point.y + 1), shape=HierarchicalLabelShape.OUTPUT)
    
    print(f"   R1 pin 2 → DATA (bidirectional)")
    print(f"   R2 pin 2 → RESET (output)")
    
    different_labels = sch.are_pins_connected("R1", "2", "R2", "2")
    print(f"   R1 pin 2 ↔ R2 pin 2 (DATA vs RESET): {different_labels}")
    
    # Save for inspection
    sch.save("test_hierarchical_labels.kicad_sch")
    print(f"\n💾 Saved: test_hierarchical_labels.kicad_sch")
    
    # Summary
    print(f"\n📊 Results:")
    print(f"   Same hierarchical label (CLK): {connected} (expected: True)")
    print(f"   Different labels (DATA vs RESET): {different_labels} (expected: False)")
    
    if connected and not different_labels:
        print(f"   ✅ PASS - Hierarchical label detection working!")
    else:
        print(f"   ❌ FAIL - Issues with hierarchical label detection")
    
    return connected, different_labels


if __name__ == "__main__":
    test_hierarchical_labels()