#!/usr/bin/env python3
"""Debug script to understand save issue."""

import kicad_sch_api as ksa

# Create a simple schematic
sch = ksa.create_schematic("debug_test")

# Add a resistor
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(100, 100)
)

# Print data structure before save
print("=== Data structure before save ===")
print(f"Data keys: {list(sch._data.keys())}")
print(f"Components count: {len(sch._components)}")
print(f"Components data before sync: {sch._data.get('components', 'NOT FOUND')}")

# Manually call sync to debug
print("\n=== Calling sync manually ===")
sch._sync_components_to_data()
print(f"Components data after sync: {sch._data.get('components', 'NOT FOUND')}")
print(f"Lib symbols after sync: {len(sch._data.get('lib_symbols', []))}")

# Try to save
try:
    sch.save("debug_test.kicad_sch")
    print("✅ Save succeeded")

    # Check file content
    with open("debug_test.kicad_sch", "r") as f:
        content = f.read()
    print(f"Generated file size: {len(content)} chars")
    print(f"First 500 chars:\n{content[:500]}")

except Exception as e:
    print(f"❌ Save failed: {e}")
    import traceback
    traceback.print_exc()