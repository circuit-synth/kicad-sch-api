#!/usr/bin/env python3
"""
Create a demonstration schematic showing orthogonal routing capabilities.

This script creates a complete schematic with multiple components and
routes them using the new orthogonal routing algorithm.
"""

import kicad_sch_api as ksa
from kicad_sch_api.geometry import create_orthogonal_routing, CornerDirection
from kicad_sch_api.core.types import Point

print("Creating demonstration schematic with orthogonal routing...")

# Create schematic
sch = ksa.create_schematic("Orthogonal Routing Demo")

# ============================================================================
# Section 1: Voltage Divider (Direct Vertical Routing)
# ============================================================================
print("\n1. Creating voltage divider with direct routing...")

r1 = sch.components.add("Device:R", "R1", "10k", position=(50.8, 50.8))
r2 = sch.components.add("Device:R", "R2", "10k", position=(50.8, 76.2))

# Get pin positions
r1_pins = sch.components.get_pins_info("R1")
r2_pins = sch.components.get_pins_info("R2")
r1_pin2 = next(p for p in r1_pins if p.number == "2")
r2_pin1 = next(p for p in r2_pins if p.number == "1")

# Route R1 to R2 (direct vertical)
result1 = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)
print(f"   Voltage divider: {len(result1.segments)} segment(s), direct={result1.is_direct}")
for start, end in result1.segments:
    sch.wires.add(start=start, end=end)

# Add labels
r1_pin1 = next(p for p in r1_pins if p.number == "1")
sch.add_label("VCC", position=(r1_pin1.position.x, r1_pin1.position.y - 5.0))

r2_pin2 = next(p for p in r2_pins if p.number == "2")
sch.add_label("GND", position=(r2_pin2.position.x, r2_pin2.position.y + 5.0))

# Add VOUT label at midpoint
midpoint_y = (r1_pin2.position.y + r2_pin1.position.y) / 2
sch.add_label("VOUT", position=(r1_pin2.position.x + 7.0, midpoint_y))

# ============================================================================
# Section 2: L-Shaped Routing (Horizontal First)
# ============================================================================
print("\n2. Creating L-shaped routing (horizontal first)...")

r3 = sch.components.add("Device:R", "R3", "1k", position=(101.6, 50.8))
r4 = sch.components.add("Device:R", "R4", "1k", position=(127.0, 76.2))

r3_pins = sch.components.get_pins_info("R3")
r4_pins = sch.components.get_pins_info("R4")
r3_pin2 = next(p for p in r3_pins if p.number == "2")
r4_pin1 = next(p for p in r4_pins if p.number == "1")

# Route with horizontal first
result2 = create_orthogonal_routing(
    r3_pin2.position,
    r4_pin1.position,
    corner_direction=CornerDirection.HORIZONTAL_FIRST
)
print(f"   L-shaped H-first: {len(result2.segments)} segments, corner at {result2.corner}")
for start, end in result2.segments:
    sch.wires.add(start=start, end=end)

# Add label at corner
if result2.corner:
    sch.add_label("NET1", position=(result2.corner.x + 2.0, result2.corner.y - 2.0))

# ============================================================================
# Section 3: L-Shaped Routing (Vertical First)
# ============================================================================
print("\n3. Creating L-shaped routing (vertical first)...")

r5 = sch.components.add("Device:R", "R5", "2.2k", position=(152.4, 50.8))
r6 = sch.components.add("Device:R", "R6", "2.2k", position=(177.8, 76.2))

r5_pins = sch.components.get_pins_info("R5")
r6_pins = sch.components.get_pins_info("R6")
r5_pin2 = next(p for p in r5_pins if p.number == "2")
r6_pin1 = next(p for p in r6_pins if p.number == "1")

# Route with vertical first
result3 = create_orthogonal_routing(
    r5_pin2.position,
    r6_pin1.position,
    corner_direction=CornerDirection.VERTICAL_FIRST
)
print(f"   L-shaped V-first: {len(result3.segments)} segments, corner at {result3.corner}")
for start, end in result3.segments:
    sch.wires.add(start=start, end=end)

