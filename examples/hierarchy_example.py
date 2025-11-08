"""
Example: Advanced Hierarchy Management with HierarchyManager

Demonstrates advanced hierarchical schematic features including:
- Sheet reuse tracking (sheets used multiple times)
- Cross-sheet signal tracking
- Sheet pin validation
- Hierarchy flattening
- Signal tracing
- Hierarchy visualization
"""

import kicad_sch_api as ksa
from pathlib import Path


def example_basic_hierarchy_tree():
    """Example: Building and exploring hierarchy tree."""
    print("\n=== Example 1: Basic Hierarchy Tree ===")

    # Create root schematic
    root = ksa.create_schematic("MyProject")

    # Add components to root
    root.components.add("Device:R", "R1", "10k", (100, 100))

    # Add hierarchical sheet
    sheet_uuid = root.sheets.add_sheet(
        name="Power Supply",
        filename="power.kicad_sch",
        position=(200, 100),
        size=(50, 50),
    )

    # Add sheet pins
    root.sheets.add_sheet_pin(sheet_uuid, "VCC", "output", "right", 10)
    root.sheets.add_sheet_pin(sheet_uuid, "GND", "output", "right", 20)

    # Build hierarchy tree
    tree = root.hierarchy.build_hierarchy_tree(root)

    print(f"Root node: {tree.name}")
    print(f"Hierarchy depth: {tree.get_depth()}")
    print(f"Children: {len(tree.children)}")


def example_reusable_sheets():
    """Example: Detecting sheets used multiple times."""
    print("\n=== Example 2: Reusable Sheets ===")

    # Create root schematic
    root = ksa.create_schematic("ModularDesign")

    # Add the same LED driver module 3 times
    for i in range(3):
        root.sheets.add_sheet(
            name=f"LED_Driver_{i+1}",
            filename="led_driver.kicad_sch",  # Same file reused!
            position=(100 + i * 70, 100),
            size=(60, 40),
        )

    # Build hierarchy
    tree = root.hierarchy.build_hierarchy_tree(root)

    # Find reused sheets
    reused = root.hierarchy.find_reused_sheets()

    print(f"Reused sheets: {len(reused)}")
    for filename, instances in reused.items():
        print(f"  '{filename}' used {len(instances)} times")
        for inst in instances:
            print(f"    - {inst.sheet_name} at path {inst.path}")


def example_sheet_pin_validation():
    """Example: Validating sheet pins against hierarchical labels."""
    print("\n=== Example 3: Sheet Pin Validation ===")

    # In a real scenario, you would:
    # 1. Create child schematic with hierarchical labels
    # 2. Create root with sheet pins
    # 3. Validate connections

    root = ksa.create_schematic("ValidationExample")

    # Add sheet
    sheet_uuid = root.sheets.add_sheet(
        name="SubModule",
        filename="submodule.kicad_sch",
        position=(100, 100),
        size=(50, 50),
    )

    # Add sheet pins
    root.sheets.add_sheet_pin(sheet_uuid, "DATA_IN", "input", "left", 10)
    root.sheets.add_sheet_pin(sheet_uuid, "DATA_OUT", "output", "right", 10)
    root.sheets.add_sheet_pin(sheet_uuid, "CLK", "input", "left", 20)

    # Build hierarchy
    tree = root.hierarchy.build_hierarchy_tree(root)

    # Validate sheet pins (requires child schematic to exist)
    connections = root.hierarchy.validate_sheet_pins()

    print(f"Total sheet pin connections: {len(connections)}")

    # Check for validation errors
    errors = root.hierarchy.get_validation_errors()
    if errors:
        print(f"Validation errors found: {len(errors)}")
        for error in errors:
            print(f"  - {error['pin_name']}: {error['error']}")
    else:
        print("All sheet pins validated successfully!")


def example_hierarchy_flattening():
    """Example: Flattening hierarchical design."""
    print("\n=== Example 4: Hierarchy Flattening ===")

    root = ksa.create_schematic("HierarchicalDesign")

    # Add root components
    root.components.add("Device:R", "R1", "1k", (100, 100))
    root.components.add("Device:C", "C1", "0.1uF", (150, 100))

    # Add hierarchical sheets (in real scenario, these would reference actual files)
    root.sheets.add_sheet("PowerModule", "power.kicad_sch", (200, 100), (50, 50))
    root.sheets.add_sheet("IoModule", "io.kicad_sch", (200, 200), (50, 50))

    # Build hierarchy
    tree = root.hierarchy.build_hierarchy_tree(root)

    # Flatten with reference prefixing
    flattened = root.hierarchy.flatten_hierarchy(prefix_references=True)

    print(f"Flattened components: {len(flattened['components'])}")
    print("Component references:")
    for comp in flattened['components']:
        print(f"  - {comp['reference']} (from {comp['hierarchy_path']})")

    print(f"\nFlattened wires: {len(flattened['wires'])}")
    print(f"Flattened labels: {len(flattened['labels'])}")


