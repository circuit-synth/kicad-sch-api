#!/usr/bin/env python3
"""
Basic MCP Server Usage Example

Shows how to use the KiCAD Schematic MCP server for AI-driven circuit creation.
"""

def main():
    """Example of operations available through MCP server."""
    
    print("KiCAD Schematic MCP Server - Basic Usage")
    print("=" * 50)
    
    print("\n1. Create a new schematic:")
    print("   create_schematic(name='My Circuit')")
    
    print("\n2. Add components:")
    print("   add_component(lib_id='Device:R', reference='R1', value='10k', position=(100, 100))")
    print("   add_component(lib_id='Device:C', reference='C1', value='0.1uF', position=(150, 100))")
    
    print("\n3. Add wire connections:")
    print("   add_wire(start_pos=(100, 90), end_pos=(150, 90))")
    
    print("\n4. List components:")
    print("   list_components()")
    
    print("\n5. Get schematic info:")
    print("   get_schematic_info()")
    
    print("\n6. Save schematic:")
    print("   save_schematic(file_path='my_circuit.kicad_sch')")
    
    print("\n7. Load existing schematic:")
    print("   load_schematic(file_path='existing_circuit.kicad_sch')")
    
    print("\nAI Usage Example:")
    print("'Create a new schematic called Power Supply, add a voltage regulator")
    print("and some decoupling capacitors, then save it as power_supply.kicad_sch'")

if __name__ == "__main__":
    main()