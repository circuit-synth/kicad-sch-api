#!/usr/bin/env python3
"""
Debug script to examine recreated resistor divider properties.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api.core.schematic import Schematic

def recreate_schematic_from_reference(ref_sch, project_name):
    """Recreate a schematic by copying all components from reference."""
    recreated_sch = Schematic.create(project_name)
    
    # Copy all components exactly
    for ref_comp in ref_sch.components:
        print(f"Recreating {ref_comp.reference}...")
        
        new_comp = recreated_sch.components.add(
            lib_id=ref_comp.lib_id,
            reference=ref_comp.reference,
            value=ref_comp.value,
            position=(ref_comp.position.x, ref_comp.position.y),
            footprint=ref_comp.footprint
        )
        
        # Copy all properties
        for prop_name, prop_value in ref_comp.properties.items():
            print(f"  Setting {prop_name} = '{prop_value}'")
            new_comp.set_property(prop_name, prop_value)
            
            # Check what was actually set
            actual_value = new_comp.get_property(prop_name)
            print(f"    Got back: '{actual_value}'")
            if str(actual_value) != str(prop_value):
                print(f"    *** MISMATCH! Expected: '{prop_value}', Got: '{actual_value}'")
    
    return recreated_sch

def main():
    print("Loading resistor divider schematic...")
    
    ref_path = Path(__file__).parent / "tests/reference_tests/reference_kicad_projects/resistor_divider/resistor_divider.kicad_sch"
    ref_sch = Schematic.load(str(ref_path))
    
    print("\n=== Recreating schematic ===")
    recreated_sch = recreate_schematic_from_reference(ref_sch, "debug_recreated")
    
    print("\n=== Saving and reloading ===")
    with tempfile.NamedTemporaryFile(suffix='.kicad_sch', delete=False) as f:
        temp_path = f.name
    
    recreated_sch.save(temp_path)
    saved_sch = Schematic.load(temp_path)
    
    print(f"\n=== Final comparison ===")
    for ref_comp in ref_sch.components:
        saved_comp = saved_sch.components.get(ref_comp.reference)
        if saved_comp:
            print(f"\n{ref_comp.reference}:")
            print(f"  Footprint: '{ref_comp.footprint}' vs '{saved_comp.footprint}'")
            
            for prop_name in ref_comp.properties:
                ref_val = ref_comp.get_property(prop_name)
                saved_val = saved_comp.get_property(prop_name)
                if ref_val != saved_val:
                    print(f"  Property {prop_name}: MISMATCH")
                    print(f"    Expected: '{ref_val}' (len: {len(str(ref_val))})")
                    print(f"    Got:      '{saved_val}' (len: {len(str(saved_val))})")
                    print(f"    Expected repr: {repr(ref_val)}")
                    print(f"    Got repr:      {repr(saved_val)}")
                else:
                    print(f"  Property {prop_name}: OK")
    
    # Cleanup
    Path(temp_path).unlink()

if __name__ == "__main__":
    main()