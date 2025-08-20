#!/usr/bin/env python3
"""
Debug the Manhattan routing algorithm to identify pathfinding issues.
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.core.manhattan_routing import (
    ManhattanRouter, RoutingStrategy, GridPoint
)
from kicad_sch_api.core.component_bounds import get_component_bounding_box
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_simple_routing():
    """Debug a simple routing scenario step by step."""
    print("🔍 Debugging Simple Manhattan Routing")
    print("=" * 50)
    
    # Create a simple test case
    sch = ksa.create_schematic("Debug Test")
    
    # Just two components with clear path
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))  
    r2 = sch.components.add("Device:R", "R2", "2k", Point(76.2, 50.8))   # Far enough apart
    
    r1_pin2 = sch.get_component_pin_position("R1", "2")
    r2_pin1 = sch.get_component_pin_position("R2", "1")
    
    print(f"📍 Simple layout:")
    print(f"   R1 at {r1.position}, pin 2 at {r1_pin2}")
    print(f"   R2 at {r2.position}, pin 1 at {r2_pin1}")
    
    # Get bounding boxes
    r1_bbox = get_component_bounding_box(r1, include_properties=False)
    r2_bbox = get_component_bounding_box(r2, include_properties=False)
    
    print(f"\n📦 Bounding boxes:")
    print(f"   R1: {r1_bbox}")
    print(f"   R2: {r2_bbox}")
    
    # Check if direct path is clear (it should be)
    from kicad_sch_api.core.component_bounds import check_path_collision
    obstacles = [r1_bbox, r2_bbox]
    collision = check_path_collision(r1_pin2, r2_pin1, obstacles, clearance=1.27)
    print(f"\n🚧 Direct path collision check: {collision}")
    
    # Try routing with debug
    router = ManhattanRouter()
    
    print(f"\n🛣️  Attempting routing...")
    path = router.route_between_points(
        r1_pin2, r2_pin1, obstacles, 
        RoutingStrategy.AESTHETIC, clearance=1.27
    )
    
    if path:
        print(f"✅ Route found: {len(path)} waypoints")
        for i, point in enumerate(path):
            print(f"   {i}: {point}")
    else:
        print(f"❌ No route found")
    
    # Let's try without any obstacles
    print(f"\n🔓 Trying without obstacles...")
    path_no_obs = router.route_between_points(
        r1_pin2, r2_pin1, [], 
        RoutingStrategy.AESTHETIC, clearance=1.27
    )
    
    if path_no_obs:
        print(f"✅ Route without obstacles: {len(path_no_obs)} waypoints")
        for i, point in enumerate(path_no_obs):
            print(f"   {i}: {point}")
    else:
        print(f"❌ No route found even without obstacles")


def debug_grid_conversion():
    """Debug grid coordinate conversions."""
    print("\n\n🔧 Debugging Grid Conversions")
    print("=" * 50)
    
    test_points = [
        Point(25.4, 46.99),   # R1 pin 2
        Point(76.2, 54.61),   # R2 pin 1 (approximate)
    ]
    
    for point in test_points:
        grid_point = GridPoint.from_world_point(point)
        back_to_world = grid_point.to_world_point()
        
        print(f"World: {point}")
        print(f"  → Grid: ({grid_point.x}, {grid_point.y})")
        print(f"  → Back to world: {back_to_world}")
        print(f"  → Grid distance: {abs(point.x - back_to_world.x):.3f}, {abs(point.y - back_to_world.y):.3f}")
        print()


def debug_routing_grid():
    """Debug routing grid construction."""
    print("\n\n🗺️  Debugging Routing Grid Construction")
    print("=" * 50)
    
    # Simple case with one obstacle
    sch = ksa.create_schematic("Grid Debug")
    obstacle_comp = sch.components.add("Device:R", "OBS", "1k", Point(50.8, 50.8))
    obstacle_bbox = get_component_bounding_box(obstacle_comp, include_properties=False)
    
    start = Point(25.4, 50.8)
    end = Point(76.2, 50.8)
    
    print(f"Start: {start}, End: {end}")
    print(f"Obstacle bbox: {obstacle_bbox}")
    
    router = ManhattanRouter()
    grid = router._build_routing_grid([obstacle_bbox], 1.27, start, end)
    
    print(f"\nRouting grid:")
    print(f"  Grid size: {grid.grid_size}mm")
    print(f"  Boundaries: {grid.boundaries}")
    print(f"  Obstacle points: {len(grid.obstacles)}")
    print(f"  Clearance points: {len(grid.clearance_map)}")
    
    # Show some obstacle points
    if grid.obstacles:
        print(f"\nSample obstacle points:")
        for i, obs_point in enumerate(list(grid.obstacles)[:10]):
            world_point = obs_point.to_world_point(grid.grid_size)
            print(f"   Grid ({obs_point.x}, {obs_point.y}) → World {world_point}")
    
    # Test pathfinding on this grid
    start_grid = GridPoint.from_world_point(start)
    end_grid = GridPoint.from_world_point(end)
    
    print(f"\nGrid coordinates:")
    print(f"  Start: ({start_grid.x}, {start_grid.y})")
    print(f"  End: ({end_grid.x}, {end_grid.y})")
    print(f"  Start valid: {grid.is_valid_point(start_grid)}")
    print(f"  End valid: {grid.is_valid_point(end_grid)}")
    
    # Check neighbors of start
    start_neighbors = grid.get_neighbors(start_grid)
    print(f"  Start neighbors: {len(start_neighbors)}")
    for neighbor in start_neighbors[:5]:  # Show first 5
        world_neighbor = neighbor.to_world_point(grid.grid_size)
        print(f"    Grid ({neighbor.x}, {neighbor.y}) → World {world_neighbor}")


if __name__ == "__main__":
    debug_simple_routing()
    debug_grid_conversion()
    debug_routing_grid()