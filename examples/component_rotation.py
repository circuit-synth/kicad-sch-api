#!/usr/bin/env python3
"""
Component Rotation Example

Demonstrates how to add components with different rotations and how
the rotation parameter works with kicad-sch-api.

Key Features Shown:
- Adding components with rotation parameter (0°, 90°, 180°, 270°)
- Using the rotate() method to rotate components after creation
- Rotation normalization (values wrap at 360°)
- Property rotation preservation through load/save
"""

import os
import kicad_sch_api as ksa


def main():
    """Create a schematic demonstrating component rotation."""

    print("Creating schematic with rotated components...")
    print("=" * 70)

    # Create schematic
    sch = ksa.create_schematic("Component Rotation Demo")

    # =========================================================================
    # 1. Add Components with Different Rotations
    # =========================================================================
    print("\n1. Adding components with rotation parameter:")

    # Row 1: Standard rotations (0°, 90°, 180°, 270°)
    r1 = sch.components.add(
        "Device:R", "R1", "10k",
        position=(100, 100),
        rotation=0,
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    print(f"   R1: rotation={r1.rotation}° (horizontal)")

    r2 = sch.components.add(
        "Device:R", "R2", "10k",
        position=(125, 100),
        rotation=90,
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    print(f"   R2: rotation={r2.rotation}° (vertical)")

    r3 = sch.components.add(
        "Device:R", "R3", "10k",
        position=(150, 100),
        rotation=180,
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    print(f"   R3: rotation={r3.rotation}° (horizontal, flipped)")

    r4 = sch.components.add(
        "Device:R", "R4", "10k",
        position=(175, 100),
        rotation=270,
        footprint="Resistor_SMD:R_0603_1608Metric"
    )
    print(f"   R4: rotation={r4.rotation}° (vertical, flipped)")

    # Row 2: More components at standard angles
    print("\n2. Adding capacitors with standard rotations:")

    c1 = sch.components.add(
        "Device:C", "C1", "100nF",
        position=(100, 125),
        rotation=0,
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )
    print(f"   C1: rotation={c1.rotation}° (horizontal)")

    c2 = sch.components.add(
        "Device:C", "C2", "100nF",
        position=(125, 125),
        rotation=90,
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )
    print(f"   C2: rotation={c2.rotation}° (vertical)")

    # =========================================================================
    # 2. Using the rotate() Method
    # =========================================================================
    print("\n3. Using rotate() method to rotate components:")

    led1 = sch.components.add(
        "Device:LED", "D1", "LED",
        position=(100, 150),
        rotation=0,
        footprint="LED_SMD:LED_0603_1608Metric"
    )
    print(f"   D1 initial: {led1.rotation}°")

    led1.rotate(90)
    print(f"   D1 after rotate(90): {led1.rotation}°")

    led1.rotate(90)
    print(f"   D1 after rotate(90) again: {led1.rotation}°")

    # =========================================================================
    # 3. Rotation Normalization
    # =========================================================================
    print("\n4. Rotation normalization (values wrap at 360°):")

    # Test with value > 360
    led2 = sch.components.add(
        "Device:LED", "D2", "LED",
        position=(125, 150),
        rotation=450,  # Will normalize to 90°
        footprint="LED_SMD:LED_0603_1608Metric"
    )
    print(f"   D2 set to 450°, normalized to: {led2.rotation}°")

    # Test with negative value
    led3 = sch.components.add(
        "Device:LED", "D3", "LED",
        position=(150, 150),
        rotation=-90,  # Will normalize to 270°
        footprint="LED_SMD:LED_0603_1608Metric"
    )
    print(f"   D3 set to -90°, normalized to: {led3.rotation}°")

    # =========================================================================
    # 4. Practical Example: Create a Resistor Array
    # =========================================================================
    print("\n5. Creating a resistor array with alternating orientations:")

    for i in range(4):
        rotation = 0 if i % 2 == 0 else 90
        position = (100 + i * 15, 175)

        sch.components.add(
            "Device:R",
            f"R{i+10}",
            "1k",
            position=position,
            rotation=rotation,
            footprint="Resistor_SMD:R_0603_1608Metric"
        )
        print(f"   R{i+10}: position={position}, rotation={rotation}°")

    # =========================================================================
    # 5. Add Labels
    # =========================================================================

    sch.add_text("Standard Rotations", position=(95, 90))
    sch.add_text("Arbitrary Angles", position=(95, 115))
    sch.add_text("Rotate Method", position=(95, 140))
    sch.add_text("Resistor Array", position=(95, 165))

    # =========================================================================
    # 6. Save Schematic
    # =========================================================================

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "component_rotation.kicad_sch")

    sch.save(output_file)

    print("\n" + "=" * 70)
    print(f"✅ Created schematic: {output_file}")
    print(f"   Components: {len(sch.components)}")
    print("\nOpen in KiCad to see the rotated components!")
    print("\nNote: Property rotations (Reference, Value labels) are automatically")
    print("      calculated based on component rotation and preserved through")
    print("      load/save cycles.")
    print("=" * 70)


if __name__ == "__main__":
    main()
