"""Test component removal with file roundtrip (the real bug)."""

import kicad_sch_api as ksa
from pathlib import Path

test_file = Path("/tmp/test_component_removal.kicad_sch")

# Create a simple schematic with 2 components
sch = ksa.Schematic.create()
c1 = sch.components.add(lib_id="Device:R", reference="R1", value="10k", position=(50, 50))
c2 = sch.components.add(lib_id="Device:R", reference="R2", value="20k", position=(100, 50))

print(f"Created schematic with 2 components")
print(f"  Components: {[c.reference for c in sch.components]}")

# Save it
sch.save(str(test_file), preserve_format=False)
print(f"\nSaved to {test_file}")

# Load it back
sch2 = ksa.Schematic.load(str(test_file))
print(f"\nAfter reload:")
components_before = [c.reference for c in sch2.components]
print(f"  Components: {components_before}")
assert len(sch2.components) == 2, "Should have 2 components after reload"

# Now remove R2
print(f"\nRemoving R2...")
r2 = None
for c in sch2.components:
    if c.reference == "R2":
        r2 = c
        break

if r2:
    # Try to remove it by reference (as the API supports)
    result = sch2.components.remove(r2)
    print(f"  Removal returned: {result}")
    
    print(f"\nAfter removal (before save):")
    components_after_removal = [c.reference for c in sch2.components]
    print(f"  Components in sch2: {components_after_removal}")
    
    # Save again
    sch2.save(str(test_file), preserve_format=True)
    print(f"\nSaved after removal")
    
    # Reload to verify
    sch3 = ksa.Schematic.load(str(test_file))
    print(f"\nAfter final reload:")
    components_final = [c.reference for c in sch3.components]
    print(f"  Components: {components_final}")
    
    if any(c.reference == "R2" for c in sch3.components):
        print(f"❌ FAILURE: R2 still exists after save/reload!")
        for c in sch3.components:
            print(f"    {c.reference}: uuid={c.uuid}")
    else:
        print(f"✅ SUCCESS: R2 was properly removed!")
else:
    print("R2 not found")

# Cleanup
if test_file.exists():
    test_file.unlink()