def example_hierarchy_statistics():
    """Example: Getting hierarchy statistics."""
    print("\n=== Example 5: Hierarchy Statistics ===")

    root = ksa.create_schematic("ComplexProject")

    # Add components
    root.components.add("Device:R", "R1", "10k", (100, 100))
    root.components.add("Device:R", "R2", "10k", (150, 100))

    # Add multiple sheets
    for i in range(3):
        root.sheets.add_sheet(
            f"Module{i+1}",
            f"module{i+1}.kicad_sch",
            (100 + i * 70, 200),
            (50, 50),
        )

    # Build hierarchy
    tree = root.hierarchy.build_hierarchy_tree(root)

    # Get statistics
    stats = root.hierarchy.get_hierarchy_statistics()

    print("Hierarchy Statistics:")
    print(f"  Total sheets: {stats['total_sheets']}")
    print(f"  Max depth: {stats['max_hierarchy_depth']}")
    print(f"  Reused sheets: {stats['reused_sheets_count']}")
    print(f"  Total components: {stats['total_components']}")
    print(f"  Total wires: {stats['total_wires']}")
    print(f"  Total labels: {stats['total_labels']}")
    print(f"  Sheet pin connections: {stats['sheet_pin_connections']}")
    print(f"  Valid connections: {stats['valid_connections']}")


def example_hierarchy_visualization():
    """Example: Visualizing hierarchy tree."""
    print("\n=== Example 6: Hierarchy Visualization ===")

    root = ksa.create_schematic("VisualExample")

    # Add hierarchical structure
    root.sheets.add_sheet("PowerSupply", "power.kicad_sch", (100, 100), (50, 50))
    root.sheets.add_sheet("MCU", "mcu.kicad_sch", (200, 100), (50, 50))
    root.sheets.add_sheet("Sensors", "sensors.kicad_sch", (300, 100), (50, 50))

    # Build hierarchy
    tree = root.hierarchy.build_hierarchy_tree(root)

    # Visualize without statistics
    print("Hierarchy Tree:")
    viz = root.hierarchy.visualize_hierarchy()
    print(viz)

    # Visualize with component counts
    print("\nHierarchy Tree with Statistics:")
    viz_stats = root.hierarchy.visualize_hierarchy(include_stats=True)
    print(viz_stats)


def example_signal_tracing():
    """Example: Tracing signals through hierarchy."""
    print("\n=== Example 7: Signal Tracing ===")

    root = ksa.create_schematic("SignalTracing")

    # Add labels
    root.add_label("VCC", position=(100, 100))
    root.add_global_label("USB_DP", position=(200, 100))

    # Build hierarchy
    tree = root.hierarchy.build_hierarchy_tree(root)

    # Trace signals
    vcc_paths = root.hierarchy.trace_signal_path("VCC")
    usb_paths = root.hierarchy.trace_signal_path("USB_DP")

    print(f"VCC signal paths: {len(vcc_paths)}")
    for path in vcc_paths:
        print(f"  Path: {path.start_path} → {path.end_path}")
        print(f"  Sheet crossings: {path.sheet_crossings}")
        print(f"  Connections: {path.connections}")

    print(f"\nUSB_DP signal paths: {len(usb_paths)}")


def example_complete_workflow():
    """Example: Complete workflow with all features."""
    print("\n=== Example 8: Complete Workflow ===")

    # 1. Create hierarchical design
    root = ksa.create_schematic("CompleteExample")
    root.components.add("Device:R", "R1", "10k", (100, 100))

    # 2. Add sheets
    power_sheet = root.sheets.add_sheet(
        "Power",
        "power.kicad_sch",
        (200, 100),
        (50, 50),
    )
    root.sheets.add_sheet_pin(power_sheet, "VCC", "output", "right", 10)
    root.sheets.add_sheet_pin(power_sheet, "GND", "output", "right", 20)

    # 3. Build hierarchy tree
    tree = root.hierarchy.build_hierarchy_tree(root)
    print("✓ Hierarchy tree built")

    # 4. Find reused sheets
    reused = root.hierarchy.find_reused_sheets()
    print(f"✓ Found {len(reused)} reused sheets")

    # 5. Validate sheet pins
    connections = root.hierarchy.validate_sheet_pins()
    print(f"✓ Validated {len(connections)} sheet pin connections")

    # 6. Get statistics
    stats = root.hierarchy.get_hierarchy_statistics()
    print(f"✓ Statistics: {stats['total_sheets']} sheets, {stats['total_components']} components")

    # 7. Flatten hierarchy
    flattened = root.hierarchy.flatten_hierarchy(prefix_references=True)
    print(f"✓ Flattened to {len(flattened['components'])} components")

    # 8. Visualize
    viz = root.hierarchy.visualize_hierarchy(include_stats=True)
    print("✓ Hierarchy visualization created")

    print("\nAll hierarchy features demonstrated successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("Advanced Hierarchy Management Examples")
    print("=" * 60)

    example_basic_hierarchy_tree()
    example_reusable_sheets()
    example_sheet_pin_validation()
    example_hierarchy_flattening()
    example_hierarchy_statistics()
    example_hierarchy_visualization()
    example_signal_tracing()
    example_complete_workflow()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
