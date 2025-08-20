#!/usr/bin/env python3
"""
Comprehensive test for Manhattan routing with obstacle avoidance.

This test validates the Manhattan routing algorithm with various scenarios:
- Simple obstacle avoidance
- Different routing strategies  
- Complex multi-obstacle layouts
- Performance and reliability testing
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point
from kicad_sch_api.core.manhattan_routing import (
    ManhattanRouter, RoutingStrategy, route_around_obstacles, 
    GridPoint, RoutingGrid
)
from kicad_sch_api.core.component_bounds import get_component_bounding_box
from kicad_sch_api.core.wire_routing import snap_to_kicad_grid
import time


def test_basic_manhattan_routing():
    """Test basic Manhattan routing around a single obstacle."""
    print("🛣️  Test 1: Basic Manhattan Routing")
    print("=" * 50)
    
    # Create schematic with obstacle blocking direct path
    sch = ksa.create_schematic("Manhattan Basic Test")
    
    # Place components to create routing scenario
    # R1 ---- [R2 obstacle] ---- R3
    r1 = sch.components.add("Device:R", "R1", "1k", Point(25.4, 50.8))   # Left
    r2 = sch.components.add("Device:R", "R2", "2k", Point(63.5, 50.8))   # Obstacle in middle
    r3 = sch.components.add("Device:R", "R3", "3k", Point(101.6, 50.8))  # Right
    
    print(f"📍 Component layout:")
    print(f"   R1 (start): {r1.position}")
    print(f"   R2 (obstacle): {r2.position}")  
    print(f"   R3 (end): {r3.position}")
    
    # Get pin positions for routing
    r1_pin2 = sch.get_component_pin_position("R1", "2")  # Right pin of R1
    r3_pin1 = sch.get_component_pin_position("R3", "1")  # Left pin of R3
    
    print(f"\n🎯 Routing target:")
    print(f"   From: R1 pin 2 at {r1_pin2}")
    print(f"   To: R3 pin 1 at {r3_pin1}")
    
    # Test different routing strategies
    strategies = [
        RoutingStrategy.SHORTEST,
        RoutingStrategy.CLEARANCE, 
        RoutingStrategy.AESTHETIC
    ]
    
    components = [r1, r2, r3]
    
    for strategy in strategies:
        print(f"\n🔍 Testing {strategy.value} strategy:")
        
        start_time = time.time()
        path = route_around_obstacles(
            r1_pin2, r3_pin1, components, 
            strategy=strategy, 
            clearance=2.54  # 2 grid units clearance
        )
        routing_time = time.time() - start_time
        
        if path:
            print(f"   ✅ Success in {routing_time*1000:.1f}ms")
            print(f"   📏 Path length: {len(path)} waypoints")
            print(f"   🗺️  Route: {' → '.join([f'({p.x:.1f}, {p.y:.1f})' for p in path])}")
            
            # Calculate total Manhattan distance
            total_distance = 0
            for i in range(len(path) - 1):
                dx = abs(path[i+1].x - path[i].x)
                dy = abs(path[i+1].y - path[i].y) 
                total_distance += dx + dy
            print(f"   📐 Total distance: {total_distance:.1f}mm")
            
            # Add wires to schematic for this strategy
            for i in range(len(path) - 1):
                sch.add_wire(path[i], path[i + 1])
                
        else:
            print(f"   ❌ Failed in {routing_time*1000:.1f}ms")
    
    # Save schematic for visual inspection
    filename = "test_manhattan_basic.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")
    print(f"   Open in KiCAD to see the routed paths!")


def test_complex_obstacle_field():
    """Test routing through a complex field of obstacles."""
    print("\n\n🏗️  Test 2: Complex Obstacle Field")
    print("=" * 50)
    
    # Create schematic with multiple obstacles
    sch = ksa.create_schematic("Complex Obstacles Test")
    
    # Create a grid of obstacle components
    obstacles = []
    for row in range(3):
        for col in range(3):
            if (row, col) not in [(0, 0), (2, 2)]:  # Leave start and end clear
                x = 25.4 + col * 25.4  # 20mm spacing
                y = 25.4 + row * 25.4
                ref = f"R{row}{col}"
                comp = sch.components.add("Device:R", ref, "1k", Point(x, y))
                obstacles.append(comp)
    
    # Add start and end components
    start_comp = sch.components.add("Device:R", "START", "1k", Point(12.7, 12.7))
    end_comp = sch.components.add("Device:R", "END", "1k", Point(88.9, 88.9))
    
    all_components = obstacles + [start_comp, end_comp]
    
    print(f"📍 Created obstacle field with {len(obstacles)} obstacles")
    print(f"   Start: {start_comp.position}")
    print(f"   End: {end_comp.position}")
    
    # Get routing points
    start_pin = sch.get_component_pin_position("START", "2") 
    end_pin = sch.get_component_pin_position("END", "1")
    
    # Test routing through obstacle field
    print(f"\n🧭 Routing through obstacle field:")
    print(f"   From: {start_pin}")
    print(f"   To: {end_pin}")
    
    start_time = time.time()
    path = route_around_obstacles(
        start_pin, end_pin, all_components,
        strategy=RoutingStrategy.AESTHETIC,
        clearance=1.27
    )
    routing_time = time.time() - start_time
    
    if path:
        print(f"   ✅ Complex routing successful in {routing_time*1000:.1f}ms")
        print(f"   📏 Path has {len(path)} waypoints")
        
        # Add wires to schematic
        for i in range(len(path) - 1):
            sch.add_wire(path[i], path[i + 1])
        
        # Check grid alignment
        all_aligned = True
        for point in path:
            snapped = snap_to_kicad_grid(point)
            if abs(point.x - snapped.x) > 0.01 or abs(point.y - snapped.y) > 0.01:
                all_aligned = False
                break
        print(f"   🔧 Grid alignment: {'✅ Perfect' if all_aligned else '❌ Issues detected'}")
        
    else:
        print(f"   ❌ Complex routing failed in {routing_time*1000:.1f}ms")
    
    # Save result
    filename = "test_manhattan_complex.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")


def test_routing_strategies_comparison():
    """Compare different routing strategies on the same layout."""
    print("\n\n🎲 Test 3: Routing Strategy Comparison")
    print("=" * 50)
    
    # Create schematic with strategic obstacle placement
    sch = ksa.create_schematic("Strategy Comparison")
    
    # Layout: Start -- [Obstacle1]
    #              \     [Obstacle2] -- End
    start = sch.components.add("Device:R", "START", "1k", Point(25.4, 50.8))
    obs1 = sch.components.add("Device:R", "OBS1", "1k", Point(50.8, 50.8))  
    obs2 = sch.components.add("Device:R", "OBS2", "1k", Point(76.2, 38.1))
    end = sch.components.add("Device:R", "END", "1k", Point(101.6, 25.4))
    
    components = [start, obs1, obs2, end]
    
    start_pin = sch.get_component_pin_position("START", "2")
    end_pin = sch.get_component_pin_position("END", "1")
    
    print(f"📍 Strategic layout for comparison:")
    print(f"   Route: {start_pin} → {end_pin}")
    
    # Test each strategy and collect metrics
    strategies = [
        RoutingStrategy.SHORTEST,
        RoutingStrategy.CLEARANCE,
        RoutingStrategy.AESTHETIC
    ]
    
    results = {}
    
    for strategy in strategies:
        print(f"\n🎯 Testing {strategy.value.upper()} strategy:")
        
        start_time = time.time()
        path = route_around_obstacles(
            start_pin, end_pin, components,
            strategy=strategy,
            clearance=1.27
        )
        routing_time = time.time() - start_time
        
        if path:
            # Calculate metrics
            total_distance = sum(
                abs(path[i+1].x - path[i].x) + abs(path[i+1].y - path[i].y)
                for i in range(len(path) - 1)
            )
            
            # Count turns (direction changes)
            turns = 0
            if len(path) > 2:
                for i in range(1, len(path) - 1):
                    prev_dx = path[i].x - path[i-1].x
                    prev_dy = path[i].y - path[i-1].y
                    next_dx = path[i+1].x - path[i].x
                    next_dy = path[i+1].y - path[i].y
                    
                    # Turn if direction changes
                    if (prev_dx != 0 and next_dy != 0) or (prev_dy != 0 and next_dx != 0):
                        turns += 1
            
            results[strategy] = {
                'success': True,
                'time': routing_time,
                'distance': total_distance,
                'waypoints': len(path),
                'turns': turns,
                'path': path
            }
            
            print(f"   ✅ Success: {routing_time*1000:.1f}ms")
            print(f"   📏 Distance: {total_distance:.1f}mm")
            print(f"   📍 Waypoints: {len(path)}")
            print(f"   🔄 Turns: {turns}")
            
        else:
            results[strategy] = {'success': False, 'time': routing_time}
            print(f"   ❌ Failed in {routing_time*1000:.1f}ms")
    
    # Summary comparison
    print(f"\n📊 Strategy Comparison Summary:")
    print(f"   {'Strategy':<12} {'Success':<8} {'Time(ms)':<10} {'Distance':<10} {'Turns':<6}")
    print(f"   {'-' * 55}")
    
    for strategy in strategies:
        result = results[strategy]
        if result['success']:
            print(f"   {strategy.value:<12} {'✅':<8} {result['time']*1000:<10.1f} "
                  f"{result['distance']:<10.1f} {result['turns']:<6}")
        else:
            print(f"   {strategy.value:<12} {'❌':<8} {result['time']*1000:<10.1f} {'N/A':<10} {'N/A':<6}")
    
    # Add best route to schematic
    best_strategy = None
    best_score = float('inf')
    
    for strategy, result in results.items():
        if result['success']:
            # Score combines distance and turns (prefer fewer turns for aesthetics)
            score = result['distance'] + result['turns'] * 5.0  # Weight turns heavily
            if score < best_score:
                best_score = score
                best_strategy = strategy
    
    if best_strategy:
        print(f"\n🏆 Best strategy: {best_strategy.value} (score: {best_score:.1f})")
        best_path = results[best_strategy]['path']
        for i in range(len(best_path) - 1):
            sch.add_wire(best_path[i], best_path[i + 1])
    
    filename = "test_manhattan_strategies.kicad_sch"
    sch.save(filename)
    print(f"\n💾 Saved: {filename}")


def test_grid_and_bounds():
    """Test grid system and bounding box integration."""
    print("\n\n🔧 Test 4: Grid System & Bounding Box Integration")
    print("=" * 50)
    
    # Test grid point conversions
    print("📐 Grid system tests:")
    
    test_points = [
        Point(0, 0),
        Point(1.27, 2.54),
        Point(12.7, 25.4),
        Point(1.5, 3.7)  # Non-grid-aligned
    ]
    
    for point in test_points:
        grid_point = GridPoint.from_world_point(point)
        world_point = grid_point.to_world_point()
        snapped_point = snap_to_kicad_grid(point)
        
        print(f"   World: {point} → Grid: ({grid_point.x}, {grid_point.y}) → "
              f"Back: {world_point} (Snapped: {snapped_point})")
    
    # Test bounding box accuracy
    print(f"\n📦 Bounding box accuracy test:")
    sch = ksa.create_schematic("Grid Test")
    
    test_component = sch.components.add("Device:R", "R1", "1k", Point(25.4, 25.4))
    bbox = get_component_bounding_box(test_component, include_properties=False)
    
    print(f"   Component at: {test_component.position}")
    print(f"   Bounding box: {bbox}")
    print(f"   Size: {bbox.width:.2f} x {bbox.height:.2f} mm")
    
    # Test pin positions vs bounding box
    pin1_pos = sch.get_component_pin_position("R1", "1")
    pin2_pos = sch.get_component_pin_position("R1", "2")
    
    pin1_inside = bbox.contains_point(pin1_pos)
    pin2_inside = bbox.contains_point(pin2_pos)
    
    print(f"   Pin 1 at {pin1_pos}: {'inside' if pin1_inside else 'outside'} bbox")
    print(f"   Pin 2 at {pin2_pos}: {'inside' if pin2_inside else 'outside'} bbox")
    
    # Test grid obstacle marking
    print(f"\n🚧 Obstacle grid marking test:")
    router = ManhattanRouter()
    
    obstacles = [bbox]
    start = Point(0, 25.4)
    end = Point(50.8, 25.4)
    
    routing_grid = router._build_routing_grid(obstacles, 1.27, start, end)
    
    print(f"   Grid size: {routing_grid.grid_size}mm")
    print(f"   Obstacles marked: {len(routing_grid.obstacles)} grid points")
    print(f"   Clearance map: {len(routing_grid.clearance_map)} points with costs")
    
    # Test a simple path
    path = router.route_between_points(start, end, obstacles, RoutingStrategy.AESTHETIC)
    if path:
        print(f"   ✅ Test route found: {len(path)} waypoints")
    else:
        print(f"   ❌ Test route failed")


def run_all_tests():
    """Run comprehensive Manhattan routing test suite."""
    print("🧪 Manhattan Routing Test Suite")
    print("🧪 " + "=" * 50)
    print("   Testing grid-based pathfinding with obstacle avoidance")
    print("   Validating different routing strategies and performance")
    print("")
    
    start_time = time.time()
    
    # Run all tests
    test_basic_manhattan_routing()
    test_complex_obstacle_field() 
    test_routing_strategies_comparison()
    test_grid_and_bounds()
    
    total_time = time.time() - start_time
    
    print(f"\n\n🎉 Manhattan Routing Test Suite Complete")
    print(f"🎉 " + "=" * 50)
    print(f"   Total execution time: {total_time:.2f} seconds")
    print(f"   Generated test files:")
    print(f"   • test_manhattan_basic.kicad_sch - Basic routing scenarios") 
    print(f"   • test_manhattan_complex.kicad_sch - Complex obstacle field")
    print(f"   • test_manhattan_strategies.kicad_sch - Strategy comparison")
    print(f"")
    print(f"💡 Open these files in KiCAD to visually verify the routing results!")
    print(f"   The routed wires should cleanly avoid component obstacles")
    print(f"   and maintain perfect grid alignment for electrical connectivity.")


if __name__ == "__main__":
    run_all_tests()