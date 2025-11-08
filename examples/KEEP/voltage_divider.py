"""
kicad-sch-api Example: Voltage Divider

Demonstrates:
- Grid-based parametric circuit design
- Component placement using integer grid coordinates
- Wire routing with proper pin connections
- Junction creation for electrical nodes
- Adding decorative elements (rectangle, text)

This is a basic 10k/10k voltage divider that outputs 2.5V when powered from 5V.
"""

import kicad_sch_api as ksa

# Enable grid units globally for cleaner parametric design
ksa.use_grid_units(True)


# ============================================================================
# VOLTAGE DIVIDER
# ============================================================================

def voltage_divider(sch, x_grid, y_grid):
    """
    Create a parametric voltage divider circuit.

    This function creates a complete voltage divider that can be placed anywhere
    on the schematic by specifying grid coordinates. All internal positions are
    relative offsets from the origin point (x_grid, y_grid).

    Args:
        sch: Schematic object to add components to
        x_grid: X origin position in grid units (integer)
        y_grid: Y origin position in grid units (integer)

    Circuit: VCC -> R1 (10k) -> VOUT -> R2 (10k) -> GND
    Output: VOUT = VCC * (R2 / (R1 + R2)) = VCC / 2
    """

    # Helper function for grid-relative positioning
    def p(dx, dy):
        """Position helper for parametric placement"""
        return (x_grid + dx, y_grid + dy)

    # ===== POWER SYMBOLS =====
    sch.components.add('power:VCC', '#PWR01', 'VCC', position=p(0, 0))
    sch.components.add('power:GND', '#PWR02', 'GND', position=p(0, 21))

    # ===== RESISTORS =====
    # Each resistor is 6 grid units tall (pins at ±3 from center)
    r1 = sch.components.add('Device:R', 'R1', '10k', position=p(0, 5))
    r2 = sch.components.add('Device:R', 'R2', '10k', position=p(0, 15))

    # ===== JUNCTION =====
    # Junction at the output node (between R1 and R2)
    sch.junctions.add(position=p(0, 11))

    # ===== WIRING =====
    # Manual wiring for power connections
    sch.add_wire(start=p(0, 0), end=p(0, 2))       # VCC to R1 pin 1 (top)
    sch.add_wire(start=p(0, 18), end=p(0, 21))     # R2 pin 2 (bottom) to GND

    # Auto-route between resistors (demonstrates pin-to-pin connection)
    sch.auto_route_pins('R1', '2', 'R2', '1', routing_strategy='direct')

    # Horizontal tap to VOUT label
    sch.add_wire(start=p(0, 11), end=p(3, 11))

    # ===== LABELS =====
    sch.add_label('VOUT', position=p(3, 11))

    # ===== DECORATIVE ELEMENTS =====
    # Rectangle border for visual grouping
    sch.add_rectangle(start=p(-10, -10), end=p(10, 26))

    # Title text
    sch.add_text("Voltage Divider", position=p(-2, -8), size=1.27)


def main():
    """Generate the voltage divider example schematic."""
    print("Creating voltage divider circuit...")

    # Create a new schematic
    sch = ksa.create_schematic("Example_VoltageDiv")

    # Place the voltage divider at grid position (20, 20)
    # This positions the VCC symbol at (20, 20) and all other components
    # are placed relative to this origin point
    voltage_divider(sch, 20, 20)

    # Save the schematic
    sch.save("voltage_divider.kicad_sch")
    print("✅ Saved: voltage_divider.kicad_sch")
    print()
    print("Open in KiCAD to see the result:")
    print("  open voltage_divider.kicad_sch")


if __name__ == "__main__":
    main()
