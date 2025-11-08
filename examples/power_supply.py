"""
kicad-sch-api Example: 3.3V Power Supply

Demonstrates:
- Grid-based parametric circuit design
- Power symbols (+5V, +3.3V, GND)
- Multiple junction points (input and output rails)
- Horizontal component layout
- Text box annotations with specifications

This is a basic 3.3V linear regulator using the AMS1117-3.3 with input/output filtering.
"""

import kicad_sch_api as ksa

# Enable grid units globally for cleaner parametric design
ksa.use_grid_units(True)


# ============================================================================
# 3.3V POWER SUPPLY
# ============================================================================

def power_supply(sch, x_grid, y_grid):
    """
    Create a parametric 3.3V power supply circuit.

    Args:
        sch: Schematic object to add components to
        x_grid: X origin position in grid units (integer)
        y_grid: Y origin position in grid units (integer)

    Circuit: +5V -> C1 (10µF) -> AMS1117-3.3 -> C2 (10µF) -> +3.3V
    Output: 3.3V @ 1A max (5V input, ~1.2V dropout)
    """

    # Helper function for grid-relative positioning
    def p(dx, dy):
        """Position helper for parametric placement"""
        return (x_grid + dx, y_grid + dy)

    # ===== POWER SYMBOLS =====
    sch.components.add('power:+5V', '#PWR01', '+5V', position=p(0, 0))
    sch.components.add('power:+3.3V', '#PWR02', '+3.3V', position=p(30, 0))

    # ===== MAIN COMPONENTS =====
    # Input capacitor (polarized)
    sch.components.add('Device:C_Polarized', 'C1', '10uF', position=p(0, 8))

    # Voltage regulator (no rotation needed)
    sch.components.add('Regulator_Linear:AMS1117-3.3', 'U1', 'AMS1117-3.3',
                      position=p(15, 4))

    # Output capacitor
    sch.components.add('Device:C', 'C2', '10uF', position=p(30, 8))

    # ===== GROUND SYMBOLS =====
    sch.components.add('power:GND', '#PWR03', 'GND', position=p(0, 15))
    sch.components.add('power:GND', '#PWR04', 'GND', position=p(15, 14))
    sch.components.add('power:GND', '#PWR05', 'GND', position=p(30, 15))

    # ===== JUNCTIONS =====
    sch.junctions.add(position=p(0, 4))   # Input rail
    sch.junctions.add(position=p(30, 4))  # Output rail

    # ===== WIRING =====
    # Input rail
    sch.add_wire(start=p(0, 0), end=p(0, 4))      # VBUS to junction
    sch.add_wire(start=p(0, 4), end=p(0, 5))      # Junction to C1
    sch.add_wire(start=p(0, 4), end=p(9, 4))      # Junction to U1

    # Output rail
    sch.add_wire(start=p(21, 4), end=p(30, 4))    # U1 to junction
    sch.add_wire(start=p(30, 4), end=p(30, 0))    # Junction to +5V
    sch.add_wire(start=p(30, 4), end=p(30, 5))    # Junction to C2

    # Ground connections
    sch.add_wire(start=p(0, 11), end=p(0, 15))    # C1 to GND
    sch.add_wire(start=p(15, 10), end=p(15, 14))  # U1 to GND
    sch.add_wire(start=p(30, 11), end=p(30, 15))  # C2 to GND

    # ===== ANNOTATIONS =====
    # Specifications text box
    specs_text = "Input: 5V DC\nOutput: 3.3V @ 1A max\nDropout: ~1.2V min"
    sch.add_text_box(
        specs_text,
        position=p(13, 36),
        size=(27, 7),
        font_size=1.27
    )

    # ===== DECORATIVE ELEMENTS =====
    # Rectangle border
    sch.add_rectangle(start=p(-5, -7.5), end=p(37, 30))

    # Title text
    sch.add_text("3.3V Power Supply", position=p(11, -3), size=1.27)


def main():
    """Generate the power supply example schematic."""
    print("Creating 3.3V power supply circuit...")

    # Create a new schematic
    sch = ksa.create_schematic("Example_PowerSupply")

    # Place the power supply at grid position (20, 20)
    power_supply(sch, 20, 20)

    # Save the schematic
    sch.save("power_supply.kicad_sch")
    print("✅ Saved: power_supply.kicad_sch")
    print()
    print("Open in KiCAD to see the result:")
    print("  open power_supply.kicad_sch")


if __name__ == "__main__":
    main()
