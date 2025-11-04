#!/usr/bin/env python3
"""
Quick test to verify instance preservation works.
"""

import sys
import logging
from pathlib import Path

# Setup logging to see our debug messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Add kicad_sch_api to path
sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import SymbolInstance

print("=" * 70)
print("TEST: Instance Preservation")
print("=" * 70)

# Create a minimal schematic
print("\n1. Creating schematic...")
sch = Schematic(name="test_project")

# Add a component
print("\n2. Adding component R1...")
comp = sch.add_component(
    library_id="Device:R",
    reference="R1",
    value="10k",
    position=(100, 100)
)

print(f"   Component created: {comp.reference}")
print(f"   Component has instances field: {hasattr(comp._data, 'instances')}")
print(f"   Current instances: {comp._data.instances}")

# Set hierarchical instance path manually
ROOT_UUID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
CHILD_UUID = "11111111-2222-3333-4444-555555555555"
hierarchical_path = f"/{ROOT_UUID}/{CHILD_UUID}"

print(f"\n3. Setting hierarchical instance path: {hierarchical_path}")
inst = SymbolInstance(
    path=hierarchical_path,
    reference="R1",
    unit=1
)
comp._data.instances = [inst]

print(f"   Instances after setting: {comp._data.instances}")
print(f"   Instance path: {comp._data.instances[0].path}")

# Save to file
output_path = Path("/tmp/test_hierarchical.kicad_sch")
print(f"\n4. Saving to {output_path}...")
sch.save(str(output_path))

print("\n5. Reloading schematic...")
reloaded = Schematic.load(str(output_path))

print(f"   Components count: {len(reloaded.components)}")
if len(reloaded.components) > 0:
    reloaded_comp = list(reloaded.components)[0]
    print(f"   Component reference: {reloaded_comp.reference}")
    print(f"   Component has instances: {hasattr(reloaded_comp._data, 'instances')}")
    print(f"   Instances count: {len(reloaded_comp._data.instances)}")
    if reloaded_comp._data.instances:
        print(f"   Instance[0] path: {reloaded_comp._data.instances[0].path}")
        print(f"   Instance[0] reference: {reloaded_comp._data.instances[0].reference}")

        # THE CRITICAL TEST
        if reloaded_comp._data.instances[0].path == hierarchical_path:
            print("\n✅ SUCCESS: Hierarchical path preserved!")
        else:
            print(f"\n❌ FAIL: Path changed!")
            print(f"   Expected: {hierarchical_path}")
            print(f"   Got: {reloaded_comp._data.instances[0].path}")
            sys.exit(1)
else:
    print("\n❌ FAIL: No components in reloaded schematic!")
    sys.exit(1)

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)
