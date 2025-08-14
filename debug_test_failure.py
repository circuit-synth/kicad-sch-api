#!/usr/bin/env python3
"""
Debug why tests were passing despite missing lib_symbols.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "python"))

from kicad_sch_api.core.schematic import Schematic

def compare_lib_symbols():
    print("🔍 Investigating lib_symbols sections...")
    
    # Load reference schematic
    ref_path = Path(__file__).parent / "python/tests/reference_tests/reference_kicad_projects/single_resistor/single_resistor.kicad_sch"
    ref_sch = Schematic.load(str(ref_path))
    
    # Create recreation
    rec_sch = Schematic.create("test_recreation")
    for ref_comp in ref_sch.components:
        rec_sch.components.add(
            lib_id=ref_comp.lib_id,
            reference=ref_comp.reference,
            value=ref_comp.value,
            position=(ref_comp.position.x, ref_comp.position.y),
            footprint=ref_comp.footprint
        )
    
    # Save both and compare lib_symbols sections
    rec_sch.save('recreation_test.kicad_sch')
    
    # Check lib_symbols in both files
    with open(ref_path, 'r') as f:
        ref_content = f.read()
    
    with open('recreation_test.kicad_sch', 'r') as f:
        rec_content = f.read()
    
    # Analyze lib_symbols sections
    def count_lib_symbols_lines(content):
        lines = content.split('\n')
        lib_lines = []
        in_lib = False
        for line in lines:
            if '(lib_symbols' in line:
                in_lib = True
                lib_lines.append(line)
            elif in_lib:
                lib_lines.append(line)
                if line.strip() == ')' and not line.startswith('\t\t'):
                    break
        return len(lib_lines)
    
    ref_lib_lines = count_lib_symbols_lines(ref_content)
    rec_lib_lines = count_lib_symbols_lines(rec_content)
    
    print(f"📊 lib_symbols comparison:")
    print(f"  Reference file: {ref_lib_lines} lines")
    print(f"  Recreation file: {rec_lib_lines} lines")
    print(f"  Difference: {abs(ref_lib_lines - rec_lib_lines)} lines")
    
    # Check if our tests were actually comparing lib_symbols
    has_device_r_ref = '(symbol "Device:R"' in ref_content
    has_device_r_rec = '(symbol "Device:R"' in rec_content
    
    print(f"\n🔍 Symbol definitions:")
    print(f"  Reference has Device:R definition: {has_device_r_ref}")
    print(f"  Recreation has Device:R definition: {has_device_r_rec}")
    
    if has_device_r_ref and not has_device_r_rec:
        print("❌ CRITICAL: Tests were not catching missing symbol definitions!")
        print("❌ This means our comparison logic was inadequate")
    elif has_device_r_ref and has_device_r_rec:
        print("✅ Both have symbol definitions - comparison should have caught this")
    
    return ref_lib_lines, rec_lib_lines

if __name__ == "__main__":
    compare_lib_symbols()