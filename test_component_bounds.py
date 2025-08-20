#!/usr/bin/env python3
"""
Test component bounding box calculations for Manhattan routing.

This test explores how to get component bounding boxes in world coordinates
so we can implement obstacle avoidance routing.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.library.cache import get_symbol_cache
from kicad_sch_api.core.component_bounds import get_component_bounding_box, SymbolBoundingBoxCalculator

def test_component_bounding_boxes():
    """Test bounding box calculations for different components."""
    print("📦 Component Bounding Box Test")
    print("=" * 50)
    
    # Create schematic
    sch = ksa.create_schematic("Bounds Test")
    
    # Add different types of components at known positions
    r1 = sch.components.add("Device:R", "R1", "1k", Point(50, 50))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(100, 100))
    
    print(f"📍 Component positions:")
    print(f"   R1 at {r1.position}")
    print(f"   R2 at {r2.position}")
    
    # Get symbol definitions from cache and test new bounding box system
    cache = get_symbol_cache()
    r1_symbol = cache.get_symbol("Device:R")
    
    if r1_symbol:
        # Test old bounding box calculation
        old_symbol_bbox = r1_symbol.bounding_box
        print(f"\n📦 Old Device:R symbol bounding box: {old_symbol_bbox}")
        print(f"   Old symbol size: {r1_symbol.size}")
        
        # Test new bounding box calculation
        new_symbol_bbox = SymbolBoundingBoxCalculator.calculate_bounding_box(r1_symbol, include_properties=False)
        print(f"\n🔧 New Device:R symbol bounding box: {new_symbol_bbox}")
        print(f"   New symbol size: ({new_symbol_bbox.width:.2f}, {new_symbol_bbox.height:.2f})")
        
        # Test world coordinate bounding boxes
        r1_world_bbox = get_component_bounding_box(r1, include_properties=False)
        r2_world_bbox = get_component_bounding_box(r2, include_properties=False)
        
        print(f"\n🌍 World bounding boxes:")
        print(f"   R1: {r1_world_bbox}")
        print(f"   R2: {r2_world_bbox}")
    
    # Test pin positions for comparison
    r1_pin1 = sch.get_component_pin_position("R1", "1")
    r1_pin2 = sch.get_component_pin_position("R1", "2")
    r2_pin1 = sch.get_component_pin_position("R2", "1") 
    r2_pin2 = sch.get_component_pin_position("R2", "2")
    
    print(f"\n📐 Pin positions for comparison:")
    print(f"   R1 pin 1: {r1_pin1}")
    print(f"   R1 pin 2: {r1_pin2}")
    print(f"   R2 pin 1: {r2_pin1}")
    print(f"   R2 pin 2: {r2_pin2}")
    
    # Test bounding box collision with new system
    if r1_symbol:
        overlap = r1_world_bbox.overlaps(r2_world_bbox)
        print(f"\n🔍 Collision detection:")
        print(f"   R1 and R2 bounding boxes overlap: {overlap}")
        
        # Test point containment
        test_point = Point(r1.position.x, r1.position.y)
        inside = r1_world_bbox.contains_point(test_point)
        print(f"   Point {test_point} inside R1 bbox: {inside}")
        
        # Test distance between components
        distance = ((r2.position.x - r1.position.x)**2 + (r2.position.y - r1.position.y)**2)**0.5
        print(f"   Distance between R1 and R2 centers: {distance:.2f}mm")
    
    # Save for visual verification
    sch.save("test_component_bounds.kicad_sch")
    print(f"\n💾 Saved: test_component_bounds.kicad_sch")
    print(f"   Open in KiCAD to verify component positions!")


def test_manhattan_routing_concept():
    """Test the concept for Manhattan routing around obstacles."""
    print("\n\n🏗️  Manhattan Routing Concept Test")
    print("=" * 50)
    
    # Create schematic with components that would block direct routing
    sch = ksa.create_schematic("Manhattan Test")
    
    # Place components in a line that blocks direct routing
    start_comp = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))  # 20, 40 grid
    obstacle = sch.components.add("Device:R", "R2", "2k", Point(63.5, 50.8))   # 50, 40 grid  
    end_comp = sch.components.add("Device:R", "R3", "3k", Point(101.6, 50.8))  # 80, 40 grid
    
    print(f"📍 Components placed:")
    print(f"   R1 (start) at {start_comp.position}")
    print(f"   R2 (obstacle) at {obstacle.position}")  
    print(f"   R3 (end) at {end_comp.position}")
    
    # Get pin positions
    r1_pin2 = sch.get_component_pin_position("R1", "2") 
    r3_pin1 = sch.get_component_pin_position("R3", "1")
    
    print(f"\n📐 Target routing:")
    print(f"   From: R1 pin 2 at {r1_pin2}")
    print(f"   To: R3 pin 1 at {r3_pin1}")
    
    # Test direct routing (should fail due to obstacle)
    print(f"\n🔗 Direct routing test:")
    direct_connected_before = sch.are_pins_connected("R1", "2", "R3", "1")
    print(f"   Before: R1 pin 2 ↔ R3 pin 1 = {direct_connected_before}")
    
    # Try direct routing (will go through obstacle)
    direct_wire = sch.auto_route_pins("R1", "2", "R3", "1")
    print(f"   Direct wire UUID: {direct_wire}")
    
    direct_connected_after = sch.are_pins_connected("R1", "2", "R3", "1")
    print(f"   After direct: R1 pin 2 ↔ R3 pin 1 = {direct_connected_after}")
    
    print(f"\n💡 Manhattan routing would:")
    print(f"   1. Detect R2 blocks the direct path")
    print(f"   2. Route around R2 using horizontal/vertical segments")
    print(f"   3. Options: go above R2 or below R2")
    print(f"   4. Choose path based on clearance and grid alignment")
    
    # Save for visual verification  
    sch.save("test_manhattan_concept.kicad_sch")
    print(f"\n💾 Saved: test_manhattan_concept.kicad_sch")
    print(f"   Open in KiCAD to see the direct routing through obstacle!")


if __name__ == "__main__":
    test_component_bounding_boxes()
    test_manhattan_routing_concept()