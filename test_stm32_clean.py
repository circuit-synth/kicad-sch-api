"""
Clean STM32 Circuit - Grid Based
Just the STM32 circuit, properly laid out
"""

import kicad_sch_api as ksa

# KiCAD standard grid
GRID = 1.27  # mm

def grid_to_mm(grid_units):
    """Convert grid units to millimeters"""
    if isinstance(grid_units, tuple):
        return (grid_units[0] * GRID, grid_units[1] * GRID)
    return grid_units * GRID

def create_stm32_clean(sch):
    """Create clean STM32 circuit using exact working positions"""

    # Use the exact positions from the working version
    ORIGIN_X_GRID = 57
    ORIGIN_Y_GRID = 34

    def pos(x_grid, y_grid):
        """Convert grid position to mm"""
        abs_x_grid = ORIGIN_X_GRID + x_grid
        abs_y_grid = ORIGIN_Y_GRID + y_grid
        return grid_to_mm((abs_x_grid, abs_y_grid))

    components = {}

    # Main microcontroller
    components['mcu'] = sch.components.add(
        'MCU_ST_STM32G0:STM32G030K8Tx', 'U1', 'STM32G030K8Tx',
        position=pos(56, 52), rotation=0
    )

    # NRST pull-up resistor
    components['r_nrst'] = sch.components.add(
        'Device:R', 'R10', '10k',
        position=pos(15, 40), rotation=0
    )

    # LED current limiting resistor
    components['r_led'] = sch.components.add(
        'Device:R', 'R11', '330',
        position=pos(69, 53), rotation=0
    )

    # Status LED
    components['led'] = sch.components.add(
        'Device:LED', 'D10', 'GREEN',
        position=pos(69, 59), rotation=90
    )

    # Decoupling capacitors
    components['c_vdd1'] = sch.components.add(
        'Device:C', 'C10', '100nF',
        position=pos(52, 29), rotation=0
    )

    components['c_vdd2'] = sch.components.add(
        'Device:C_Polarized', 'C11', '10uF',
        position=pos(61, 29), rotation=0
    )

    components['c_nrst'] = sch.components.add(
        'Device:C', 'C12', '100nF',
        position=pos(19, 47), rotation=0
    )

    # SWD Debug connector
    components['debug'] = sch.components.add(
        'Connector:Conn_01x04_Pin', 'J1', 'SWD',
        position=pos(88, 31), rotation=180
    )

    # Power symbols
    sch.components.add('power:+3.3V', '#PWR020', '+3.3V', position=pos(51, 15))
    sch.components.add('power:+3.3V', '#PWR021', '+3.3V', position=pos(80, 27))
    sch.components.add('power:+3.3V', '#PWR022', '+3.3V', position=pos(15, 35))
    sch.components.add('power:GND', '#PWR023', 'GND', position=pos(69, 65))
    sch.components.add('power:GND', '#PWR024', 'GND', position=pos(57, 24))
    sch.components.add('power:GND', '#PWR025', 'GND', position=pos(56, 80))
    sch.components.add('power:GND', '#PWR026', 'GND', position=pos(19, 50))
    sch.components.add('power:GND', '#PWR027', 'GND', position=pos(83, 29), rotation=270)

    # Wiring - all positions in GRID UNITS
    wires = [
        # VDD power distribution
        ((52, 24), (57, 24)),
        ((57, 24), (61, 24)),
        ((56, 16), (51, 16)),
        ((51, 16), (52, 16)),
        ((52, 16), (61, 16)),
        ((56, 16), (56, 38)),
        ((51, 15), (51, 16)),
        ((52, 16), (52, 21)),
        ((61, 16), (61, 21)),
        # NRST circuit
        ((15, 42), (19, 42)),
        ((19, 42), (29, 42)),
        ((11, 42), (15, 42)),
        ((15, 35), (15, 38)),
        # LED circuit
        ((58, 48), (69, 48)),
        ((69, 48), (69, 50)),
        ((69, 56), (69, 56)),
        ((69, 62), (69, 65)),
        # Debug header
        ((80, 27), (83, 27)),
        ((83, 29), (83, 29)),
        ((81, 31), (83, 31)),
        ((81, 33), (83, 33)),
        # SWD signals from MCU
        ((62, 64), (58, 64)),
        ((62, 65), (58, 65)),
    ]

    for start_grid, end_grid in wires:
        sch.add_wire(
            start=grid_to_mm(start_grid),
            end=grid_to_mm(end_grid)
        )

    # Labels
    labels = [
        ('NRST', (11, 42), 0),
        ('SWDIO', (62, 64), 0),
        ('SWCLK', (62, 65), 0),
        ('SWDIO', (81, 31), 0),
        ('SWCLK', (81, 33), 0),
    ]

    for text, (x_grid, y_grid), rotation in labels:
        sch.add_label(text, position=grid_to_mm((x_grid, y_grid)), rotation=rotation)

    return components


if __name__ == "__main__":
    print("Creating clean STM32 circuit...")
    sch = ksa.create_schematic("STM32_Clean")

    components = create_stm32_clean(sch)

    print(f"\nCreated {len(components)} components:")
    for name, comp in components.items():
        print(f"  {name}: {comp.reference} ({comp.value})")

    output_file = "stm32_clean.kicad_sch"
    sch.save(output_file)
    print(f"\nSaved to: {output_file}")
