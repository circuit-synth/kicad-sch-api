#!/usr/bin/env python3
"""
Test pure load + save roundtrip to see if format is preserved.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api.core.schematic import Schematic

def test_pure_roundtrip():
    print("🔄 Testing pure load + save roundtrip...")
    
    # Load reference
    ref_path = Path(__file__).parent / "tests/reference_tests/reference_kicad_projects/blank_schematic/blank_schematic.kicad_sch"
    sch = Schematic.load(str(ref_path))
    
    # Save immediately without any changes
    with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
        temp_path = f.name
    
    sch.save(temp_path, preserve_format=True)
    
    # Compare files
    import filecmp
    identical = filecmp.cmp(ref_path, temp_path, shallow=False)
    
    print(f"  Files identical: {identical}")
    
    if not identical:
        print("  ❌ Even pure load+save doesn't preserve format!")
        
        # Show the difference
        with open(ref_path, 'r') as f:
            ref_content = f.read()
        with open(temp_path, 'r') as f:
            temp_content = f.read()
        
        print(f"  Reference: {len(ref_content.splitlines())} lines")
        print(f"  Saved: {len(temp_content.splitlines())} lines")
        
        print(f"  Reference preview:")
        for i, line in enumerate(ref_content.splitlines()[:5]):
            print(f"    {i+1}: {repr(line)}")
        
        print(f"  Saved preview:")
        for i, line in enumerate(temp_content.splitlines()[:5]):
            print(f"    {i+1}: {repr(line)}")
    else:
        print("  ✅ Pure load+save preserves format exactly!")
    
    # Clean up
    Path(temp_path).unlink()
    
    return identical

if __name__ == "__main__":
    test_pure_roundtrip()