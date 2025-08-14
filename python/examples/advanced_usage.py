#!/usr/bin/env python3
"""
Advanced usage example for kicad-sch-api.

Demonstrates advanced features like bulk operations, filtering,
validation, and performance optimization for large schematics.
"""

import time

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point


def create_resistor_network():
    """Create a large resistor network to demonstrate performance."""
    print("🏗️ Creating large resistor network...")

    sch = ksa.create_schematic("Resistor Network")

    # Create a 10x10 grid of resistors (100 total)
    resistors = []
    start_time = time.time()

    for row in range(10):
        for col in range(10):
            ref = f"R{row*10 + col + 1}"
            value = f"{(row + 1) * (col + 1)}k"  # Varied values
            position = (col * 15 + 50, row * 15 + 50)  # 15mm spacing

            resistor = sch.components.add(
                lib_id="Device:R",
                reference=ref,
                value=value,
                position=position,
                footprint="Resistor_SMD:R_0603_1608Metric",
            )
            resistors.append(resistor)

    creation_time = time.time() - start_time
    print(f"✅ Created {len(resistors)} resistors in {creation_time:.3f}s")

    return sch, resistors


def demonstrate_filtering():
    """Demonstrate advanced component filtering capabilities."""
    print("\n🔍 Advanced Component Filtering:")

    sch, resistors = create_resistor_network()

    # Filter by lib_id
    all_resistors = sch.components.filter(lib_id="Device:R")
    print(f"  All resistors: {len(all_resistors)}")

    # Filter by value pattern
    high_value = sch.components.filter(value_pattern="k")
    print(f"  High value (k-ohm): {len(high_value)}")

    # Filter by reference pattern
    import re

    top_row = sch.components.filter(reference_pattern=r"R[1-9]$")  # R1-R9
    print(f"  Top row (R1-R9): {len(top_row)}")

    # Spatial filtering
    center_area = sch.components.in_area(80, 80, 120, 120)
    print(f"  Components in center area: {len(center_area)}")

    # Proximity filtering
    center_point = Point(100, 100)
    nearby = sch.components.near_point(center_point, radius=30)
    print(f"  Components near center: {len(nearby)}")

    return sch


