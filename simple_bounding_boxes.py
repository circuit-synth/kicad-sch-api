#!/usr/bin/env python3
"""
Simple bounding box visualization and Manhattan routing.

Focus on core functionality:
1. Generate accurate component bounding boxes
2. Draw bounding boxes on schematic for visualization
3. Simple Manhattan routing between two points
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.core.component_bounds import get_component_bounding_box


def draw_bounding_box(schematic, bbox, label="BBox"):
    """
    Mark a bounding box on the schematic using text labels at corners.
    
    Args:
        schematic: The schematic to draw on
        bbox: BoundingBox to draw  
        label: Optional label for the box
    """
    # Add text markers at the four corners of bounding box
    # Top-left corner
    schematic.add_text(
        f"{label}_TL", 
        Point(bbox.min_x, bbox.max_y),
        size=0.8
    )
    
    # Top-right corner
    schematic.add_text(
        f"{label}_TR",
        Point(bbox.max_x, bbox.max_y), 
        size=0.8
    )
    
    # Bottom-left corner
    schematic.add_text(
        f"{label}_BL",
        Point(bbox.min_x, bbox.min_y),
        size=0.8
    )
    
    # Bottom-right corner
    schematic.add_text(
        f"{label}_BR",
        Point(bbox.max_x, bbox.min_y),
        size=0.8
    )
    
    # Add main label with bounding box info
    schematic.add_text(
        f"{label}: {bbox.width:.1f}x{bbox.height:.1f}mm", 
        Point(bbox.min_x, bbox.max_y + 2),
        size=1.0
    )


def simple_manhattan_route(start, end):
    """
    Create a simple L-shaped Manhattan route between two points.
    
    Args:
        start: Starting point
        end: Ending point
        
    Returns:
        List of waypoints for L-shaped route
    """
    # Simple L-route: horizontal first, then vertical
    if abs(start.x - end.x) > 0.1:  # Need horizontal segment
        if abs(start.y - end.y) > 0.1:  # Need vertical segment too
            # L-shaped route: start -> corner -> end
            corner = Point(end.x, start.y)
            return [start, corner, end]
        else:
            # Pure horizontal
            return [start, end]
    else:
        # Pure vertical
        return [start, end]


def test_simple_bounding_boxes():
    """Test simple bounding box generation and visualization."""
    print("📦 Simple Bounding Box Test")
    print("=" * 40)
    
    # Create schematic
    sch = ksa.create_schematic("Simple BBox Test")
    
    # Add some components at different positions
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(76.2, 50.8))
    r3 = sch.components.add("Device:R", "R3", "3k", Point(50.8, 25.4))
    
    components = [r1, r2, r3]
    
    print(f"📍 Added {len(components)} components:")
    for comp in components:
        print(f"   {comp.reference} at {comp.position}")
    
    # Generate and draw bounding boxes
    print(f"\n📦 Generating bounding boxes:")
    for comp in components:
        bbox = get_component_bounding_box(comp, include_properties=False)
        print(f"   {comp.reference}: {bbox}")
        print(f"      Size: {bbox.width:.2f} x {bbox.height:.2f} mm")
        
        # Draw bounding box on schematic
        draw_bounding_box(sch, bbox, f"{comp.reference}_bbox")
    
    # Save for visual inspection
    filename = "simple_bounding_boxes.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    print(f"   Open in KiCAD to see component bounding boxes drawn as graphic lines!")


def test_simple_manhattan_routing():
    """Test simple Manhattan routing."""
    print("\n\n🛣️  Simple Manhattan Routing Test")
    print("=" * 40)
    
    # Create schematic
    sch = ksa.create_schematic("Simple Manhattan Test")
    
    # Add two components
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(76.2, 25.4))
    
    print(f"📍 Components:")
    print(f"   R1 at {r1.position}")
    print(f"   R2 at {r2.position}")
    
    # Get pin positions
    r1_pin2 = sch.get_component_pin_position("R1", "2")
    r2_pin1 = sch.get_component_pin_position("R2", "1")
    
    print(f"\n🎯 Routing:")
    print(f"   From: {r1_pin2}")
    print(f"   To: {r2_pin1}")
    
    # Create simple Manhattan route
    route = simple_manhattan_route(r1_pin2, r2_pin1)
    print(f"\n📐 Route waypoints:")
    for i, point in enumerate(route):
        print(f"   {i}: {point}")
    
    # Add wires for the route
    for i in range(len(route) - 1):
        sch.add_wire(route[i], route[i + 1])
    
    # Draw bounding boxes for visualization
    for comp in [r1, r2]:
        bbox = get_component_bounding_box(comp, include_properties=False)
        draw_bounding_box(sch, bbox, f"{comp.reference}_bbox")
    
    # Save result
    filename = "simple_manhattan_routing.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    print(f"   Open in KiCAD to see the L-shaped Manhattan route!")


def test_obstacle_avoidance_concept():
    """Test concept of routing around obstacles."""
    print("\n\n🚧 Simple Obstacle Avoidance Concept")
    print("=" * 40)
    
    # Create schematic with obstacle
    sch = ksa.create_schematic("Obstacle Concept")
    
    # Layout: R1 -- [R2 obstacle] -- R3
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))
    r2 = sch.components.add("Device:R", "R2", "2k", Point(50.8, 50.8))  # Obstacle
    r3 = sch.components.add("Device:R", "R3", "3k", Point(76.2, 50.8))
    
    # Get routing points
    r1_pin2 = sch.get_component_pin_position("R1", "2")
    r3_pin1 = sch.get_component_pin_position("R3", "1")
    
    print(f"📍 Layout with obstacle:")
    print(f"   R1 at {r1.position}, pin 2: {r1_pin2}")
    print(f"   R2 (obstacle) at {r2.position}")
    print(f"   R3 at {r3.position}, pin 1: {r3_pin1}")
    
    # Get obstacle bounding box
    r2_bbox = get_component_bounding_box(r2, include_properties=False)
    print(f"\n📦 Obstacle bounding box: {r2_bbox}")
    
    # Check if direct path would intersect obstacle
    # Simple check: does the horizontal line from R1 to R3 pass through R2's bbox?
    direct_y = r1_pin2.y  # Horizontal line at this Y
    obstacle_blocks_direct = (
        r2_bbox.min_y <= direct_y <= r2_bbox.max_y and  # Line passes through bbox Y range
        r1_pin2.x < r2_bbox.max_x and r3_pin1.x > r2_bbox.min_x  # Line passes through bbox X range
    )
    
    print(f"\n🚧 Direct path analysis:")
    print(f"   Direct route Y: {direct_y:.2f}")
    print(f"   Obstacle Y range: {r2_bbox.min_y:.2f} to {r2_bbox.max_y:.2f}")
    print(f"   Obstacle blocks direct path: {obstacle_blocks_direct}")
    
    if obstacle_blocks_direct:
        # Route around obstacle - go above or below
        clearance = 2.54  # 2 grid units
        
        # Try routing above obstacle
        above_y = r2_bbox.max_y + clearance
        route_above = [
            r1_pin2,
            Point(r1_pin2.x, above_y),    # Go up
            Point(r3_pin1.x, above_y),    # Go across above obstacle
            r3_pin1                       # Go down to destination
        ]
        
        # Try routing below obstacle  
        below_y = r2_bbox.min_y - clearance
        route_below = [
            r1_pin2,
            Point(r1_pin2.x, below_y),    # Go down
            Point(r3_pin1.x, below_y),    # Go across below obstacle
            r3_pin1                       # Go up to destination
        ]
        
        print(f"\n🛣️  Routing options:")
        print(f"   Above obstacle (Y={above_y:.2f}): {len(route_above)} segments")
        print(f"   Below obstacle (Y={below_y:.2f}): {len(route_below)} segments")
        
        # Choose the route with shorter total distance
        def manhattan_distance(route):
            total = 0
            for i in range(len(route) - 1):
                total += abs(route[i+1].x - route[i].x) + abs(route[i+1].y - route[i].y)
            return total
        
        above_distance = manhattan_distance(route_above)
        below_distance = manhattan_distance(route_below)
        
        if above_distance <= below_distance:
            chosen_route = route_above
            choice = "above"
            distance = above_distance
        else:
            chosen_route = route_below
            choice = "below"
            distance = below_distance
        
        print(f"   Chosen: {choice} (distance: {distance:.1f}mm)")
        
        # Draw the chosen route
        for i in range(len(chosen_route) - 1):
            sch.add_wire(chosen_route[i], chosen_route[i + 1])
            
    else:
        # Direct route is clear
        direct_route = simple_manhattan_route(r1_pin2, r3_pin1)
        for i in range(len(direct_route) - 1):
            sch.add_wire(direct_route[i], direct_route[i + 1])
        print(f"   Direct route used")
    
    # Draw all bounding boxes
    for comp in [r1, r2, r3]:
        bbox = get_component_bounding_box(comp, include_properties=False)
        draw_bounding_box(sch, bbox, f"{comp.reference}_bbox")
    
    # Save result
    filename = "simple_obstacle_concept.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    print(f"   Open in KiCAD to see obstacle avoidance routing!")


def main():
    """Run simple bounding box and routing tests."""
    print("🔧 Simple Bounding Boxes & Manhattan Routing")
    print("🔧 " + "=" * 50)
    print("   Focus on core functionality with visual verification")
    print("")
    
    test_simple_bounding_boxes()
    test_simple_manhattan_routing()
    test_obstacle_avoidance_concept()
    
    print(f"\n\n✨ Simple Tests Complete!")
    print(f"✨ " + "=" * 30)
    print(f"   Generated files:")
    print(f"   • simple_bounding_boxes.kicad_sch - Bounding box visualization")
    print(f"   • simple_manhattan_routing.kicad_sch - Basic L-shaped routing")
    print(f"   • simple_obstacle_concept.kicad_sch - Simple obstacle avoidance")
    print(f"")
    print(f"💡 Open these files in KiCAD to see:")
    print(f"   📦 Component bounding boxes drawn as graphic rectangles")
    print(f"   🛣️  Manhattan routing with horizontal/vertical segments")
    print(f"   🚧 Simple obstacle avoidance (above/below routing)")


if __name__ == "__main__":
    main()