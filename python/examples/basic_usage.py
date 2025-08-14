#!/usr/bin/env python3
"""
Basic usage example for kicad-sch-api.

This example demonstrates the core functionality of kicad-sch-api,
showing how to create, manipulate, and save KiCAD schematic files.
"""

import kicad_sch_api as ksa


def main():
    """Demonstrate basic kicad-sch-api usage."""
    print("🚀 kicad-sch-api Basic Usage Example")
    print("=" * 50)

    # 1. Create a new schematic
    print("\n📋 Creating new schematic...")
    sch = ksa.create_schematic("Voltage Divider Example")
    print(f"✅ Created schematic: {sch.title_block.get('title', 'Untitled')}")

    # 2. Add components
    print("\n🔧 Adding components...")

    # Add input resistor
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100, 100),
        footprint="Resistor_SMD:R_0603_1608Metric",
    )
    print(f"✅ Added {r1.reference}: {r1.value} at {r1.position}")

    # Add output resistor
    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="10k",
        position=(100, 150),
        footprint="Resistor_SMD:R_0603_1608Metric",
    )
    print(f"✅ Added {r2.reference}: {r2.value} at {r2.position}")

    # Add input capacitor for filtering
    c1 = sch.components.add(
        lib_id="Device:C",
        reference="C1",
        value="0.1uF",
        position=(50, 125),
        footprint="Capacitor_SMD:C_0603_1608Metric",
    )
    print(f"✅ Added {c1.reference}: {c1.value} at {c1.position}")

    # 3. Set component properties
    print("\n📝 Setting component properties...")

    r1.set_property("MPN", "RC0603FR-0710KL")
    r1.set_property("Tolerance", "1%")
    r2.set_property("MPN", "RC0603FR-0710KL")
    r2.set_property("Tolerance", "1%")
    c1.set_property("MPN", "CL10B104KB8NNNC")
    c1.set_property("Voltage", "50V")

    print(f"✅ Set properties for all components")

    # 4. Add connections
    print("\n🔗 Adding wire connections...")

    # Get pin positions for connections
    r1_pin1 = r1.get_pin_position("1")  # Top of R1
    r1_pin2 = r1.get_pin_position("2")  # Bottom of R1
    r2_pin1 = r2.get_pin_position("1")  # Top of R2
    r2_pin2 = r2.get_pin_position("2")  # Bottom of R2
    c1_pin1 = c1.get_pin_position("1")  # Left of C1

    if all([r1_pin1, r1_pin2, r2_pin1, r2_pin2, c1_pin1]):
        # Connect R1 bottom to R2 top (voltage divider middle)
        wire1 = sch.add_wire(r1_pin2, r2_pin1)
        print(f"✅ Connected R1 pin 2 to R2 pin 1")

        # Connect input capacitor to R1 top
        wire2 = sch.add_wire(c1_pin1, r1_pin1)
        print(f"✅ Connected C1 to R1 input")
    else:
        print("⚠️ Could not determine pin positions for connections")

    # 5. Display schematic information
    print("\n📊 Schematic Summary:")
    summary = sch.get_summary()
    print(f"  Components: {summary['component_count']}")
    print(f"  Title: {summary['title']}")
    print(f"  Modified: {summary['modified']}")

    # 6. Component analysis
    print("\n🔍 Component Analysis:")

    # Find all resistors
    resistors = sch.components.filter(lib_id="Device:R")
    print(f"  Resistors found: {len(resistors)}")

    # Find components by value
    ten_k_components = sch.components.filter(value="10k")
    print(f"  10k components: {len(ten_k_components)}")

    # Find components in area
    left_side = sch.components.in_area(40, 90, 80, 160)
    print(f"  Components on left side: {len(left_side)}")

    # 7. Bulk operations
    print("\n⚡ Bulk Operations:")

    # Update all resistors with tolerance
    updated_count = sch.components.bulk_update(
        criteria={"lib_id": "Device:R"}, updates={"properties": {"Power": "0.1W"}}
    )
    print(f"✅ Updated {updated_count} resistors with power rating")

    # 8. Validation
    print("\n✅ Validation:")
    issues = sch.validate()
    errors = [issue for issue in issues if issue.level.value in ("error", "critical")]
    warnings = [issue for issue in issues if issue.level.value == "warning"]

    print(f"  Validation issues: {len(issues)} total")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print("  ❌ Critical errors found:")
        for error in errors[:3]:  # Show first 3
            print(f"    - {error}")
    else:
        print("  ✅ No critical errors found")

    # 9. Performance statistics
    print("\n⚡ Performance Statistics:")
    perf_stats = sch.get_performance_stats()

    if "symbol_cache" in perf_stats:
        cache_stats = perf_stats["symbol_cache"]
        print(f"  Symbol cache hit rate: {cache_stats.get('hit_rate_percent', 0)}%")
        print(f"  Symbols cached: {cache_stats.get('total_symbols_cached', 0)}")

    comp_stats = perf_stats.get("components", {})
    print(f"  Total components: {comp_stats.get('total_components', 0)}")

    # 10. Save schematic
    print("\n💾 Saving schematic...")
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
        output_path = f.name

    try:
        sch.save(output_path, preserve_format=True)
        print(f"✅ Saved schematic to: {output_path}")

        # Verify file was created and has content
        file_size = os.path.getsize(output_path)
        print(f"  File size: {file_size} bytes")

        # Quick validation by reloading
        sch2 = ksa.load_schematic(output_path)
        print(f"✅ Reload verification: {len(sch2.components)} components")

    finally:
        # Clean up temporary file
        if os.path.exists(output_path):
            os.unlink(output_path)
            print(f"🧹 Cleaned up temporary file")

    print("\n🎉 Basic usage example completed successfully!")
    print("\nKey takeaways:")
    print("  • Enhanced API: resistor.value = '10k' (vs kicad-skip's verbose syntax)")
    print("  • Fast operations: O(1) component lookup and bulk updates")
    print("  • Format preservation: Exact KiCAD compatibility guaranteed")
    print("  • Professional validation: Comprehensive error detection")
    print("  • Performance monitoring: Built-in statistics and optimization")


if __name__ == "__main__":
    main()
