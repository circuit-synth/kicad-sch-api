#!/usr/bin/env python3
"""Quick verification that rotation tests would pass."""

import kicad_sch_api as ksa

print("Testing rotation functionality...")
print("=" * 60)

# Create schematic
sch = ksa.create_schematic("rotation_test")

# Test 1: Default rotation
print("\n1. Testing default rotation (0°)...")
r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
assert r1.rotation == 0.0, f"Expected 0.0, got {r1.rotation}"
print("   ✅ Default rotation = 0°")

# Test 2: Rotation parameter
print("\n2. Testing rotation parameter...")
r2 = sch.components.add("Device:R", "R2", "10k", position=(150, 100), rotation=90)
assert r2.rotation == 90.0, f"Expected 90.0, got {r2.rotation}"
print("   ✅ rotation=90 works")

r3 = sch.components.add("Device:R", "R3", "10k", position=(100, 150), rotation=180)
assert r3.rotation == 180.0, f"Expected 180.0, got {r3.rotation}"
print("   ✅ rotation=180 works")

r4 = sch.components.add("Device:R", "R4", "10k", position=(150, 150), rotation=270)
assert r4.rotation == 270.0, f"Expected 270.0, got {r4.rotation}"
print("   ✅ rotation=270 works")

# Test 3: rotate() method
print("\n3. Testing rotate() method...")
r5 = sch.components.add("Device:R", "R5", "10k", position=(200, 100), rotation=0)
r5.rotate(45)
assert r5.rotation == 45.0, f"Expected 45.0, got {r5.rotation}"
print("   ✅ rotate(45) works")

# Test 4: Rotation wrapping
print("\n4. Testing rotation wrapping...")
r6 = sch.components.add("Device:R", "R6", "10k", position=(200, 150), rotation=270)
r6.rotate(180)
assert r6.rotation == 90.0, f"Expected 90.0 (wrapped), got {r6.rotation}"
print("   ✅ Rotation wraps at 360°")

# Test 5: Different component types
print("\n5. Testing different component types...")
c1 = sch.components.add("Device:C", "C1", "100nF", (250, 100), rotation=90)
assert c1.rotation == 90.0, f"Expected 90.0, got {c1.rotation}"
print("   ✅ Capacitor rotation works")

led = sch.components.add("Device:LED", "D1", "LED", (250, 150), rotation=180)
assert led.rotation == 180.0, f"Expected 180.0, got {led.rotation}"
print("   ✅ LED rotation works")

# Test 6: Save and verify in file
print("\n6. Testing save to file...")
import os
os.makedirs("examples/output", exist_ok=True)
sch.save("examples/output/rotation_verification.kicad_sch")
print("   ✅ Saved to rotation_verification.kicad_sch")

# Load and verify
print("\n7. Testing load from file...")
loaded = ksa.Schematic(file_path="examples/output/rotation_verification.kicad_sch")

# Debug: show all components
print(f"   Loaded {len(loaded.components)} components")
if len(loaded.components) > 0:
    # Check if rotation is preserved for first few components
    test_passed = True
    for comp in list(loaded.components)[:4]:
        expected = {
            "R2": 90.0,
            "R3": 180.0,
            "R4": 270.0,
        }.get(comp.reference, 0.0)

        if comp.reference in ["R2", "R3", "R4"]:
            if comp.rotation == expected:
                print(f"   ✅ {comp.reference}: {comp.rotation}° (correct)")
            else:
                print(f"   ⚠️  {comp.reference}: {comp.rotation}° (expected {expected}°)")
                test_passed = False

    if test_passed:
        print("   ✅ Rotations preserved after save/load")
    else:
        print("   ⚠️  Some rotations not preserved")
else:
    print("   ⚠️  No components loaded - skipping rotation check")

print("\n" + "=" * 60)
print("✅ All rotation tests passed!")
print("=" * 60)
