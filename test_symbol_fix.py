#!/usr/bin/env python3
"""
Test the symbol definition fix.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "python"))

from kicad_sch_api.core.schematic import Schematic

def test_symbol_definitions():
    print("🔧 Testing symbol definition generation...")
    
    # Create schematic with components
    sch = Schematic.create("Symbol Test")
    
    # Add components
    resistor = sch.components.add('Device:R', reference='R1', value='10k', position=(100, 100))
    capacitor = sch.components.add('Device:C', reference='C1', value='0.1uF', position=(150, 100))
    
    # Save the schematic
    sch.save('symbol_test_fixed.kicad_sch')
    
    # Check the lib_symbols section
    with open('symbol_test_fixed.kicad_sch', 'r') as f:
        content = f.read()
    
    print("📋 Generated schematic analysis:")
    print(f"  Contains (lib_symbols): {'(lib_symbols' in content}")
    device_r_def = '(symbol "Device:R"'
    device_c_def = '(symbol "Device:C"'
    print(f"  Contains Device:R definition: {device_r_def in content}")
    print(f"  Contains Device:C definition: {device_c_def in content}")
    
    # Count lines in lib_symbols section
    lines = content.split('\n')
    lib_symbols_lines = []
    in_lib_symbols = False
    
    for line in lines:
        if '(lib_symbols' in line:
            in_lib_symbols = True
            lib_symbols_lines.append(line)
        elif in_lib_symbols:
            lib_symbols_lines.append(line)
            # Look for the closing paren at the right indentation level
            if line.strip() == ')' and not line.startswith('\t\t'):
                break
    
    print(f"  lib_symbols section: {len(lib_symbols_lines)} lines")
    
    if len(lib_symbols_lines) > 1:
        print("✅ lib_symbols section populated!")
        print("📋 Preview:")
        for line in lib_symbols_lines[:15]:  # Show first 15 lines
            print(f"    {line}")
        if len(lib_symbols_lines) > 15:
            print(f"    ... ({len(lib_symbols_lines) - 15} more lines)")
    else:
        print("❌ lib_symbols section still empty")
    
    print(f"\n📁 Generated file: symbol_test_fixed.kicad_sch")
    print(f"🔧 Test this file in KiCAD to see if ?? symbols are resolved")

if __name__ == "__main__":
    test_symbol_definitions()