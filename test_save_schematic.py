#!/usr/bin/env python3
"""
Test saving a schematic file through MCP
"""

from kicad_sch_api.mcp.server import (
    create_schematic, add_component, add_wire, 
    save_schematic, list_components
)

def test_save_schematic():
    """Test creating and saving a complete schematic."""
    print("Testing MCP schematic creation and saving...")
    
    # 1. Create a new schematic
    print("\n1. Creating schematic...")
    result = create_schematic("Power Supply")
    print(f"✅ {result['message']}")
    
    # 2. Add components
    print("\n2. Adding voltage regulator...")
    result = add_component(
        lib_id="Regulator_Linear:AMS1117-3.3",
        reference="U1",
        value="AMS1117-3.3",
        position=(100.0, 100.0),
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )
    print(f"✅ {result['message']}")
    
    print("\n3. Adding input capacitor...")
    result = add_component(
        lib_id="Device:C",
        reference="C1",
        value="10uF",
        position=(75.0, 110.0),
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    print(f"✅ {result['message']}")
    
    print("\n4. Adding output capacitor...")
    result = add_component(
        lib_id="Device:C",
        reference="C2", 
        value="22uF",
        position=(125.0, 110.0),
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    print(f"✅ {result['message']}")
    
    # 3. Add wire connections
    print("\n5. Adding wire connections...")
    result = add_wire(
        start_pos=(75.0, 100.0),
        end_pos=(92.0, 100.0)  # To U1 input
    )
    print(f"✅ Added input wire")
    
    result = add_wire(
        start_pos=(108.0, 100.0),  # From U1 output
        end_pos=(125.0, 100.0)
    )
    print(f"✅ Added output wire")
    
    # 4. List all components
    print("\n6. Listing all components...")
    result = list_components()
    print(f"✅ Found {result['count']} components:")
    for comp in result['components']:
        print(f"   - {comp['reference']}: {comp['lib_id']} = {comp['value']}")
    
    # 5. Save the schematic
    print("\n7. Saving schematic...")
    result = save_schematic("test_power_supply.kicad_sch")
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   Saved to: {result['file_path']}")
        
        # Verify file exists
        import os
        if os.path.exists("test_power_supply.kicad_sch"):
            file_size = os.path.getsize("test_power_supply.kicad_sch")
            print(f"   File size: {file_size} bytes")
            print("✅ File saved successfully!")
        else:
            print("❌ File not found on disk")
    else:
        print(f"❌ Save failed: {result['message']}")

if __name__ == "__main__":
    test_save_schematic()