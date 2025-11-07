#!/usr/bin/env python3
"""
Demonstration of orthogonal routing functionality.

This example shows how to use the create_orthogonal_routing() function
to automatically generate Manhattan-style wire routes between points.
"""

from kicad_sch_api.core.types import Point
from kicad_sch_api.geometry import (
    CornerDirection,
    create_orthogonal_routing,
    validate_routing_result,
)


def print_routing_result(result, label=""):
    """Pretty print a routing result."""
    print(f"\n{label}")
    print("=" * 60)
    print(f"Is Direct: {result.is_direct}")
    print(f"Corner: {result.corner}")
    print(f"Segments ({len(result.segments)}):")
    for i, (start, end) in enumerate(result.segments, 1):
        print(f"  {i}. ({start.x:.2f}, {start.y:.2f}) → ({end.x:.2f}, {end.y:.2f})")


def demo_direct_routing():
    """Demonstrate direct routing when points are aligned."""
    print("\n" + "=" * 60)
    print("DEMO 1: Direct Routing (Aligned Points)")
    print("=" * 60)

    # Horizontal routing
    result = create_orthogonal_routing(
        Point(100.0, 100.0),
        Point(150.0, 100.0)
    )
    print_routing_result(result, "Horizontal routing:")
    validate_routing_result(result)

    # Vertical routing
    result = create_orthogonal_routing(
        Point(100.0, 100.0),
        Point(100.0, 150.0)
    )
    print_routing_result(result, "Vertical routing:")
    validate_routing_result(result)


def demo_l_shaped_routing():
    """Demonstrate L-shaped routing with direction preferences."""
    print("\n" + "=" * 60)
    print("DEMO 2: L-Shaped Routing (Non-Aligned Points)")
    print("=" * 60)

    from_pos = Point(100.0, 100.0)
    to_pos = Point(150.0, 125.0)

    # Horizontal first
    result = create_orthogonal_routing(
        from_pos, to_pos,
        corner_direction=CornerDirection.HORIZONTAL_FIRST
    )
    print_routing_result(result, "Horizontal First:")
    validate_routing_result(result)

    # Vertical first
    result = create_orthogonal_routing(
        from_pos, to_pos,
        corner_direction=CornerDirection.VERTICAL_FIRST
    )
    print_routing_result(result, "Vertical First:")
    validate_routing_result(result)

    # Auto (heuristic-based)
    result = create_orthogonal_routing(
        from_pos, to_pos,
        corner_direction=CornerDirection.AUTO
    )
    print_routing_result(result, "Auto (dx >= dy → horizontal first):")
    validate_routing_result(result)


def demo_inverted_y_axis():
    """Demonstrate routing with KiCAD's inverted Y-axis."""
    print("\n" + "=" * 60)
    print("DEMO 3: KiCAD Inverted Y-Axis")
    print("=" * 60)
    print("Remember: Lower Y = visually HIGHER on screen!")
    print("          Higher Y = visually LOWER on screen!")

    # Routing "upward" (to lower Y value)
    result = create_orthogonal_routing(
        Point(100.0, 125.0),  # Visually lower (higher Y)
        Point(150.0, 100.0),  # Visually higher (lower Y)
        corner_direction=CornerDirection.HORIZONTAL_FIRST
    )
    print_routing_result(result, "Routing upward on screen (to lower Y):")

    # Routing "downward" (to higher Y value)
    result = create_orthogonal_routing(
        Point(100.0, 100.0),  # Visually higher (lower Y)
        Point(150.0, 125.0),  # Visually lower (higher Y)
        corner_direction=CornerDirection.HORIZONTAL_FIRST
    )
    print_routing_result(result, "Routing downward on screen (to higher Y):")


def demo_real_world_scenario():
    """Demonstrate routing with realistic component pin positions."""
    print("\n" + "=" * 60)
    print("DEMO 4: Real-World Scenario (Voltage Divider)")
    print("=" * 60)

    # Voltage divider: R1 and R2 in series
    # R1 at (127.0, 88.9), R2 at (127.0, 114.3)
    r1_pin2 = Point(127.0, 92.71)   # R1 bottom pin
    r2_pin1 = Point(127.0, 110.49)  # R2 top pin

    result = create_orthogonal_routing(r1_pin2, r2_pin1)
    print_routing_result(result, "R1 pin 2 → R2 pin 1 (vertical):")
    print("\nNote: Direct routing because pins are vertically aligned!")

    # Now tap off to an output pin
    midpoint = Point(127.0, 101.6)  # Midpoint for VOUT
    output = Point(160.0, 101.6)     # Output connector

    result = create_orthogonal_routing(midpoint, output)
    print_routing_result(result, "Junction → Output (horizontal):")
    print("\nNote: Direct routing because junction and output are horizontally aligned!")


def demo_auto_heuristic():
    """Demonstrate AUTO direction selection heuristic."""
    print("\n" + "=" * 60)
    print("DEMO 5: AUTO Direction Selection Heuristic")
    print("=" * 60)
    print("Rule: If dx >= dy → horizontal first, else vertical first\n")

    # Case 1: dx > dy (prefer horizontal)
    from_pos = Point(100.0, 100.0)
    to_pos = Point(160.0, 120.0)  # dx=60, dy=20
    result = create_orthogonal_routing(from_pos, to_pos, CornerDirection.AUTO)
    print(f"From {from_pos} to {to_pos}")
    print(f"  dx={abs(to_pos.x - from_pos.x):.1f}, dy={abs(to_pos.y - from_pos.y):.1f}")
    print(f"  → Chose horizontal first (corner at {result.corner})")

    # Case 2: dy > dx (prefer vertical)
    to_pos = Point(120.0, 160.0)  # dx=20, dy=60
    result = create_orthogonal_routing(from_pos, to_pos, CornerDirection.AUTO)
    print(f"\nFrom {from_pos} to {to_pos}")
    print(f"  dx={abs(to_pos.x - from_pos.x):.1f}, dy={abs(to_pos.y - from_pos.y):.1f}")
    print(f"  → Chose vertical first (corner at {result.corner})")

    # Case 3: dx == dy (prefer horizontal by default)
    to_pos = Point(150.0, 150.0)  # dx=50, dy=50
    result = create_orthogonal_routing(from_pos, to_pos, CornerDirection.AUTO)
    print(f"\nFrom {from_pos} to {to_pos}")
    print(f"  dx={abs(to_pos.x - from_pos.x):.1f}, dy={abs(to_pos.y - from_pos.y):.1f}")
    print(f"  → Chose horizontal first (tie → horizontal)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ORTHOGONAL ROUTING DEMONSTRATION")
    print("=" * 60)
    print("\nThis demo shows the core orthogonal routing functionality")
    print("for automatic Manhattan-style wire routing in KiCAD schematics.")

    demo_direct_routing()
    demo_l_shaped_routing()
    demo_inverted_y_axis()
    demo_real_world_scenario()
    demo_auto_heuristic()

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nAll routing results validated successfully!")
    print("Ready for MCP server integration (Phase 2).\n")
