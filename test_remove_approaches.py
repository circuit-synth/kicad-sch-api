"""Test different approaches to removing a component."""

import kicad_sch_api as ksa
from pathlib import Path

test_file = Path("/tmp/test_remove.kicad_sch")

# Create schematic with 2 components
sch = ksa.Schematic.create()
c1 = sch.components.add(lib_id="Device:R", reference="R1", value="10k", position=(50, 50))
c2 = sch.components.add(lib_id="Device:R", reference="R2", value="20k", position=(100, 50))
sch.save(str(test_file))

# Reload
sch = ksa.Schematic.load(str(test_file))
print(f"Components before: {[c.reference for c in sch.components]}")
print(f"Component types: {[type(c).__name__ for c in sch.components]}")

r2 = None
for c in sch.components:
    if c.reference == "R2":
        r2 = c
        break

print(f"\nR2 object type: {type(r2)}")
print(f"R2 uuid: {r2.uuid}")
print(f"R2 reference: {r2.reference}")

# Approach 1: Try removing by component object
print(f"\n--- Approach 1: Remove by component object ---")
result1 = sch.components.remove(r2)
print(f"Result: {result1}")
print(f"Components after: {[c.reference for c in sch.components]}")

# Reload for next test
sch = ksa.Schematic.load(str(test_file))
r2 = [c for c in sch.components if c.reference == "R2"][0]

# Approach 2: Try removing by reference string
print(f"\n--- Approach 2: Remove by reference string ---")
result2 = sch.components.remove("R2")
print(f"Result: {result2}")
print(f"Components after: {[c.reference for c in sch.components]}")

# Reload for next test  
sch = ksa.Schematic.load(str(test_file))
r2 = [c for c in sch.components if c.reference == "R2"][0]

# Approach 3: Try removing by UUID string
print(f"\n--- Approach 3: Remove by UUID string ---")
r2_uuid = r2.uuid
result3 = sch.components.remove(r2_uuid)
print(f"Result: {result3}")
print(f"Components after: {[c.reference for c in sch.components]}")

# Cleanup
test_file.unlink(missing_ok=True)
