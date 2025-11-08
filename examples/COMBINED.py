"""
kicad-sch-api Example: COMBINED - Run All Examples

Demonstrates:
- Running all example circuits sequentially
- Each circuit creates its own schematic file
- Complete showcase of all kicad-sch-api capabilities

This runs all the individual example scripts to generate their schematics:
1. Voltage Divider → voltage_divider.kicad_sch
2. RC Filter → rc_filter.kicad_sch
3. Power Supply (3.3V) → power_supply.kicad_sch
4. STM32 Microcontroller → stm32_simple.kicad_sch

Perfect way to generate all example schematics at once!
"""

import sys
from pathlib import Path

# Add examples directory to path
examples_dir = Path(__file__).parent
sys.path.insert(0, str(examples_dir))

# Import all example modules
import voltage_divider
import rc_filter
import power_supply
import stm32_simple


def main():
    """Run all example scripts to generate all schematics."""
    print("=" * 70)
    print("COMBINED - Running All Example Circuits")
    print("=" * 70)
    print()

    examples = [
        ("Voltage Divider", voltage_divider),
        ("RC Filter", rc_filter),
        ("3.3V Power Supply", power_supply),
        ("STM32 Microcontroller", stm32_simple),
    ]

    for i, (name, module) in enumerate(examples, 1):
        print(f"[{i}/{len(examples)}] Running {name}...")
        print("-" * 70)
        module.main()
        print()

    print("=" * 70)
    print("✅ ALL EXAMPLES COMPLETED!")
    print("=" * 70)
    print()
    print("Generated schematics:")
    print("  • voltage_divider.kicad_sch")
    print("  • rc_filter.kicad_sch")
    print("  • power_supply.kicad_sch")
    print("  • stm32_simple.kicad_sch")
    print()
    print("Open any schematic in KiCAD:")
    print("  open voltage_divider.kicad_sch")
    print("  open rc_filter.kicad_sch")
    print("  open power_supply.kicad_sch")
    print("  open stm32_simple.kicad_sch")


if __name__ == "__main__":
    main()
