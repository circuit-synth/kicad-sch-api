"""
Generate manual test schematics for collection architecture validation.

This script creates several test schematics using the new collection
architecture to verify correct KiCad rendering and format preservation.
"""

import sys
sys.path.insert(0, '/Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-schematic')

import kicad_sch_api as ksa

def test_1_basic_components():
    """Test 1: Basic component creation using ComponentCollection."""
    print("Creating Test 1: Basic Components...")
    
    sch = ksa.create_schematic("Manual_Test_1_Components")
    
    # Add various components using new ComponentCollection API
    sch.components.add("Device:R", "R1", "10k", position=(100, 100))
    sch.components.add("Device:R", "R2", "1k", position=(100, 120))
    sch.components.add("Device:C", "C1", "100nF", position=(130, 100))
    sch.components.add("Device:LED", "D1", "RED", position=(130, 120))
    
    # Test get() method (new API)
    r1 = sch.components.get("R1")
    print(f"  Retrieved R1: {r1.reference} = {r1.value}")
    
    # Test filter() method (new API)
    resistors = sch.components.filter(lib_id="Device:R")
    print(f"  Found {len(resistors)} resistors via filter()")
    
    sch.save("manual_tests/test_1_basic_components.kicad_sch")
    print("  ✓ Saved test_1_basic_components.kicad_sch\n")
    return sch

def test_2_labels():
    """Test 2: Label creation using LabelCollection."""
    print("Creating Test 2: Labels...")
    
    sch = ksa.create_schematic("Manual_Test_2_Labels")
    
    # Add labels using new LabelCollection API (returns LabelElement)
    label1 = sch.labels.add("VCC", position=(100, 100))
    label2 = sch.labels.add("GND", position=(100, 120))
    label3 = sch.labels.add("SIGNAL", position=(100, 140))
    
    print(f"  Added label: {label1.text} at {label1.position}")
    print(f"  Added label: {label2.text} at {label2.position}")
    
    # Test get_by_text() method
    vcc_labels = sch.labels.get_by_text("VCC")
    print(f"  Found {len(vcc_labels)} VCC labels")
    
    sch.save("manual_tests/test_2_labels.kicad_sch")
    print("  ✓ Saved test_2_labels.kicad_sch\n")
    return sch

def test_3_wires_and_junctions():
    """Test 3: Wires and junctions using new collections."""
    print("Creating Test 3: Wires and Junctions...")
    
    sch = ksa.create_schematic("Manual_Test_3_Wires")
    
    # Add components
    sch.components.add("Device:R", "R1", "10k", position=(100, 100))
    sch.components.add("Device:R", "R2", "10k", position=(150, 100))
    
    # Add wires using WireCollection
    wire1 = sch.wires.add(start=(110, 100), end=(130, 100))
    wire2 = sch.wires.add(start=(130, 100), end=(140, 100))
    print(f"  Added {len(sch.wires)} wires")
    
    # Add junction at wire intersection
    junction = sch.junctions.add(position=(130, 100))
    print(f"  Added junction at (130, 100)")
    
    # Add label
    sch.labels.add("NET1", position=(125, 95))
    
    sch.save("manual_tests/test_3_wires_and_junctions.kicad_sch")
    print("  ✓ Saved test_3_wires_and_junctions.kicad_sch\n")
    return sch

