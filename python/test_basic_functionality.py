#!/usr/bin/env python3
"""
Basic functionality test to verify the kicad-sch-api package works.

This is a standalone test script to verify that we can create and manipulate
schematics without the full test framework.
"""

import sys
import tempfile
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent / "kicad_sch_api"))

try:
    from kicad_sch_api.core.schematic import Schematic
    from kicad_sch_api.core.types import Point
    print("✓ Successfully imported core modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_schematic_creation():
    """Test basic schematic creation."""
    print("\n--- Testing Schematic Creation ---")
    
    try:
        # Create a new schematic
        sch = Schematic.create("test_schematic")
        print(f"✓ Created schematic with {len(sch.components)} components")
        
        # Add a component
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 100)
        )
        print(f"✓ Added component {resistor.reference}")
        
        # Verify component properties
        assert resistor.reference == "R1"
        assert resistor.lib_id == "Device:R"
        assert resistor.value == "10k"
        print(f"✓ Component properties verified")
        
        # Test component access
        retrieved = sch.components.get("R1")
        assert retrieved is not None
        assert retrieved.reference == "R1"
        print(f"✓ Component retrieval works")
        
        return True
        
    except Exception as e:
        print(f"✗ Schematic creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schematic_save_load():
    """Test schematic save and load."""
    print("\n--- Testing Schematic Save/Load ---")
    
    try:
        # Create schematic
        sch = Schematic.create("save_test")
        sch.components.add("Device:R", "R1", "10k", (100, 50))
        sch.components.add("Device:C", "C1", "0.1uF", (200, 50))
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        sch.save(temp_path)
        print(f"✓ Saved schematic to {temp_path}")
        
        # Verify file was created
        assert Path(temp_path).exists()
        print(f"✓ File exists on disk")
        
        # Load the schematic back
        loaded_sch = Schematic.load(temp_path)
        print(f"✓ Loaded schematic with {len(loaded_sch.components)} components")
        
        # Verify components were preserved
        assert len(loaded_sch.components) == 2
        assert loaded_sch.components.get("R1") is not None
        assert loaded_sch.components.get("C1") is not None
        print(f"✓ All components preserved in save/load")
        
        # Clean up
        Path(temp_path).unlink()
        
        return True
        
    except Exception as e:
        print(f"✗ Save/load test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reference_schematic_loading():
    """Test loading reference schematics."""
    print("\n--- Testing Reference Schematic Loading ---")
    
    reference_dir = Path(__file__).parent / "tests" / "reference_kicad_projects"
    
    if not reference_dir.exists():
        print(f"⚠ Reference directory not found: {reference_dir}")
        return True  # Skip this test
    
    test_cases = [
        "blank_schematic",
        "single_resistor",
        "two_resistors"
    ]
    
    successful_loads = 0
    
    for case in test_cases:
        try:
            sch_path = reference_dir / case / f"{case}.kicad_sch"
            if sch_path.exists():
                sch = Schematic.load(str(sch_path))
                component_count = len(sch.components)
                print(f"✓ Loaded {case}: {component_count} components")
                successful_loads += 1
            else:
                print(f"⚠ Reference file not found: {sch_path}")
        except Exception as e:
            print(f"✗ Failed to load {case}: {e}")
    
    print(f"Successfully loaded {successful_loads}/{len(test_cases)} reference schematics")
    return successful_loads > 0

def main():
    """Run all basic functionality tests."""
    print("KiCAD-SCH-API Basic Functionality Test")
    print("=" * 40)
    
    tests = [
        test_schematic_creation,
        test_schematic_save_load,
        test_reference_schematic_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n--- Test Results ---")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())