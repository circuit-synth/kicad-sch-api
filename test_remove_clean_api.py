"""Test component removal with clean API."""

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

r2 = [c for c in sch.components if c.reference == "R2"][0]
r2_uuid = r2.uuid

# Approach 1: Remove by reference
print(f"\n--- Approach 1: remove('R2') ---")
result = sch.components.remove("R2")
print(f"Result: {result}")
print(f"Components after: {[c.reference for c in sch.components]}")

# Reload for next test
sch = ksa.Schematic.load(str(test_file))

# Approach 2: Remove by UUID
print(f"\n--- Approach 2: remove_by_uuid(uuid) ---")
r2 = [c for c in sch.components if c.reference == "R2"][0]
result = sch.components.remove_by_uuid(r2.uuid)
print(f"Result: {result}")
print(f"Components after: {[c.reference for c in sch.components]}")

# Reload for next test
sch = ksa.Schematic.load(str(test_file))

# Approach 3: Remove by component object
print(f"\n--- Approach 3: remove_component(component) ---")
r2 = [c for c in sch.components if c.reference == "R2"][0]
result = sch.components.remove_component(r2)
print(f"Result: {result}")
print(f"Components after: {[c.reference for c in sch.components]}")

# Save and verify persistence
print(f"\n--- Verify persistence ---")
sch.save(str(test_file))
sch_verify = ksa.Schematic.load(str(test_file))
print(f"After save/reload: {[c.reference for c in sch_verify.components]}")

if len(sch_verify.components) == 1 and sch_verify.components[0].reference == "R1":
    print("✅ Persistence verified!")
else:
    print("❌ Persistence failed!")

# Cleanup
test_file.unlink(missing_ok=True)
