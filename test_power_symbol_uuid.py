#!/usr/bin/env python3
"""Test to verify power symbol UUID preservation during save."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api import load_schematic, Schematic
from kicad_sch_api.core.types import Point
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_power_symbol_uuid_preservation():
    """Test that power symbol UUIDs are preserved through save/load cycle."""

    print("\n" + "="*70)
    print("TEST: Power Symbol UUID Preservation")
    print("="*70)

    # Create new schematic
    sch = Schematic()
    sch.name = "test_power_uuid"

    # Add a power symbol
    print("\n1. Adding power symbol to schematic...")
    power_comp = sch.components.add(
        lib_id="power:VCC",
        reference="#PWR001",
        value="VCC",
        position=(50, 50)
    )

    print(f"   Power component added:")
    print(f"   - reference: {power_comp.reference}")
    print(f"   - lib_id: {power_comp.lib_id}")
    print(f"   - uuid: {power_comp.uuid}")
    print(f"   - _data.uuid: {power_comp._data.uuid}")
    print(f"   - _data.__dict__.keys(): {list(power_comp._data.__dict__.keys())}")

    original_uuid = power_comp.uuid

    # Save to file
    test_file = Path("/tmp/test_power_uuid.kicad_sch")
    print(f"\n2. Saving to {test_file}...")
    sch.save(test_file, preserve_format=False)

    # Check what was written to file
    print("\n3. Checking file content...")
    with open(test_file, 'r') as f:
        content = f.read()

    if f'(uuid "{original_uuid}")' in content:
        print(f"   ✅ UUID {original_uuid} FOUND in file")
    else:
        print(f"   ❌ UUID {original_uuid} NOT FOUND in file")

    # Check if there's ANY uuid for #PWR001
    import re
    pwr_section = re.search(r'\(symbol.*?lib_id "power:VCC".*?\(instances', content, re.DOTALL)
    if pwr_section:
        uuid_match = re.search(r'\(uuid "([^"]+)"', pwr_section.group(0))
        if uuid_match:
            found_uuid = uuid_match.group(1)
            print(f"   Found UUID in file: {found_uuid}")
            if found_uuid == original_uuid:
                print(f"   ✅ MATCHES original UUID")
            else:
                print(f"   ❌ DIFFERENT from original UUID {original_uuid}")
        else:
            print(f"   ❌ NO UUID found in power symbol section")

    # Load it back
    print(f"\n4. Loading from {test_file}...")
    loaded_sch = load_schematic(test_file)

    # Find the power symbol
    power_symbols = [c for c in loaded_sch.components if c.reference == "#PWR001"]

    if power_symbols:
        loaded_power = power_symbols[0]
        print(f"   Power symbol loaded:")
        print(f"   - reference: {loaded_power.reference}")
        print(f"   - uuid: {loaded_power.uuid}")

        if loaded_power.uuid == original_uuid:
            print(f"\n   ✅ SUCCESS: UUID preserved through save/load cycle")
            return True
        else:
            print(f"\n   ❌ FAILURE: UUID changed")
            print(f"      Original: {original_uuid}")
            print(f"      Loaded:   {loaded_power.uuid}")
            return False
    else:
        print(f"\n   ❌ FAILURE: Power symbol not found after load")
        return False

if __name__ == "__main__":
    success = test_power_symbol_uuid_preservation()
    sys.exit(0 if success else 1)
