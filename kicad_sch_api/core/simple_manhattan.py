"""
Simple Manhattan routing with basic obstacle avoidance.

This module provides a simple, working implementation of Manhattan routing
that can be integrated with the existing auto_route_pins API.
"""

import logging
from typing import List, Optional, Tuple
from .types import Point, SchematicSymbol
from .component_bounds import get_component_bounding_box, BoundingBox

logger = logging.getLogger(__name__)


def simple_manhattan_route(start: Point, end: Point) -> List[Point]:
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
        # Pure vertical or same point
        return [start, end]


def check_horizontal_line_collision(start: Point, end: Point, bbox: BoundingBox) -> bool:
    """Check if a horizontal line collides with a bounding box."""
    line_y = start.y
    line_min_x = min(start.x, end.x)
    line_max_x = max(start.x, end.x)
    
    # Check Y range collision
    if not (bbox.min_y <= line_y <= bbox.max_y):
        return False
    
    # Check X range collision  
    if line_max_x < bbox.min_x or line_min_x > bbox.max_x:
        return False
        
    return True


def simple_obstacle_avoidance_route(
    start: Point, 
    end: Point, 
    obstacles: List[BoundingBox],
    clearance: float = 2.54
) -> List[Point]:
    """
    Route around obstacles with simple above/below strategy.
    
    Args:
        start: Starting point
        end: Ending point  
        obstacles: List of obstacle bounding boxes
        clearance: Clearance distance from obstacles
        
    Returns:
        List of waypoints avoiding obstacles
    """
    # Try direct L-shaped route first
    direct_route = simple_manhattan_route(start, end)
    
    # Check if any segment collides with obstacles
    collision_detected = False
    for i in range(len(direct_route) - 1):
        seg_start = direct_route[i]
        seg_end = direct_route[i + 1]
        
        for obstacle in obstacles:
            if check_horizontal_line_collision(seg_start, seg_end, obstacle):
                collision_detected = True
                logger.debug(f"Collision detected between {seg_start} -> {seg_end} and obstacle {obstacle}")
                break
        if collision_detected:
            break
    
    if not collision_detected:
        logger.debug("Direct route is clear")
        return direct_route
    
    # Find obstacles that block the path
    blocking_obstacles = []
    for obstacle in obstacles:
        # Check if obstacle is roughly between start and end points
        if (min(start.x, end.x) < obstacle.max_x and 
            max(start.x, end.x) > obstacle.min_x):
            blocking_obstacles.append(obstacle)
    
    if not blocking_obstacles:
        logger.debug("No blocking obstacles found, using direct route")
        return direct_route
    
    # Find the combined bounding area of all blocking obstacles
    combined_min_y = min(obs.min_y for obs in blocking_obstacles)
    combined_max_y = max(obs.max_y for obs in blocking_obstacles)
    
    # Calculate routing options
    above_y = combined_max_y + clearance
    below_y = combined_min_y - clearance
    
    # Route above obstacles
    route_above = [
        start,
        Point(start.x, above_y),      # Go up
        Point(end.x, above_y),        # Go across above obstacles  
        end                           # Go down to destination
    ]
    
    # Route below obstacles
    route_below = [
        start,
        Point(start.x, below_y),      # Go down
        Point(end.x, below_y),        # Go across below obstacles
        end                           # Go up to destination
    ]
    
    # Calculate Manhattan distances
    def manhattan_distance(route):
        total = 0
        for i in range(len(route) - 1):
            total += abs(route[i+1].x - route[i].x) + abs(route[i+1].y - route[i].y)
        return total
    
    above_distance = manhattan_distance(route_above)
    below_distance = manhattan_distance(route_below)
    
    # Choose shorter route
    if above_distance <= below_distance:
        chosen_route = route_above
        choice = "above"
    else:
        chosen_route = route_below
        choice = "below"
    
    logger.debug(f"Obstacle avoidance: routing {choice} obstacles (distance: {min(above_distance, below_distance):.1f}mm)")
    return chosen_route


def auto_route_with_manhattan(
    schematic,
    start_component: SchematicSymbol,
    start_pin: str,
    end_component: SchematicSymbol, 
    end_pin: str,
    avoid_components: Optional[List[SchematicSymbol]] = None,
    clearance: float = 2.54
) -> Optional[str]:
    """
    Auto route between pins using Manhattan routing with obstacle avoidance.
    
    Args:
        schematic: The schematic object
        start_component: Starting component
        start_pin: Starting pin number
        end_component: Ending component  
        end_pin: Ending pin number
        avoid_components: Components to avoid (if None, avoid all components)
        clearance: Clearance distance from obstacles
        
    Returns:
        Wire UUID if successful, None if failed
    """
    # Get pin positions
    from .pin_utils import get_component_pin_position
    
    start_pos = get_component_pin_position(start_component, start_pin)
    end_pos = get_component_pin_position(end_component, end_pin)
    
    if not start_pos or not end_pos:
        logger.warning("Could not determine pin positions")
        return None
    
    logger.debug(f"Manhattan routing: {start_component.reference} pin {start_pin} -> {end_component.reference} pin {end_pin}")
    logger.debug(f"  From: {start_pos}")
    logger.debug(f"  To: {end_pos}")
    
    # Get obstacle bounding boxes
    obstacles = []
    if avoid_components is None:
        # Avoid all components in schematic except start and end
        avoid_components = [comp for comp in schematic.components 
                          if comp.reference != start_component.reference 
                          and comp.reference != end_component.reference]
    
    for component in avoid_components:
        bbox = get_component_bounding_box(component, include_properties=False)
        obstacles.append(bbox)
        logger.debug(f"  Obstacle: {component.reference} at {bbox}")
    
    # Calculate route
    route = simple_obstacle_avoidance_route(start_pos, end_pos, obstacles, clearance)
    
    logger.debug(f"  Route: {len(route)} waypoints")
    for i, point in enumerate(route):
        logger.debug(f"    {i}: {point}")
    
    # Add wires to schematic
    wire_uuids = []
    for i in range(len(route) - 1):
        wire_uuid = schematic.add_wire(route[i], route[i + 1])
        wire_uuids.append(wire_uuid)
    
    logger.debug(f"Added {len(wire_uuids)} wire segments")
    
    # Return first wire UUID (for compatibility)
    return wire_uuids[0] if wire_uuids else None