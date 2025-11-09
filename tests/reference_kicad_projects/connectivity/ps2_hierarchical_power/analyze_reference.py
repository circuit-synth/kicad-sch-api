"""Analyze PS2 hierarchical power symbols reference schematics"""

import sys

sys.path.insert(0, "/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api")

import kicad_sch_api as ksa
from kicad_sch_api.core.pin_utils import list_component_pins

print("=" * 80)
print("PS2 HIERARCHICAL POWER SYMBOLS ANALYSIS")
print("=" * 80)

# Load parent schematic
print("\n" + "=" * 80)
print("PARENT SCHEMATIC")
print("=" * 80)

parent = ksa.Schematic.load(
    "tests/reference_kicad_projects/connectivity/ps2_hierarchical_power/ps2_hierarchical_power.kicad_sch"
)

print("\nCOMPONENTS:")
for comp in parent.components:
    print(f"\n{comp.reference} ({comp.lib_id}):")
    print(f"  Position: {comp.position}")
    print(f"  Value: {comp.value}")

    if comp.lib_id.startswith("power:"):
        print(f"  ⚡ POWER SYMBOL")

    pins = list_component_pins(comp)
    if pins:
        print(f"  Pins:")
        for pin_num, pin_pos in pins:
            print(f"    Pin {pin_num}: ({pin_pos.x:.2f}, {pin_pos.y:.2f})")

print(f"\nWIRES: {len(list(parent.wires))}")
for i, wire in enumerate(parent.wires, 1):
    print(
        f"Wire {i}: ({wire.points[0].x:.2f}, {wire.points[0].y:.2f}) → ({wire.points[-1].x:.2f}, {wire.points[-1].y:.2f})"
    )

print(f"\nLABELS: {len(list(parent.labels))}")
for label in parent.labels:
    print(f"Label '{label.text}' at ({label.position.x:.2f}, {label.position.y:.2f})")

print(f"\nHIERARCHICAL SHEETS:")
if hasattr(parent, "_data") and "sheets" in parent._data:
    sheets = parent._data.get("sheets", [])
    print(f"Found {len(sheets)} hierarchical sheets")
    for sheet in sheets:
        print(f"\nSheet: {sheet.get('name')}")
        print(f"  UUID: {sheet.get('uuid')}")
        print(f"  File: {sheet.get('filename')}")
        print(
            f"  Position: ({sheet.get('position', {}).get('x')}, {sheet.get('position', {}).get('y')})"
        )
        print(
            f"  Size: ({sheet.get('size', {}).get('width')} x {sheet.get('size', {}).get('height')})"
        )

        pins = sheet.get("pins", [])
        print(f"  Sheet Pins: {len(pins)}")
        for pin in pins:
            print(f"    Pin '{pin.get('name')}' ({pin.get('pin_type')})")
            print(
                f"      Position: ({pin.get('position', {}).get('x')}, {pin.get('position', {}).get('y')})"
            )
            print(f"      UUID: {pin.get('uuid')}")
else:
    print("No hierarchical sheets found")

# Load child schematic
print("\n" + "=" * 80)
print("CHILD SCHEMATIC")
print("=" * 80)

child = ksa.Schematic.load(
    "tests/reference_kicad_projects/connectivity/ps2_hierarchical_power/child_circuit.kicad_sch"
)

print("\nCOMPONENTS:")
for comp in child.components:
    print(f"\n{comp.reference} ({comp.lib_id}):")
    print(f"  Position: {comp.position}")
    print(f"  Value: {comp.value}")

    if comp.lib_id.startswith("power:"):
        print(f"  ⚡ POWER SYMBOL")

    pins = list_component_pins(comp)
    if pins:
        print(f"  Pins:")
        for pin_num, pin_pos in pins:
            print(f"    Pin {pin_num}: ({pin_pos.x:.2f}, {pin_pos.y:.2f})")

print(f"\nWIRES: {len(list(child.wires))}")
for i, wire in enumerate(child.wires, 1):
    print(
        f"Wire {i}: ({wire.points[0].x:.2f}, {wire.points[0].y:.2f}) → ({wire.points[-1].x:.2f}, {wire.points[-1].y:.2f})"
    )

print(f"\nHIERARCHICAL LABELS: {len(list(child.hierarchical_labels))}")
for label in child.hierarchical_labels:
    print(f"Hierarchical Label '{label.text}' at ({label.position.x:.2f}, {label.position.y:.2f})")
    if hasattr(label, "_data"):
        print(f"  Shape: {label._data.shape}")
        print(f"  UUID: {label._data.uuid}")

print("\n" + "=" * 80)
print("EXPECTED CONNECTIVITY")
print("=" * 80)
print(
    """
Multi-sheet connectivity should work as follows:

1. VCC net (global power symbol):
   - Parent: VCC power symbol (#PWR01)
   - Parent: R1.1
   - Should be accessible from child sheet (even though not wired there)

2. DATA net (hierarchical connection):
   - Parent: R1.2, label "DATA"
   - Parent: Sheet pin "DATA" (input)
   - Child: Hierarchical label "DATA" (input)
   - Child: R2.1
   - These should all be on the same net via sheet pin connection

3. GND net (global power symbol):
   - Child: R2.2
   - Child: GND power symbol (#PWR02)
   - Should be accessible from parent sheet (even though not wired there)

Expected: 3 nets total (VCC, DATA, GND)

Hierarchical connectivity requirements:
- Sheet pins in parent connect to hierarchical labels in child
- Pin names must match exactly
- Pin types should match (input/output/bidirectional)
- Power symbols are global across ALL sheets
"""
)
print("=" * 80)
