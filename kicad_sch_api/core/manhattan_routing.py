"""
Manhattan routing with obstacle avoidance for KiCAD schematics.

This module implements grid-based pathfinding algorithms for routing wires
around component obstacles while maintaining Manhattan (orthogonal) constraints
and perfect KiCAD grid alignment.

Based on research into EDA routing algorithms and adapted for schematic capture.
"""

import heapq
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .component_bounds import BoundingBox, check_path_collision, get_component_bounding_box
from .types import Point, SchematicSymbol
from .wire_routing import snap_to_kicad_grid

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Routing strategy options for different optimization goals."""

    SHORTEST = "shortest"  # Minimize Manhattan distance
    CLEARANCE = "clearance"  # Maximize obstacle clearance
    AESTHETIC = "aesthetic"  # Balance distance, turns, and clearance
    DIRECT = "direct"  # Fallback to direct routing


@dataclass
class GridPoint:
    """A point on the routing grid."""

    x: int
    y: int

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other) -> bool:
        return isinstance(other, GridPoint) and self.x == other.x and self.y == other.y

    def to_world_point(self, grid_size: float = 1.27) -> Point:
        """Convert grid coordinates to world coordinates."""
        return Point(self.x * grid_size, self.y * grid_size)

    @classmethod
    def from_world_point(cls, point: Point, grid_size: float = 1.27) -> "GridPoint":
        """Convert world coordinates to grid coordinates."""
        return cls(x=round(point.x / grid_size), y=round(point.y / grid_size))

    def manhattan_distance(self, other: "GridPoint") -> int:
        """Calculate Manhattan distance to another grid point."""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class PathNode:
    """Node for A* pathfinding algorithm."""

    position: GridPoint
    g_cost: float  # Cost from start
    h_cost: float  # Heuristic cost to goal
    parent: Optional["PathNode"] = None

    @property
    def f_cost(self) -> float:
        """Total cost for A* (g + h)."""
        return self.g_cost + self.h_cost

    def __lt__(self, other: "PathNode") -> bool:
        """For priority queue ordering."""
        return self.f_cost < other.f_cost


@dataclass
class RoutingGrid:
    """Grid representation for Manhattan routing."""

    grid_size: float = 1.27  # KiCAD standard grid in mm
    obstacles: Set[GridPoint] = field(default_factory=set)
    boundaries: Optional[BoundingBox] = None
    clearance_map: Dict[GridPoint, float] = field(default_factory=dict)

    def is_valid_point(self, point: GridPoint) -> bool:
        """Check if a grid point is valid for routing."""
        # Check if point is an obstacle
        if point in self.obstacles:
            return False

        # Check boundaries if defined
        if self.boundaries:
            world_point = point.to_world_point(self.grid_size)
            if not self.boundaries.contains_point(world_point):
                return False

        return True

    def get_neighbors(self, point: GridPoint) -> List[GridPoint]:
        """Get valid neighboring points (4-connected Manhattan)."""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Up, Right, Down, Left
            neighbor = GridPoint(point.x + dx, point.y + dy)
            if self.is_valid_point(neighbor):
                neighbors.append(neighbor)
        return neighbors

    def get_clearance_cost(self, point: GridPoint) -> float:
        """Get clearance-based cost for routing strategies."""
        return self.clearance_map.get(point, 0.0)


class ManhattanRouter:
    """Manhattan routing engine with obstacle avoidance."""

    def __init__(self, grid_size: float = 1.27, default_clearance: float = 1.27):
        """
        Initialize Manhattan router.

        Args:
            grid_size: Grid spacing in mm (KiCAD standard: 1.27mm)
            default_clearance: Default clearance from obstacles in mm
        """
        self.grid_size = grid_size
        self.default_clearance = default_clearance

    def route_between_points(
        self,
        start: Point,
        end: Point,
        obstacles: List[BoundingBox],
        strategy: RoutingStrategy = RoutingStrategy.AESTHETIC,
        clearance: Optional[float] = None,
    ) -> Optional[List[Point]]:
        """
        Route between two points avoiding obstacles.

        Args:
            start: Starting point in world coordinates
            end: Ending point in world coordinates
            obstacles: List of obstacle bounding boxes
            strategy: Routing strategy to use
            clearance: Obstacle clearance (uses default if None)

        Returns:
            List of waypoints for the route, or None if no route found
        """
        if clearance is None:
            clearance = self.default_clearance

        logger.debug(f"Routing from {start} to {end} with strategy {strategy.value}")

        # Check if direct path is clear
        if not check_path_collision(start, end, obstacles, clearance):
            logger.debug("Direct path is clear, using direct routing")
            return [start, end]

        # Grid-snap the start and end points
        start_snapped = snap_to_kicad_grid(start, self.grid_size)
        end_snapped = snap_to_kicad_grid(end, self.grid_size)

        # Build routing grid
        routing_grid = self._build_routing_grid(obstacles, clearance, start_snapped, end_snapped)

        # Convert to grid coordinates
        start_grid = GridPoint.from_world_point(start_snapped, self.grid_size)
        end_grid = GridPoint.from_world_point(end_snapped, self.grid_size)

        # Find path using A*
        path_grid = self._find_path_astar(start_grid, end_grid, routing_grid, strategy)

        if not path_grid:
            logger.warning(f"No path found from {start} to {end}")
            return None

        # Convert back to world coordinates
        path_world = [point.to_world_point(self.grid_size) for point in path_grid]

        # Optimize path
        optimized_path = self._optimize_path(path_world)

        logger.debug(f"Found path with {len(optimized_path)} waypoints")
        return optimized_path

    def _build_routing_grid(
        self, obstacles: List[BoundingBox], clearance: float, start: Point, end: Point
    ) -> RoutingGrid:
        """Build routing grid with obstacles and clearance information."""
        # Calculate grid bounds that encompass all obstacles plus start/end
        min_x = min(start.x, end.x)
        max_x = max(start.x, end.x)
        min_y = min(start.y, end.y)
        max_y = max(start.y, end.y)

        for obstacle in obstacles:
            min_x = min(min_x, obstacle.min_x - clearance)
            max_x = max(max_x, obstacle.max_x + clearance)
            min_y = min(min_y, obstacle.min_y - clearance)
            max_y = max(max_y, obstacle.max_y + clearance)

        # Add margin for routing
        margin = clearance * 2
        grid_bounds = BoundingBox(min_x - margin, min_y - margin, max_x + margin, max_y + margin)

        # Create grid and mark obstacles
        grid = RoutingGrid(self.grid_size, boundaries=grid_bounds)

        for obstacle in obstacles:
            self._mark_obstacle_on_grid(grid, obstacle, clearance)

        return grid

    def _mark_obstacle_on_grid(self, grid: RoutingGrid, obstacle: BoundingBox, clearance: float):
        """Mark obstacle area on routing grid."""
        # Expand obstacle by clearance
        expanded_obstacle = obstacle.expand(clearance)

        # Convert to grid coordinates
        min_grid_x = int((expanded_obstacle.min_x) // self.grid_size) - 1
        max_grid_x = int((expanded_obstacle.max_x) // self.grid_size) + 1
        min_grid_y = int((expanded_obstacle.min_y) // self.grid_size) - 1
        max_grid_y = int((expanded_obstacle.max_y) // self.grid_size) + 1

        # Mark obstacle points
        for gx in range(min_grid_x, max_grid_x + 1):
            for gy in range(min_grid_y, max_grid_y + 1):
                grid_point = GridPoint(gx, gy)
                world_point = grid_point.to_world_point(self.grid_size)

                if expanded_obstacle.contains_point(world_point):
                    grid.obstacles.add(grid_point)
                else:
                    # Calculate clearance cost for points near obstacles
                    distance_to_obstacle = self._distance_to_bbox(world_point, obstacle)
                    if distance_to_obstacle < clearance * 2:
                        # Inverse cost - closer to obstacle = higher cost
                        cost = max(0, clearance * 2 - distance_to_obstacle)
                        grid.clearance_map[grid_point] = cost

    def _distance_to_bbox(self, point: Point, bbox: BoundingBox) -> float:
        """Calculate minimum distance from point to bounding box."""
        dx = max(bbox.min_x - point.x, 0, point.x - bbox.max_x)
        dy = max(bbox.min_y - point.y, 0, point.y - bbox.max_y)
        return (dx * dx + dy * dy) ** 0.5

    def _find_path_astar(
        self, start: GridPoint, goal: GridPoint, grid: RoutingGrid, strategy: RoutingStrategy
    ) -> Optional[List[GridPoint]]:
        """Find path using A* algorithm with strategy-specific costs."""
        if start == goal:
            return [start]

        # Priority queue for open set
        open_set = []
        open_dict: Dict[GridPoint, PathNode] = {}
        closed_set: Set[GridPoint] = set()

        # Initialize start node
        start_node = PathNode(
            position=start, g_cost=0, h_cost=self._heuristic_cost(start, goal, strategy)
        )

        heapq.heappush(open_set, start_node)
        open_dict[start] = start_node

        while open_set:
            # Get node with lowest f_cost
            current = heapq.heappop(open_set)
            del open_dict[current.position]
            closed_set.add(current.position)

            # Check if we reached the goal
            if current.position == goal:
                return self._reconstruct_path(current)

            # Check neighbors
            for neighbor_pos in grid.get_neighbors(current.position):
                if neighbor_pos in closed_set:
                    continue

                # Calculate costs
                move_cost = self._movement_cost(current.position, neighbor_pos, grid, strategy)
                tentative_g = current.g_cost + move_cost

                # Check if this path to neighbor is better
                if neighbor_pos in open_dict:
                    neighbor_node = open_dict[neighbor_pos]
                    if tentative_g < neighbor_node.g_cost:
                        neighbor_node.g_cost = tentative_g
                        neighbor_node.parent = current
                else:
                    # Add new node to open set
                    neighbor_node = PathNode(
                        position=neighbor_pos,
                        g_cost=tentative_g,
                        h_cost=self._heuristic_cost(neighbor_pos, goal, strategy),
                        parent=current,
                    )
                    heapq.heappush(open_set, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node

        # No path found
        return None

    def _heuristic_cost(
        self, point: GridPoint, goal: GridPoint, strategy: RoutingStrategy
    ) -> float:
        """Calculate heuristic cost based on strategy."""
        manhattan_dist = point.manhattan_distance(goal)

        if strategy == RoutingStrategy.SHORTEST:
            return float(manhattan_dist)
        elif strategy == RoutingStrategy.CLEARANCE:
            return float(manhattan_dist) * 0.5  # Lower weight on distance
        elif strategy == RoutingStrategy.AESTHETIC:
            return float(manhattan_dist) * 0.8  # Balanced weight
        else:  # DIRECT fallback
            return float(manhattan_dist)

    def _movement_cost(
        self,
        from_point: GridPoint,
        to_point: GridPoint,
        grid: RoutingGrid,
        strategy: RoutingStrategy,
    ) -> float:
        """Calculate cost of moving between two adjacent grid points."""
        base_cost = 1.0  # Base movement cost

        if strategy == RoutingStrategy.SHORTEST:
            return base_cost

        elif strategy == RoutingStrategy.CLEARANCE:
            # Higher cost for points near obstacles
            clearance_cost = grid.get_clearance_cost(to_point)
            return base_cost + clearance_cost * 2.0

        elif strategy == RoutingStrategy.AESTHETIC:
            # Balance clearance with reasonable cost
            clearance_cost = grid.get_clearance_cost(to_point)
            return base_cost + clearance_cost * 0.5

        else:  # DIRECT fallback
            return base_cost

    def _reconstruct_path(self, goal_node: PathNode) -> List[GridPoint]:
        """Reconstruct path from goal node back to start."""
        path = []
        current = goal_node

        while current:
            path.append(current.position)
            current = current.parent

        path.reverse()
        return path

    def _optimize_path(self, path: List[Point]) -> List[Point]:
        """Optimize path by removing unnecessary waypoints."""
        if len(path) < 3:
            return path

        optimized = [path[0]]  # Always keep start point

        for i in range(1, len(path) - 1):
            prev_point = optimized[-1]
            current_point = path[i]
            next_point = path[i + 1]

            # Check if we can skip current point (collinear points)
            if not self._are_collinear(prev_point, current_point, next_point):
                optimized.append(current_point)

        optimized.append(path[-1])  # Always keep end point
        return optimized

    def _are_collinear(self, p1: Point, p2: Point, p3: Point, tolerance: float = 0.01) -> bool:
        """Check if three points are collinear (on the same line)."""
        # For Manhattan routing, points are collinear if they form a straight horizontal or vertical line
        horizontal = abs(p1.y - p2.y) < tolerance and abs(p2.y - p3.y) < tolerance
        vertical = abs(p1.x - p2.x) < tolerance and abs(p2.x - p3.x) < tolerance
        return horizontal or vertical


def route_around_obstacles(
    start: Point,
    end: Point,
    components: List[SchematicSymbol],
    strategy: RoutingStrategy = RoutingStrategy.AESTHETIC,
    clearance: float = 1.27,
    grid_size: float = 1.27,
) -> Optional[List[Point]]:
    """
    High-level function to route between two points avoiding component obstacles.

    Args:
        start: Starting point in world coordinates
        end: Ending point in world coordinates
        components: List of components to avoid
        strategy: Routing strategy to use
        clearance: Minimum clearance from components
        grid_size: Grid spacing for routing

    Returns:
        List of waypoints for the route, or None if no route found
    """
    logger.debug(f"🛣️  Manhattan routing: {start} → {end}, strategy={strategy.value}")

    # Get component bounding boxes
    obstacles = []
    for component in components:
        bbox = get_component_bounding_box(component, include_properties=False)
        obstacles.append(bbox)
        logger.debug(f"   Obstacle: {component.reference} at {bbox}")

    # Create router and find path
    router = ManhattanRouter(grid_size, clearance)
    path = router.route_between_points(start, end, obstacles, strategy, clearance)

    if path:
        logger.debug(f"   ✅ Route found with {len(path)} waypoints")
        for i, point in enumerate(path):
            logger.debug(f"      {i}: {point}")
    else:
        logger.warning(f"   ❌ No route found")

    return path
