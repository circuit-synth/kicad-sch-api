"""Create reference schematic for PS2: Hierarchical power symbols"""

import sys

sys.path.insert(0, "/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api")

import kicad_sch_api as ksa

print("=" * 80)
print("PS2: HIERARCHICAL POWER SYMBOLS")
print("=" * 80)

# Create parent schematic
print("\n1. Creating parent schematic...")
parent = ksa.create_schematic("PS2: Hierarchical Power")

# Add resistor in parent
r1 = parent.components.add(lib_id="Device:R", reference="R1", value="10k", position=(100, 100))
print(f"   ✓ Added R1 at (100, 100)")

# Add power symbol in parent (VCC)
try:
    vcc_parent = parent.components.add(
        lib_id="power:VCC", reference="#PWR01", value="VCC", position=(100, 90)
    )
    print(f"   ✓ Added VCC power symbol in parent")
except Exception as e:
    print(f"   ⚠ Could not add VCC symbol: {e}")

# Add hierarchical sheet
print("\n   Adding hierarchical sheet...")
sheet_uuid = parent.sheets.add_sheet(
    name="Child Circuit", filename="child_circuit.kicad_sch", position=(140, 80), size=(40, 50)
)
print(f"   ✓ Added hierarchical sheet: {sheet_uuid[:8]}...")

# Add sheet pin for DATA signal
print("   Adding sheet pin 'DATA'...")
pin_uuid = parent.sheets.add_sheet_pin(
    sheet_uuid=sheet_uuid,
    name="DATA",
    pin_type="input",
    position=(140, 100),  # Left edge of sheet
    justify="right",
)
print(f"   ✓ Added sheet pin 'DATA': {pin_uuid[:8]}...")

# Save parent schematic
parent_path = "tests/reference_kicad_projects/connectivity/ps2_hierarchical_power/ps2_hierarchical_power.kicad_sch"
parent.save(parent_path)
print(f"   ✓ Saved parent: {parent_path}")

# Create child schematic
print("\n2. Creating child schematic...")
child = ksa.create_schematic("PS2 Child Circuit")

# Add resistor in child
r2 = child.components.add(lib_id="Device:R", reference="R2", value="10k", position=(130, 100))
print(f"   ✓ Added R2 at (130, 100)")

# Add power symbol in child (GND)
try:
    gnd_child = child.components.add(
        lib_id="power:GND", reference="#PWR02", value="GND", position=(130, 110)
    )
    print(f"   ✓ Added GND power symbol in child")
except Exception as e:
    print(f"   ⚠ Could not add GND symbol: {e}")

# Save child schematic
child_path = (
    "tests/reference_kicad_projects/connectivity/ps2_hierarchical_power/child_circuit.kicad_sch"
)
child.save(child_path)
print(f"   ✓ Saved child: {child_path}")

print("\n" + "=" * 80)
print("WHAT TO ADD IN KICAD (PARENT SCHEMATIC):")
print("=" * 80)
print(
    """
1. Open ps2_hierarchical_power.kicad_sch in KiCAD
   (Should already have R1, VCC power symbol, and hierarchical sheet with DATA pin)

2. Add wire from VCC (#PWR01) to R1 pin 1 [TOP pin - visually at top]

3. Add wire from R1 pin 2 [BOTTOM pin - visually at bottom] to the right

4. Add local label "DATA" on that wire

5. Add wire connecting DATA label to sheet pin on hierarchical sheet border

6. Save parent schematic
"""
)

print("=" * 80)
print("WHAT TO ADD IN KICAD (CHILD SCHEMATIC):")
print("=" * 80)
print(
    """
1. Open child_circuit.kicad_sch in KiCAD

2. Add hierarchical label "DATA":
   - Type: Input (to match parent sheet pin)
   - Position: to the left of R2

3. Add wire from DATA label to R2 pin 1 [TOP pin - visually at top]

4. Add wire from R2 pin 2 [BOTTOM pin - visually at bottom] to GND (#PWR02)

5. Save child schematic
"""
)

print("\n" + "=" * 80)
print("EXPECTED CONNECTIVITY:")
print("=" * 80)
print(
    """
After completing both schematics:

1. VCC net (global power symbol):
   - Parent: VCC power symbol (#PWR01)
   - Parent: R1.1 (pin 1 - visually top)
   - Should be global across all sheets

2. DATA net (hierarchical connection):
   - Parent: R1.2 (pin 2 - visually bottom), label "DATA"
   - Child: hierarchical label "DATA", R2.1 (pin 1 - visually top)
   - Connected via sheet pin

3. GND net (global power symbol):
   - Child: R2.2 (pin 2 - visually bottom)
   - Child: GND power symbol (#PWR02)
   - Should be global across all sheets

Expected net count: 3 nets (VCC, DATA, GND)
"""
)
print("=" * 80)
