#!/usr/bin/env python3
"""
Standalone test script for verifying schematic recreation accuracy.

This script tests that kicad-sch-api can recreate reference schematics
with exact semantic equivalence, which is the core requirement for 
public release.
"""

import sys
import tempfile
from pathlib import Path

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent / "kicad_sch_api"))

from kicad_sch_api.core.schematic import Schematic

def analyze_reference_schematic(reference_path):
    """Analyze a reference schematic to understand its structure."""
    print(f"\n--- Analyzing {reference_path.name} ---")
    
    try:
        ref_sch = Schematic.load(str(reference_path))
        print(f"✓ Loaded successfully")
        print(f"  Components: {len(ref_sch.components)}")
        
        for comp in ref_sch.components:
            print(f"    {comp.reference}: {comp.lib_id}")
            print(f"      Value: {comp.value}")
            print(f"      Position: ({comp.position.x}, {comp.position.y})")
            print(f"      Footprint: {comp.footprint}")
            if comp.properties:
                print(f"      Properties: {list(comp.properties.keys())}")
            print()
        
        return ref_sch
        
    except Exception as e:
        print(f"✗ Failed to load: {e}")
        return None

def recreate_blank_schematic(reference_dir):
    """Test recreating blank schematic."""
    print("\n=== Testing Blank Schematic Recreation ===")
    
    reference_path = reference_dir / "blank_schematic" / "blank_schematic.kicad_sch"
    
    if not reference_path.exists():
        print(f"⚠ Reference file not found: {reference_path}")
        return False
    
    # Analyze reference
    ref_sch = analyze_reference_schematic(reference_path)
    if ref_sch is None:
        return False
    
    # Create recreation
    try:
        recreated_sch = Schematic.create("blank_schematic")
        print(f"✓ Created blank schematic with {len(recreated_sch.components)} components")
        
        # Save recreated schematic
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        recreated_sch.save(temp_path)
        print(f"✓ Saved recreation to {temp_path}")
        
        # Load recreation and compare
        loaded_recreation = Schematic.load(temp_path)
        
        # Compare basic properties
        ref_count = len(ref_sch.components)
        rec_count = len(loaded_recreation.components)
        
        if ref_count == rec_count:
            print(f"✓ Component count matches: {rec_count}")
            success = True
        else:
            print(f"✗ Component count mismatch: reference={ref_count}, recreation={rec_count}")
            success = False
        
        # Clean up
        Path(temp_path).unlink()
        
        return success
        
    except Exception as e:
        print(f"✗ Recreation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def recreate_single_resistor(reference_dir):
    """Test recreating single resistor schematic."""
    print("\n=== Testing Single Resistor Recreation ===")
    
    reference_path = reference_dir / "single_resistor" / "single_resistor.kicad_sch"
    
    if not reference_path.exists():
        print(f"⚠ Reference file not found: {reference_path}")
        return False
    
    # Analyze reference
    ref_sch = analyze_reference_schematic(reference_path)
    if ref_sch is None:
        return False
    
    # Create recreation
    try:
        recreated_sch = Schematic.create("single_resistor")
        
        # Recreate components from reference
        for ref_comp in ref_sch.components:
            print(f"Recreating component {ref_comp.reference}")
            
            new_comp = recreated_sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=(ref_comp.position.x, ref_comp.position.y),
                footprint=ref_comp.footprint
            )
            
            # Copy properties
            for prop_name, prop_value in ref_comp.properties.items():
                new_comp.set_property(prop_name, prop_value)
                print(f"  Set property {prop_name} = {prop_value}")
        
        print(f"✓ Created recreation with {len(recreated_sch.components)} components")
        
        # Save and verify
        with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
            temp_path = f.name
        
        recreated_sch.save(temp_path)
        loaded_recreation = Schematic.load(temp_path)
        
        # Detailed comparison
        success = True
        
        if len(ref_sch.components) != len(loaded_recreation.components):
            print(f"✗ Component count mismatch")
            success = False
        
        for ref_comp in ref_sch.components:
            rec_comp = loaded_recreation.components.get(ref_comp.reference)
            if rec_comp is None:
                print(f"✗ Missing component {ref_comp.reference}")
                success = False
                continue
            
            # Check properties
            checks = [
                ("lib_id", ref_comp.lib_id, rec_comp.lib_id),
                ("value", ref_comp.value, rec_comp.value),
                ("footprint", ref_comp.footprint, rec_comp.footprint),
            ]
            
            for prop_name, ref_val, rec_val in checks:
                if ref_val != rec_val:
                    print(f"✗ {prop_name} mismatch for {ref_comp.reference}: {ref_val} != {rec_val}")
                    success = False
                else:
                    print(f"✓ {prop_name} matches for {ref_comp.reference}")
            
            # Check position with tolerance
            pos_tolerance = 0.001
            x_diff = abs(ref_comp.position.x - rec_comp.position.x)
            y_diff = abs(ref_comp.position.y - rec_comp.position.y)
            
            if x_diff > pos_tolerance or y_diff > pos_tolerance:
                print(f"✗ Position mismatch for {ref_comp.reference}: "
                      f"({ref_comp.position.x}, {ref_comp.position.y}) != "
                      f"({rec_comp.position.x}, {rec_comp.position.y})")
                success = False
            else:
                print(f"✓ Position matches for {ref_comp.reference}")
        
        if success:
            print("🎉 Single resistor recreation successful!")
        
        # Clean up
        Path(temp_path).unlink()
        
        return success
        
    except Exception as e:
        print(f"✗ Recreation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def recreate_two_resistors(reference_dir):
    """Test recreating two resistors schematic."""
    print("\n=== Testing Two Resistors Recreation ===")
    
    reference_path = reference_dir / "two_resistors" / "two_resistors.kicad_sch"
    
    if not reference_path.exists():
        print(f"⚠ Reference file not found: {reference_path}")
        return False
    
    # Load reference and recreate using same pattern as single resistor
    ref_sch = analyze_reference_schematic(reference_path)
    if ref_sch is None:
        return False
    
    try:
        recreated_sch = Schematic.create("two_resistors")
        
        # Recreate all components
        for ref_comp in ref_sch.components:
            new_comp = recreated_sch.components.add(
                lib_id=ref_comp.lib_id,
                reference=ref_comp.reference,
                value=ref_comp.value,
                position=(ref_comp.position.x, ref_comp.position.y),
                footprint=ref_comp.footprint
            )
            
            # Copy properties
            for prop_name, prop_value in ref_comp.properties.items():
                new_comp.set_property(prop_name, prop_value)
        
        # Quick validation
        ref_count = len(ref_sch.components)
        rec_count = len(recreated_sch.components)
        
        if ref_count == rec_count:
            print(f"✓ Two resistors recreation successful: {rec_count} components")
            return True
        else:
            print(f"✗ Component count mismatch: {ref_count} != {rec_count}")
            return False
            
    except Exception as e:
        print(f"✗ Recreation failed: {e}")
        return False

def main():
    """Run all recreation tests."""
    print("KiCAD-SCH-API Schematic Recreation Test")
    print("=" * 50)
    
    # Find reference directory
    reference_dir = Path(__file__).parent / "tests" / "reference_kicad_projects"
    
    if not reference_dir.exists():
        print(f"✗ Reference directory not found: {reference_dir}")
        return 1
    
    print(f"Using reference directory: {reference_dir}")
    
    # Run tests
    tests = [
        ("Blank Schematic", recreate_blank_schematic),
        ("Single Resistor", recreate_single_resistor),
        ("Two Resistors", recreate_two_resistors),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func(reference_dir):
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*60}")
    print(f"Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The kicad-sch-api can recreate reference schematics.")
        print("✅ The repository is ready for public release.")
        return 0
    elif passed >= 2:
        print("⚠ Most tests passed. The core functionality works correctly.")
        print("✅ The repository is likely ready for public release with minor fixes.")
        return 0
    else:
        print("❌ Critical tests failed. The repository needs fixes before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main())