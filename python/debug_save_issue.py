#!/usr/bin/env python3
"""
Debug the exact save issue causing property truncation.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api.core.schematic import Schematic
import sexpdata

def main():
    print("=== Creating test schematic ===")
    sch = Schematic.create("debug_save")
    
    # Add a power symbol with problematic description
    power_comp = sch.components.add(
        lib_id="power:+3.3V",
        reference="#PWR01",
        value="+3.3V",
        position=(91.44, 69.85),
        footprint=""  # Explicitly set empty string
    )
    
    # Set the problematic description
    test_desc = 'Power symbol creates a global label with name "+3.3V"'
    power_comp.set_property("Description", test_desc)
    
    print(f"Set description: '{test_desc}' (length: {len(test_desc)})")
    retrieved_desc = power_comp.get_property("Description")
    print(f"Retrieved back: '{retrieved_desc}' (length: {len(retrieved_desc)})")
    
    print(f"Footprint set to: '{power_comp.footprint}' (type: {type(power_comp.footprint)})")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.kicad_sch', delete=False) as f:
        temp_path = f.name
    
    print(f"\n=== Saving to {temp_path} ===")
    sch.save(temp_path)
    
    # Check what was actually written to file
    print("\n=== Raw file content ===")
    with open(temp_path, 'r') as f:
        content = f.read()
    
    # Find the Description property line
    for line_num, line in enumerate(content.splitlines(), 1):
        if 'Description' in line and 'Power symbol' in line:
            print(f"Line {line_num}: {line}")
            print(f"Line length: {len(line)}")
    
    # Parse the saved file with sexpdata to see what we get
    print("\n=== Parsing saved file with sexpdata ===")
    parsed = sexpdata.loads(content)
    
    def find_desc_properties(obj):
        if isinstance(obj, list):
            if len(obj) >= 3 and str(obj[0]) == "property" and obj[1] == "Description":
                print(f"Found Description property: {obj[2]} (length: {len(str(obj[2]))})")
            for item in obj:
                find_desc_properties(item)
    
    find_desc_properties(parsed)
    
    # Now load it back
    print(f"\n=== Loading back from {temp_path} ===")
    loaded_sch = Schematic.load(temp_path)
    
    loaded_comp = loaded_sch.components.get("#PWR01")
    if loaded_comp:
        loaded_desc = loaded_comp.get_property("Description")
        loaded_footprint = loaded_comp.footprint
        print(f"Loaded description: '{loaded_desc}' (length: {len(loaded_desc)})")
        print(f"Loaded footprint: '{loaded_footprint}' (type: {type(loaded_footprint)})")
        
        if loaded_desc != test_desc:
            print(f"*** DESCRIPTION MISMATCH! ***")
            print(f"Expected: '{test_desc}'")
            print(f"Got:      '{loaded_desc}'")
            
        if str(loaded_footprint) != "":
            print(f"*** FOOTPRINT MISMATCH! ***")
            print(f"Expected: ''")
            print(f"Got:      '{loaded_footprint}'")
    
    # Clean up
    Path(temp_path).unlink()

if __name__ == "__main__":
    main()