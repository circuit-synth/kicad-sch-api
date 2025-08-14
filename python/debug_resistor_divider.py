#!/usr/bin/env python3
"""
Debug script to examine resistor divider power symbol properties.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api.core.schematic import Schematic

def main():
    print("Loading resistor divider schematic...")
    
    ref_path = Path(__file__).parent / "tests/reference_tests/reference_kicad_projects/resistor_divider/resistor_divider.kicad_sch"
    ref_sch = Schematic.load(str(ref_path))
    
    print(f"Found {len(ref_sch.components)} components:")
    
    for comp in ref_sch.components:
        print(f"\n--- {comp.reference} ({comp.lib_id}) ---")
        print(f"Value: '{comp.value}'")
        print(f"Footprint: '{comp.footprint}' (type: {type(comp.footprint)})")
        print(f"Position: ({comp.position.x}, {comp.position.y})")
        print(f"Properties ({len(comp.properties)}):")
        for prop_name, prop_value in comp.properties.items():
            print(f"  {prop_name}: '{prop_value}' (len: {len(str(prop_value))})")
            if prop_name == 'Description':
                print(f"    Raw repr: {repr(prop_value)}")

if __name__ == "__main__":
    main()