#!/usr/bin/env python3
"""
Debug property parsing to see what sexpdata returns.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import sexpdata

def main():
    ref_path = Path(__file__).parent / "tests/reference_tests/reference_kicad_projects/resistor_divider/resistor_divider.kicad_sch"
    
    with open(ref_path, 'r') as f:
        content = f.read()
    
    # Parse with sexpdata
    parsed = sexpdata.loads(content)
    
    # Find properties with "Power symbol" in description
    def find_power_properties(obj, depth=0):
        if isinstance(obj, list):
            if len(obj) >= 3 and str(obj[0]) == "property" and "Power symbol" in str(obj[2]):
                print(f"Found property at depth {depth}:")
                print(f"  Raw list: {obj}")
                print(f"  Length: {len(obj)}")
                for i, item in enumerate(obj):
                    print(f"    [{i}]: {repr(item)} (type: {type(item)})")
                print()
            
            for item in obj:
                find_power_properties(item, depth + 1)
    
    find_power_properties(parsed)

if __name__ == "__main__":
    main()