# Add label at corner
if result3.corner:
    sch.add_label("NET2", position=(result3.corner.x - 7.0, result3.corner.y + 2.0))

# ============================================================================
# Section 4: Complex Chain with AUTO Routing
# ============================================================================
print("\n4. Creating chain of components with AUTO routing...")

chain_components = []
for i in range(5):
    x = 50.8 + i * 25.4
    y = 101.6 + (i % 2) * 12.7  # Zigzag pattern
    r = sch.components.add(
        "Device:R",
        f"R{7+i}",
        "100",
        position=(x, y)
    )
    chain_components.append(r)

# Route chain with AUTO direction
for i in range(len(chain_components) - 1):
    r_from = chain_components[i]
    r_to = chain_components[i + 1]

    pins_from = sch.components.get_pins_info(r_from.reference)
    pins_to = sch.components.get_pins_info(r_to.reference)

    pin2 = next(p for p in pins_from if p.number == "2")
    pin1 = next(p for p in pins_to if p.number == "1")

    result = create_orthogonal_routing(
        pin2.position,
        pin1.position,
        corner_direction=CornerDirection.AUTO
    )

    for start, end in result.segments:
        sch.wires.add(start=start, end=end)

    print(f"   Chain R{7+i}→R{8+i}: {len(result.segments)} segments")

# ============================================================================
# Section 5: Power Distribution (Horizontal Routing)
# ============================================================================
print("\n5. Creating power distribution with horizontal routing...")

# VCC rail
vcc_rail_start = Point(50.8, 25.4)
vcc_rail_end = Point(177.8, 25.4)
sch.wires.add(start=vcc_rail_start, end=vcc_rail_end)
sch.add_label("VCC_RAIL", position=(114.3, 22.9))

# Connect components to VCC rail
vcc_taps = [
    (r1, Point(50.8, 25.4)),
    (r3, Point(101.6, 25.4)),
    (r5, Point(152.4, 25.4)),
]

for component, rail_point in vcc_taps:
    pins = sch.components.get_pins_info(component.reference)
    pin1 = next(p for p in pins if p.number == "1")

    result = create_orthogonal_routing(
        rail_point,
        pin1.position,
        corner_direction=CornerDirection.VERTICAL_FIRST
    )

    for start, end in result.segments:
        sch.wires.add(start=start, end=end)

    print(f"   {component.reference} to VCC rail: {len(result.segments)} segments")

# ============================================================================
# Section 6: Text Annotations
# ============================================================================
sch.add_text(
    "Orthogonal Routing Demonstration",
    position=(50.8, 12.7),
    effects={'size': (2.54, 2.54), 'bold': True}
)

sch.add_text(
    "1. Direct Vertical",
    position=(45.0, 90.0),
    effects={'size': (1.27, 1.27)}
)

sch.add_text(
    "2. Horizontal First",
    position=(95.0, 90.0),
    effects={'size': (1.27, 1.27)}
)

sch.add_text(
    "3. Vertical First",
    position=(147.0, 90.0),
    effects={'size': (1.27, 1.27)}
)

sch.add_text(
    "4. Auto Routing Chain",
    position=(75.0, 130.0),
    effects={'size': (1.27, 1.27)}
)

sch.add_text(
    "5. Power Distribution",
    position=(75.0, 20.0),
    effects={'size': (1.27, 1.27)}
)

# ============================================================================
# Save Schematic
# ============================================================================
output_path = "orthogonal_routing_demo.kicad_sch"
sch.save(output_path)

print(f"\n✅ Schematic created successfully!")
print(f"📄 Saved to: {output_path}")
print(f"📊 Statistics:")
print(f"   - Components: {len(list(sch.components))}")
print(f"   - Wires: {len(list(sch.wires))}")
print(f"   - Labels: {len([item for item in sch._data.get('items', []) if isinstance(item, list) and len(item) > 0 and item[0] == 'label'])}")
print(f"\n🎯 Open in KiCAD to see the routing in action!")
