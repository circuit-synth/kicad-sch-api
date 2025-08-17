#!/usr/bin/env python3
"""Simple test: Create a new schematic and add a resistor."""

import logging
import kicad_sch_api as ksa

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

def main():
    """Create a new schematic and add a resistor."""
    print("🔧 DEBUG: Creating new schematic...")
    
    # Create a new schematic
    sch = ksa.create_schematic("Simple Circuit")
    print(f"✅ Created schematic: {sch.title_block.get('title', 'Untitled')}")
    print(f"🔧 DEBUG: Initial data keys: {list(sch._data.keys())}")
    
    print(f"🔧 DEBUG: Adding resistor...")
    
    # Add a resistor
    resistor = sch.components.add(
        lib_id="Device:R",
        reference="R1", 
        value="10k",
        position=(100, 100)
    )
    
    print(f"✅ Added {resistor.reference}: {resistor.value} at {resistor.position}")
    print(f"🔧 DEBUG: Resistor lib_id: {resistor.lib_id}")
    print(f"🔧 DEBUG: Resistor pins: {len(resistor.pins)} pins")
    print(f"🔧 DEBUG: Component collection size: {len(sch.components)}")
    
    # Debug schematic data structure
    print(f"🔧 DEBUG: Schematic data keys: {list(sch._data.keys())}")
    print(f"🔧 DEBUG: Components in data: {len(sch._data.get('components', []))}")
    print(f"🔧 DEBUG: Lib_symbols keys: {list(sch._data.get('lib_symbols', {}).keys())}")
    
    # Trigger the sync manually for debugging
    sch._sync_components_to_data()
    print(f"🔧 DEBUG: After sync - Components in data: {len(sch._data.get('components', []))}")
    print(f"🔧 DEBUG: After sync - Lib_symbols keys: {list(sch._data.get('lib_symbols', {}).keys())}")
    
    # Check what the lib_symbols actually contains
    if sch._data.get('lib_symbols'):
        for lib_id, lib_data in sch._data['lib_symbols'].items():
            print(f"🔧 DEBUG: Lib_symbols[{lib_id}] type: {type(lib_data)}")
            if isinstance(lib_data, list):
                print(f"🔧 DEBUG: Lib_symbols[{lib_id}] length: {len(lib_data)}")
                print(f"🔧 DEBUG: Lib_symbols[{lib_id}] first few items: {lib_data[:3] if len(lib_data) > 3 else lib_data}")
    
    # Save the schematic
    output_file = "simple_circuit.kicad_sch"
    print(f"🔧 DEBUG: Saving to {output_file}...")
    sch.save(output_file)
    print(f"✅ Saved schematic to {output_file}")
    
    # Debug what was actually written
    with open(output_file, 'r') as f:
        content = f.read()
        print(f"🔧 DEBUG: File size: {len(content)} bytes")
        print(f"🔧 DEBUG: First 500 characters:")
        print(content[:500])


if __name__ == "__main__":
    main()
