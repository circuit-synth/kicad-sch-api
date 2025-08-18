#!/usr/bin/env python3
"""
Basic test of MCP server functionality
"""

from kicad_sch_api.mcp.server import (
    create_schematic, get_schematic_info, add_component, 
    list_components, state
)

def test_basic_functionality():
    """Test basic MCP server functions."""
    print("Testing MCP server functionality...")
    
    # Test creating a schematic
    print("\n1. Testing create_schematic...")
    result = create_schematic("Test Circuit")
    print(f"Result: {result}")
    
    # Test getting info
    print("\n2. Testing get_schematic_info...")
    result = get_schematic_info()
    print(f"Result: {result}")
    
    # Test adding a component
    print("\n3. Testing add_component...")
    result = add_component(
        lib_id="Device:R",
        reference="R1", 
        value="10k",
        position=(100.0, 100.0)
    )
    print(f"Result: {result}")
    
    # Test listing components
    print("\n4. Testing list_components...")
    result = list_components()
    print(f"Result: {result}")
    
    print("\n✅ Basic functionality test complete!")

if __name__ == "__main__":
    test_basic_functionality()