def test_4_batch_mode():
    """Test 4: Batch mode performance test."""
    print("Creating Test 4: Batch Mode (50 components)...")
    
    sch = ksa.create_schematic("Manual_Test_4_Batch")
    
    # Use batch mode for bulk operations (100× speedup)
    import time
    start = time.time()
    
    with sch.components.batch_mode():
        for i in range(50):
            x = 100 + (i % 10) * 15
            y = 100 + (i // 10) * 15
            sch.components.add("Device:R", f"R{i+1}", "10k", position=(x, y))
    
    elapsed = time.time() - start
    print(f"  Added 50 components in {elapsed:.3f}s using batch mode")
    print(f"  Total components: {len(sch.components)}")
    
    sch.save("manual_tests/test_4_batch_mode.kicad_sch")
    print("  ✓ Saved test_4_batch_mode.kicad_sch\n")
    return sch

def test_5_complex_circuit():
    """Test 5: Complex circuit with mixed elements."""
    print("Creating Test 5: Complex Circuit...")
    
    sch = ksa.create_schematic("Manual_Test_5_Complex")
    
    # Add various components
    sch.components.add("Device:R", "R1", "10k", position=(100, 100))
    sch.components.add("Device:R", "R2", "10k", position=(150, 100))
    sch.components.add("Device:C", "C1", "100nF", position=(125, 120))
    sch.components.add("Device:LED", "D1", "RED", position=(175, 100))
    
    # Add wires
    sch.wires.add(start=(110, 100), end=(125, 100))
    sch.wires.add(start=(125, 100), end=(140, 100))
    sch.wires.add(start=(125, 100), end=(125, 110))
    sch.wires.add(start=(160, 100), end=(165, 100))
    
    # Add junctions
    sch.junctions.add(position=(125, 100))
    
    # Add labels
    sch.labels.add("VCC", position=(100, 90))
    sch.labels.add("OUT", position=(160, 90))
    sch.labels.add("GND", position=(125, 130))
    
    # Test filtering
    resistors = sch.components.filter(lib_id="Device:R")
    print(f"  Added {len(resistors)} resistors")
    print(f"  Total wires: {len(sch.wires)}")
    print(f"  Total labels: {len(sch.labels)}")
    
    sch.save("manual_tests/test_5_complex_circuit.kicad_sch")
    print("  ✓ Saved test_5_complex_circuit.kicad_sch\n")
    return sch

def test_6_filter_operations():
    """Test 6: Filter operations and queries."""
    print("Creating Test 6: Filter Operations...")
    
    sch = ksa.create_schematic("Manual_Test_6_Filters")
    
    # Add components with different values
    sch.components.add("Device:R", "R1", "10k", position=(100, 100))
    sch.components.add("Device:R", "R2", "10k", position=(120, 100))
    sch.components.add("Device:R", "R3", "1k", position=(140, 100))
    sch.components.add("Device:C", "C1", "100nF", position=(100, 120))
    sch.components.add("Device:C", "C2", "10uF", position=(120, 120))
    
    # Test filter operations
    resistors = sch.components.filter(lib_id="Device:R")
    print(f"  Filter by lib_id='Device:R': {len(resistors)} components")
    
    ten_k = sch.components.filter(value="10k")
    print(f"  Filter by value='10k': {len(ten_k)} components")
    
    capacitors = sch.components.filter(lib_id="Device:C")
    print(f"  Filter by lib_id='Device:C': {len(capacitors)} components")
    
    # Add labels for each component type
    sch.labels.add("RESISTORS", position=(100, 90))
    sch.labels.add("CAPACITORS", position=(100, 110))
    
    sch.save("manual_tests/test_6_filter_operations.kicad_sch")
    print("  ✓ Saved test_6_filter_operations.kicad_sch\n")
    return sch

if __name__ == "__main__":
    print("=" * 60)
    print("Manual Test Schematic Generation")
    print("Testing New Collection Architecture")
    print("=" * 60)
    print()
    
    # Generate all test schematics
    test_1_basic_components()
    test_2_labels()
    test_3_wires_and_junctions()
    test_4_batch_mode()
    test_5_complex_circuit()
    test_6_filter_operations()
    
    print("=" * 60)
    print("All test schematics generated successfully!")
    print("=" * 60)
    print()
    print("Files created in manual_tests/:")
    print("  1. test_1_basic_components.kicad_sch")
    print("  2. test_2_labels.kicad_sch")
    print("  3. test_3_wires_and_junctions.kicad_sch")
    print("  4. test_4_batch_mode.kicad_sch")
    print("  5. test_5_complex_circuit.kicad_sch")
    print("  6. test_6_filter_operations.kicad_sch")
    print()
    print("Ready for manual inspection in KiCad!")
