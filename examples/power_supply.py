"""
kicad-sch-api Example: 5V Power Supply

Demonstrates:
- Grid-based parametric circuit design
- Power symbols (VBUS, +5V, GND)
- Multiple junction points (input and output rails)
- Polarized capacitor placement
- Voltage regulator integration
- Text box annotations with specifications

This is a basic 5V linear regulator using the LM7805 with input/output filtering.
"""

import kicad_sch_api as ksa

# Enable grid units globally for cleaner parametric design
ksa.use_grid_units(True)


# ============================================================================
# 5V POWER SUPPLY
# ============================================================================

def power_supply(sch, x_grid, y_grid):
    """
    Create a parametric 5V power supply circuit.

    This function creates a complete LM7805-based 5V regulator that can be
    placed anywhere on the schematic by specifying grid coordinates. All
    internal positions are relative offsets from the origin point.

    Args:
        sch: Schematic object to add components to
        x_grid: X origin position in grid units (integer)
        y_grid: Y origin position in grid units (integer)

    Circuit: VBUS -> C1 (10µF) -> LM7805 -> C2 (10µF) -> +5V
    Output: 5V @ 1.5A max (7-35V input, ~2V dropout)
    """

    # Helper function for grid-relative positioning
    def p(dx, dy):
        """Position helper for parametric placement"""
        return (x_grid + dx, y_grid + dy)

    # ===== POWER SYMBOLS =====
    sch.components.add('power:VBUS', '#PWR01', 'VBUS', position=p(5, 0))
    sch.components.add('power:+5V', '#PWR02', '+5V', position=p(15, 0))

    # ===== MAIN COMPONENTS =====
    # Input filter capacitor (polarized)
    c_in = sch.components.add('Device:C_Polarized', 'C1', '10uF',
                             position=p(5, 4))

    # Voltage regulator (LM7805)
    u = sch.components.add('Regulator_Linear:LM7805_TO220', 'U1', 'LM7805',
                          position=p(10, 5))

    # Output filter capacitor
    c_out = sch.components.add('Device:C', 'C2', '10uF',
                              position=p(15, 4))

    # ===== GROUND SYMBOLS =====
    sch.components.add('power:GND', '#PWR03', 'GND', position=p(5, 7))
    sch.components.add('power:GND', '#PWR04', 'GND', position=p(10, 9))
    sch.components.add('power:GND', '#PWR05', 'GND', position=p(15, 7))

    # ===== JUNCTIONS =====
    # Input rail junction (splits to C1 and U1)
    sch.junctions.add(position=p(5, 2))

    # Output rail junction (splits from U1 to C2 and +5V)
    sch.junctions.add(position=p(15, 2))

    # ===== WIRING =====
    # Get pin positions
    vbus_pins = sch.list_component_pins('#PWR01')
    v5_pins = sch.list_component_pins('#PWR02')
    c_in_pins = sch.list_component_pins('C1')
    u_pins = sch.list_component_pins('U1')
    c_out_pins = sch.list_component_pins('C2')
    gnd_in_pins = sch.list_component_pins('#PWR03')
    gnd_u_pins = sch.list_component_pins('#PWR04')
    gnd_out_pins = sch.list_component_pins('#PWR05')

    # Input rail (VBUS -> junction -> C1 + U1)
    sch.add_wire(start=vbus_pins[0][1], end=p(5, 2))
    sch.add_wire(start=p(5, 2), end=c_in_pins[0][1])
    sch.add_wire(start=p(5, 2), end=u_pins[0][1])

    # Output rail (U1 -> junction -> C2 + +5V)
    sch.add_wire(start=u_pins[2][1], end=p(15, 2))
    sch.add_wire(start=p(15, 2), end=c_out_pins[0][1])
    sch.add_wire(start=p(15, 2), end=v5_pins[0][1])

    # Ground connections
    sch.add_wire(start=c_in_pins[1][1], end=gnd_in_pins[0][1])
    sch.add_wire(start=u_pins[1][1], end=gnd_u_pins[0][1])
    sch.add_wire(start=c_out_pins[1][1], end=gnd_out_pins[0][1])

    # ===== ANNOTATIONS =====
    # Specifications text box
    specs_text = "Input: 7-35V DC\nOutput: 5V @ 1.5A max\nDropout: ~2V min"
    sch.add_text_box(
        specs_text,
        position=p(11, 12),
        size=(8, 4),
        font_size=1.27
    )

    # ===== DECORATIVE ELEMENTS =====
    # Rectangle border for visual grouping
    sch.add_rectangle(start=p(-2, -3), end=p(22, 16))

    # Title text
    sch.add_text("5V Power Supply", position=p(6, -1), size=1.27)


def main():
    """Generate the power supply example schematic."""
    print("Creating 5V power supply circuit...")

    # Create a new schematic
    sch = ksa.create_schematic("Example_PowerSupply")

    # Place the power supply at grid position (20, 20)
    # This positions the reference origin at (20, 20) and all other components
    # are placed relative to this origin point
    power_supply(sch, 20, 20)

    # Save the schematic
    sch.save("power_supply.kicad_sch")
    print("✅ Saved: power_supply.kicad_sch")
    print()
    print("Open in KiCAD to see the result:")
    print("  open power_supply.kicad_sch")


if __name__ == "__main__":
    main()
