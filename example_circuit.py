"""
kicad-sch-api Example Circuit - Voltage Divider Only

A single clean, parametric circuit demonstrating grid-based positioning.
"""

import kicad_sch_api as ksa

GRID = 1.27  # mm


def grid_to_mm(grid_units):
    """Convert grid units to millimeters"""
    if isinstance(grid_units, tuple):
        return (grid_units[0] * GRID, grid_units[1] * GRID)
    return grid_units * GRID


# ============================================================================
# VOLTAGE DIVIDER
# ============================================================================

def voltage_divider(sch, x_grid, y_grid):
    """
    Voltage divider circuit: 10k/10k resistive divider

    Args:
        sch: Schematic object
        x_grid: X position in grid units
        y_grid: Y position in grid units
    """

    def pos(dx, dy):
        return grid_to_mm((x_grid + dx, y_grid + dy))

    # VCC symbol at top
    sch.components.add('power:VCC', '#PWR01', 'VCC', position=pos(0, 0))

    # First resistor (6 grid units tall, centered at grid 5)
    r1 = sch.components.add('Device:R', 'R1', '10k', position=pos(0, 5))

    # Second resistor (6 grid units tall, centered at grid 15)
    r2 = sch.components.add('Device:R', 'R2', '10k', position=pos(0, 15))

    # GND symbol closer (grid 21)
    sch.components.add('power:GND', '#PWR02', 'GND', position=pos(0, 21))

    # Add junction at midpoint between resistors
    sch.junctions.add(position=pos(0, 11))

    # Wiring - vertical chain with junction tap
    sch.add_wire(start=pos(0, 0), end=pos(0, 2))       # VCC to R1 top
    sch.add_wire(start=pos(0, 8), end=pos(0, 11))      # R1 bottom to junction
    sch.add_wire(start=pos(0, 11), end=pos(0, 12))     # Junction to R2 top
    sch.add_wire(start=pos(0, 18), end=pos(0, 21))     # R2 bottom to GND
    sch.add_wire(start=pos(0, 11), end=pos(3, 11))     # Junction to VOUT label (horizontal tap)

    # Output label at junction
    sch.add_label('VOUT', position=pos(3, 11))


def main():
    print("Creating voltage divider circuit...")
    sch = ksa.create_schematic("Example_VoltageDiv")

    voltage_divider(sch, 20, 20)  # Place at grid (20, 20)

    sch.save("example_circuit.kicad_sch")
    print("✅ Saved: example_circuit.kicad_sch")


if __name__ == "__main__":
    main()
