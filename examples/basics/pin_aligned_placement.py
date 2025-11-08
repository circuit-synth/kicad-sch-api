"""
Pin-Aligned Component Placement Example

This example demonstrates the new pin-aligned placement features that make it
easy to create clean horizontal signal flows without manual offset calculations.

Issue: https://github.com/circuit-synth/kicad-sch-api/issues/137
"""

import sys
from pathlib import Path

# Add repository root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import kicad_sch_api as ksa

# Create a new schematic
sch = ksa.create_schematic("PinAlignmentDemo")

print("=" * 70)
print("Pin-Aligned Component Placement Demo")
print("=" * 70)

# Example 1: Basic pin-aligned placement
print("\n1. Basic Pin-Aligned Placement")
print("-" * 70)

# Traditional approach (requires manual calculation):
# - Resistor at (100, 100)
# - Pin 2 is at offset (0, -3.81) from component center
# - To place pin 2 at (150, 100), component must be at (150, 103.81)

# NEW approach using add_with_pin_at():
r1 = sch.components.add_with_pin_at(
    lib_id="Device:R",
    pin_number="2",
    pin_position=(100, 100),  # Specify where pin 2 should be
    value="10k"
)

print(f"✓ Added {r1.reference} with pin 2 at (100, 100)")
print(f"  Component position: {r1.position}")
pin2_pos = r1.get_pin_position("2")
print(f"  Pin 2 actual position: {pin2_pos}")


# Example 2: Horizontal signal chain
print("\n2. Creating Horizontal Signal Chain (Voltage Divider)")
print("-" * 70)

signal_y = 150  # Horizontal signal line at Y=150

# Add first resistor with pin 2 on the signal line
r2 = sch.components.add_with_pin_at(
    lib_id="Device:R",
    pin_number="2",
    pin_position=(100, signal_y),
    value="10k",
    reference="R1"
)

# Add second resistor with pin 1 on the same signal line
# This creates a perfect horizontal connection point
r3 = sch.components.add_with_pin_at(
    lib_id="Device:R",
    pin_number="1",
    pin_position=(150, signal_y),
    value="10k",
    reference="R2"
)

print(f"✓ Created voltage divider:")
print(f"  {r2.reference} pin 2 at: {r2.get_pin_position('2')}")
print(f"  {r3.reference} pin 1 at: {r3.get_pin_position('1')}")
print(f"  Horizontal alignment error: {abs(r2.get_pin_position('2').y - r3.get_pin_position('1').y):.3f}mm")


# Example 3: RC Lowpass Filter
print("\n3. Creating RC Lowpass Filter with Perfect Alignment")
print("-" * 70)

filter_y = 200

# Input resistor
r_filter = sch.components.add_with_pin_at(
    lib_id="Device:R",
    pin_number="2",  # Output side
    pin_position=(100, filter_y),
    value="1k",
    reference="R3"
)

# Filter capacitor aligned with resistor output
c_filter = sch.components.add_with_pin_at(
    lib_id="Device:C",
    pin_number="1",  # Input side
    pin_position=(150, filter_y),
    value="100nF",
    reference="C1"
)

print(f"✓ Created RC filter:")
print(f"  {r_filter.reference} output: {r_filter.get_pin_position('2')}")
print(f"  {c_filter.reference} input: {c_filter.get_pin_position('1')}")


# Example 4: Aligning existing components
print("\n4. Realigning Existing Components")
print("-" * 70)

# Add a component at arbitrary position
r_messy = sch.components.add(
    lib_id="Device:R",
    position=(120, 275),  # Not aligned
    value="4.7k",
    reference="R4"
)

print(f"Before alignment: {r_messy.reference} pin 2 at {r_messy.get_pin_position('2')}")

# Align it to our signal line using align_pin()
target_y = 250
r_messy.align_pin("2", (r_messy.get_pin_position("2").x, target_y))

print(f"After alignment:  {r_messy.reference} pin 2 at {r_messy.get_pin_position('2')}")


# Example 5: Complex circuit with multiple alignments
print("\n5. Complex Circuit: Multiple Component Alignment")
print("-" * 70)

complex_y = 300

# Create a chain of components all aligned to the same horizontal line
components = []

components.append(sch.components.add_with_pin_at(
    lib_id="Device:R", pin_number="2", pin_position=(50, complex_y),
    value="1k", reference="R5"
))

components.append(sch.components.add_with_pin_at(
    lib_id="Device:C", pin_number="1", pin_position=(100, complex_y),
    value="100nF", reference="C2"
))

components.append(sch.components.add_with_pin_at(
    lib_id="Device:R", pin_number="1", pin_position=(150, complex_y),
    value="2k", reference="R6"
))

components.append(sch.components.add_with_pin_at(
    lib_id="Device:C", pin_number="1", pin_position=(200, complex_y),
    value="47nF", reference="C3"
))

print("✓ Created component chain with perfect horizontal alignment:")
# Show which pins were aligned (the ones specified in add_with_pin_at)
aligned_pins = ["2", "1", "1", "1"]  # R5:pin2, C2:pin1, R6:pin1, C3:pin1
for comp, pin in zip(components, aligned_pins):
    pos = comp.get_pin_position(pin)
    print(f"  {comp.reference:8s} pin {pin}: Y = {pos.y:.2f}mm")


# Example 6: Different rotations
print("\n6. Pin Alignment with Rotated Components")
print("-" * 70)

rotation_y = 350

# Horizontal resistor (0°)
r_h = sch.components.add_with_pin_at(
    lib_id="Device:R",
    pin_number="1",
    pin_position=(100, rotation_y),
    rotation=0,
    value="1k",
    reference="R7"
)

# Vertical resistor (90°) with pin 1 at same position
r_v = sch.components.add_with_pin_at(
    lib_id="Device:R",
    pin_number="1",
    pin_position=(150, rotation_y),
    rotation=90,
    value="1k",
    reference="R8"
)

print(f"✓ Rotated components:")
print(f"  {r_h.reference} (0°):   pin 1 at {r_h.get_pin_position('1')}")
print(f"  {r_v.reference} (90°):  pin 1 at {r_v.get_pin_position('1')}")


# Save the schematic
output_file = "pin_aligned_demo.kicad_sch"
sch.save(output_file)

print("\n" + "=" * 70)
print(f"✓ Schematic saved to: {output_file}")
print("=" * 70)

print("\nKey Benefits:")
print("  • No manual pin offset calculations required")
print("  • Perfect horizontal/vertical signal alignment")
print("  • Works with any rotation (0°, 90°, 180°, 270°)")
print("  • Automatic grid snapping for proper connectivity")
print("  • Clean, professional-looking schematics")

print("\nAPI Reference:")
print("  • add_with_pin_at()  - Add component positioned by pin")
print("  • align_pin()        - Move existing component to align pin")
print("  • calculate_position_for_pin() - Low-level position calculation")
