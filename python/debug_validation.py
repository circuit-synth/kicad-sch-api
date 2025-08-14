#!/usr/bin/env python3
"""Debug validation issues."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kicad_sch_api.utils.validation import SchematicValidator
from kicad_sch_api.core.schematic import Schematic

def test_validation_patterns():
    validator = SchematicValidator()
    
    test_cases = [
        ("R1", True),    # Should pass
        ("R", True),     # Should pass (no number)
        ("#PWR01", True), # Should pass (power symbol)
        ("1R", False),   # Should fail (starts with digit)
        ("R-1", False),  # Should fail (has hyphen)
        ("r1", False),   # Should fail (lowercase)
        ("R 1", False),  # Should fail (has space)
        ("", False),     # Should fail (empty)
    ]
    
    print("Testing validation patterns:")
    for ref, expected in test_cases:
        result = validator.validate_reference(ref)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{ref}': {result} (expected {expected})")

def test_component_add_validation():
    print("\nTesting component add validation:")
    sch = Schematic.create("Validation Test")
    
    invalid_refs = ["1R", "R-1", "r1", "R 1", ""]
    
    for invalid_ref in invalid_refs:
        try:
            comp = sch.components.add("Device:R", invalid_ref, "10k")
            print(f"  ✗ '{invalid_ref}': Did not raise error - got {comp.reference}")
        except Exception as e:
            print(f"  ✓ '{invalid_ref}': Correctly raised {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_validation_patterns()
    test_component_add_validation()