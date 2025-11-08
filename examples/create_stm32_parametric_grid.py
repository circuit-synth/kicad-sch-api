"""
STM32G030K8Tx Parametric Circuit Generator - GRID BASED VERSION

Creates a complete STM32 microcontroller circuit using grid units (1.27mm).
Much more intuitive than working in mm!
"""

import kicad_sch_api as ksa


# KiCAD standard grid
GRID = 1.27  # mm


def grid_to_mm(grid_units):
    """Convert grid units to millimeters"""
    if isinstance(grid_units, tuple):
        return (grid_units[0] * GRID, grid_units[1] * GRID)
    return grid_units * GRID


def create_stm32_microprocessor_grid(sch, x_offset_grids=0, y_offset_grids=0, instance=1):
    """
    Create STM32G030K8Tx microprocessor circuit at specified position.

    Args:
        sch: KiCAD schematic object
        x_offset_grids: X position offset in grid units (1.27mm each)
        y_offset_grids: Y position offset in grid units (1.27mm each)
        instance: Circuit instance number (affects reference designators)

    Returns:
        dict: Dictionary of created components with their references
    """

    # Circuit origin in grid units (top-left of bounding box)
    # Original mm: (72.39, 43.815) = approximately (57, 34.5) grids
    ORIGIN_X_GRID = 57
    ORIGIN_Y_GRID = 34

    def pos(x_grid, y_grid):
        """Convert grid position to mm position with offset"""
        abs_x_grid = ORIGIN_X_GRID + x_grid
        abs_y_grid = ORIGIN_Y_GRID + y_grid
        return grid_to_mm((x_offset_grids + abs_x_grid, y_offset_grids + abs_y_grid))

    # Reference designator naming based on instance
    base_num = (instance - 1) * 100
    u_ref = f'U{instance + 1}' if instance > 1 else 'U1'
    c_refs = [f'C{base_num + 10 + i}' for i in range(3)]
    r_refs = [f'R{base_num + 10 + i}' for i in range(2)]
    d_ref = f'D{base_num + 10}'
    j_ref = f'J{instance}'

    components = {}

    # Component positions in GRID UNITS relative to origin
    # Main microcontroller - approximately (128.27, 110.49)mm = (101, 87) grids
    components['mcu'] = sch.components.add(
        'MCU_ST_STM32G0:STM32G030K8Tx',
        u_ref,
        'STM32G030K8Tx',
        position=pos(56, 52),  # Grid-based position
        rotation=0
    )

    # NRST pull-up resistor - (91.44, 85.09)mm = (72, 67) grids
    components['r_nrst'] = sch.components.add(
        'Device:R',
        r_refs[0],
        '10k',
        position=pos(15, 40),  # Grid position
        rotation=0
    )

    # LED current limiting resistor - (160.02, 101.6)mm = (126, 80) grids
    components['r_led'] = sch.components.add(
        'Device:R',
        r_refs[1],
        '330',
        position=pos(69, 53),  # Grid position
        rotation=0
    )

    # Status LED - (160.02, 109.22)mm = (126, 86) grids
    components['led'] = sch.components.add(
        'Device:LED',
        d_ref,
        'GREEN',
        position=pos(69, 59),  # Grid position
        rotation=90
    )

    # Decoupling capacitors
    components['c_vdd1'] = sch.components.add(
        'Device:C',
        c_refs[0],
        '100nF',
        position=pos(52, 29),
        rotation=0
    )

    components['c_vdd2'] = sch.components.add(
        'Device:C_Polarized',
        c_refs[1],
        '10uF',
        position=pos(61, 29),
        rotation=0
    )

    components['c_nrst'] = sch.components.add(
        'Device:C',
        c_refs[2],
        '100nF',
        position=pos(19, 47),
        rotation=0
    )

    # SWD Debug connector
    components['debug'] = sch.components.add(
        'Connector:Conn_01x04_Pin',
        j_ref,
        'SWD',
        position=pos(88, 31),
        rotation=180
    )

    # Power symbols - add as regular components
    pwr_base = base_num + 20

    # +3.3V symbols
    sch.components.add('power:+3.3V', f'#PWR{pwr_base:02d}', '+3.3V', position=pos(51, 15))
    sch.components.add('power:+3.3V', f'#PWR{pwr_base+1:02d}', '+3.3V', position=pos(80, 27))
    sch.components.add('power:+3.3V', f'#PWR{pwr_base+2:02d}', '+3.3V', position=pos(15, 35))

    # GND symbols
    sch.components.add('power:GND', f'#PWR{pwr_base+3:02d}', 'GND', position=pos(69, 65))
    sch.components.add('power:GND', f'#PWR{pwr_base+4:02d}', 'GND', position=pos(57, 24))
    sch.components.add('power:GND', f'#PWR{pwr_base+5:02d}', 'GND', position=pos(56, 80))
    sch.components.add('power:GND', f'#PWR{pwr_base+6:02d}', 'GND', position=pos(19, 50))
    sch.components.add('power:GND', f'#PWR{pwr_base+7:02d}', 'GND', position=pos(83, 29), rotation=270)

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
        ((69, 56), (69, 56)),  # R11 pin 2 to D10 cathode
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
            start=grid_to_mm((x_offset_grids + start_grid[0], y_offset_grids + start_grid[1])),
            end=grid_to_mm((x_offset_grids + end_grid[0], y_offset_grids + end_grid[1]))
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
        sch.add_label(
            text,
            position=grid_to_mm((x_offset_grids + x_grid, y_offset_grids + y_grid)),
            rotation=rotation
        )

    return components


if __name__ == "__main__":
    # Test: Create schematic with STM32 circuit at origin
    sch = ksa.create_schematic("STM32_Parametric_Grid_Test")

    print("Creating STM32 microprocessor circuit (GRID-BASED)...")
    components = create_stm32_microprocessor_grid(sch, x_offset_grids=0, y_offset_grids=0, instance=1)

    print(f"\nCreated {len(components)} components:")
    for name, comp in components.items():
        print(f"  {name}: {comp.reference} ({comp.value})")

    # Save schematic
    output_file = "stm32_parametric_grid_test.kicad_sch"
    sch.save(output_file)
    print(f"\nSchematic saved to: {output_file}")
    print(f"\nNow positions are in GRID UNITS - much easier to adjust!")
    print(f"  Example: Move component 1 grid = just add/subtract 1 from position")