def demonstrate_bulk_operations():
    """Demonstrate bulk update operations for large schematics."""
    print("\n⚡ Bulk Operations Performance:")

    sch = demonstrate_filtering()

    # Bulk update all resistors
    start_time = time.time()

    updated_count = sch.components.bulk_update(
        criteria={"lib_id": "Device:R"},
        updates={
            "properties": {
                "Tolerance": "1%",
                "Power": "0.1W",
                "Manufacturer": "Yageo",
                "Temperature_Coefficient": "100ppm/K",
            }
        },
    )

    bulk_time = time.time() - start_time
    print(f"✅ Bulk updated {updated_count} components in {bulk_time:.3f}s")
    print(f"  Performance: {bulk_time/updated_count*1000:.2f}ms per component")

    # Verify updates applied
    sample_resistor = sch.components.get("R1")
    if sample_resistor:
        print(f"  Sample properties: {len(sample_resistor.properties)} properties set")
        print(f"    Tolerance: {sample_resistor.get_property('Tolerance')}")
        print(f"    Power: {sample_resistor.get_property('Power')}")

    return sch


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring and statistics."""
    print("\n📊 Performance Monitoring:")

    sch = demonstrate_bulk_operations()

    # Get comprehensive performance statistics
    stats = sch.get_performance_stats()

    print("  Schematic Performance:")
    schematic_stats = stats.get("schematic", {})
    print(f"    Operations: {schematic_stats.get('operation_count', 0)}")
    print(f"    Avg time: {schematic_stats.get('avg_operation_time_ms', 0):.2f}ms")

    print("  Component Collection:")
    component_stats = stats.get("components", {})
    print(f"    Total components: {component_stats.get('total_components', 0)}")
    print(f"    Unique references: {component_stats.get('unique_references', 0)}")
    print(f"    Libraries used: {component_stats.get('libraries_used', 0)}")

    print("  Symbol Cache:")
    cache_stats = stats.get("symbol_cache", {})
    print(f"    Cache hit rate: {cache_stats.get('hit_rate_percent', 0):.1f}%")
    print(f"    Symbols cached: {cache_stats.get('total_symbols_cached', 0)}")
    print(f"    Total load time: {cache_stats.get('total_load_time_ms', 0):.1f}ms")

    return sch


def demonstrate_validation_and_error_handling():
    """Demonstrate comprehensive validation and error handling."""
    print("\n✅ Validation and Error Handling:")

    sch = ksa.create_schematic("Validation Test")

    # Add valid components
    sch.components.add("Device:R", "R1", "10k", (100, 50))
    sch.components.add("Device:C", "C1", "0.1uF", (150, 50))

    # Test validation
    issues = sch.validate()
    print(f"  Validation issues found: {len(issues)}")

    # Categorize issues
    errors = [issue for issue in issues if issue.level.value in ("error", "critical")]
    warnings = [issue for issue in issues if issue.level.value == "warning"]

    print(f"    Errors: {len(errors)}")
    print(f"    Warnings: {len(warnings)}")

    if issues:
        print("  Issue details:")
        for issue in issues[:3]:  # Show first 3
            print(f"    {issue.level.value.upper()}: {issue.message}")

    # Demonstrate error handling
    print("\n🛡️ Error Handling Examples:")

    try:
        # Try to add component with invalid reference
        sch.components.add("Device:R", "1R", "10k")  # Invalid reference
    except ksa.ValidationError as e:
        print(f"  ✅ Caught validation error: {e}")

    try:
        # Try to add duplicate reference
        sch.components.add("Device:C", "R1", "22uF")  # Duplicate reference
    except ksa.ValidationError as e:
        print(f"  ✅ Caught duplicate reference: {e}")

    try:
        # Try invalid lib_id
        sch.components.add("InvalidFormat", "R5", "10k")  # Missing colon
    except ksa.ValidationError as e:
        print(f"  ✅ Caught invalid lib_id: {e}")

    return sch


def demonstrate_format_preservation():
    """Demonstrate exact format preservation capabilities."""
    print("\n💎 Format Preservation:")

    sch = ksa.create_schematic("Format Test")
    sch.components.add("Device:R", "R1", "10k", (100, 50))

    import os
    import tempfile

    # Save with format preservation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".kicad_sch", delete=False) as f:
        output_path = f.name

    try:
        start_time = time.time()
        sch.save(output_path, preserve_format=True)
        save_time = time.time() - start_time

        print(f"  ✅ Saved with format preservation in {save_time:.3f}s")

        # Reload and verify
        start_time = time.time()
        sch2 = ksa.load_schematic(output_path)
        load_time = time.time() - start_time

        print(f"  ✅ Reloaded in {load_time:.3f}s")
        print(f"  ✅ Component preservation: {len(sch2.components)} components")

        # Verify component data preserved
        r1_original = sch.components.get("R1")
        r1_reloaded = sch2.components.get("R1")

        if r1_original and r1_reloaded:
            print(f"    Reference: {r1_reloaded.reference} ✅")
            print(f"    Value: {r1_reloaded.value} ✅")
            print(f"    Position: {r1_reloaded.position} ✅")
            print(f"    Lib ID: {r1_reloaded.lib_id} ✅")

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def demonstrate_library_integration():
    """Demonstrate symbol library integration."""
    print("\n📚 Symbol Library Integration:")

    # Get global symbol cache
    cache = ksa.get_symbol_cache()

    # Library discovery
    discovered = cache.discover_libraries()
    print(f"  Libraries discovered: {discovered}")

    # Symbol search
    symbols = cache.search_symbols("resistor", limit=5)
    print(f"  Resistor symbols found: {len(symbols)}")

    for symbol in symbols[:3]:  # Show first 3
        print(f"    {symbol.lib_id}: {symbol.description}")

    # Cache performance
    cache_stats = cache.get_performance_stats()
    print(f"  Cache performance:")
    print(f"    Hit rate: {cache_stats.get('hit_rate_percent', 0):.1f}%")
    print(f"    Total symbols: {cache_stats.get('total_symbols_cached', 0)}")


def main():
    """Run all advanced usage examples."""
    print("🚀 kicad-sch-api Advanced Usage Examples")
    print("=" * 60)

    try:
        # Run all demonstrations
        demonstrate_filtering()
        demonstrate_bulk_operations()
        demonstrate_performance_monitoring()
        demonstrate_validation_and_error_handling()
        demonstrate_format_preservation()
        demonstrate_library_integration()

        print("\n🎉 All advanced examples completed successfully!")
        print("\nAdvanced features demonstrated:")
        print("  ✅ High-performance component collections")
        print("  ✅ Bulk operations for large schematics")
        print("  ✅ Comprehensive validation and error handling")
        print("  ✅ Exact format preservation")
        print("  ✅ Symbol library caching and discovery")
        print("  ✅ Performance monitoring and statistics")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
