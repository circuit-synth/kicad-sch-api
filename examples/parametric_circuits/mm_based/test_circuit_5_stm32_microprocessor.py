"""
STM32G030K8Tx Parametric Circuit Generator

Creates a complete STM32 microcontroller circuit with all support components
at any specified (x, y) position. Based on the clean manual layout.
"""

import kicad_sch_api as ksa


def snap_to_grid(value, grid=1.27):
    """Snap coordinate to KiCAD grid (default 1.27mm = 50 mil)"""
    return round(value / grid) * grid


def create_stm32_microprocessor(sch, x_offset=0, y_offset=0, instance=1):
    """
    Create STM32G030K8Tx microprocessor circuit at specified position.

    Args:
        sch: KiCAD schematic object
        x_offset: X position offset in mm
        y_offset: Y position offset in mm
        instance: Circuit instance number (affects reference designators)

    Returns:
        dict: Dictionary of created components with their references
    """

    # Original circuit origin (top-left of bounding box)
    ORIGIN_X = 72.39
    ORIGIN_Y = 43.815

    # Position transformation helper
    def pos(abs_x, abs_y):
        """Convert absolute position from original circuit to offset position"""
        rel_x = abs_x - ORIGIN_X
        rel_y = abs_y - ORIGIN_Y
        return (snap_to_grid(x_offset + rel_x), snap_to_grid(y_offset + rel_y))

    # Reference designator naming based on instance
    base_num = (instance - 1) * 100
    u_ref = f'U{instance + 1}' if instance > 1 else 'U1'
    c_refs = [f'C{base_num + 10 + i}' for i in range(3)]
    r_refs = [f'R{base_num + 10 + i}' for i in range(2)]
    d_ref = f'D{base_num + 10}'
    j_ref = f'J{instance}'

    components = {}

    # Main microcontroller
    components['mcu'] = sch.components.add(
        'MCU_ST_STM32G0:STM32G030K8Tx',
        u_ref,
        'STM32G030K8Tx',
        position=pos(128.27, 110.49),
        rotation=0
    )

    # NRST pull-up resistor (moved up 1 grid = 1.27mm)
    components['r_nrst'] = sch.components.add(
        'Device:R',
        r_refs[0],
        '10k',
        position=pos(91.44, 85.09),  # Was 86.36, now 85.09 (up 1.27mm)
        rotation=0
    )

    # LED current limiting resistor (vertical orientation)
    components['r_led'] = sch.components.add(
        'Device:R',
        r_refs[1],
        '330',
        position=pos(160.02, 101.6),  # Moved down 1 grid from 100.33
        rotation=0  # Vertical
    )

    # Status LED (vertical orientation - cathode at top, anode at bottom)
    components['led'] = sch.components.add(
        'Device:LED',
        d_ref,
        'GREEN',
        position=pos(160.02, 109.22),  # Moved down 1 grid from 107.95
        rotation=90  # Rotated 90 degrees
    )

    # Decoupling capacitor 1 (VDD)
    components['c_vdd1'] = sch.components.add(
        'Device:C',
        c_refs[0],
        '100nF',
        position=pos(138.43, 71.12),
        rotation=0
    )

    # Bulk capacitor (VDD)
    components['c_vdd2'] = sch.components.add(
        'Device:C_Polarized',
        c_refs[1],
        '10uF',
        position=pos(149.86, 71.12),
        rotation=0
    )

    # Decoupling capacitor 3 (NRST) - adjusted for R10 moved up
    components['c_nrst'] = sch.components.add(
        'Device:C',
        c_refs[2],
        '100nF',
        position=pos(96.52, 93.98),  # Back to original position
        rotation=0
    )

    # SWD Debug connector
    components['debug'] = sch.components.add(
        'Connector:Conn_01x04_Pin',
        j_ref,
        'SWD',
        position=pos(184.15, 83.82),
        rotation=180
    )

    # Power symbols - add as regular components
    pwr_base = base_num + 20

    # +3.3V symbols
    sch.components.add(
        'power:+3.3V',
        f'#PWR{pwr_base:02d}',
        '+3.3V',
        position=pos(137.16, 63.5)
    )
    sch.components.add(
        'power:+3.3V',
        f'#PWR{pwr_base+1:02d}',
        '+3.3V',
        position=pos(173.99, 78.74)
    )
    sch.components.add(
        'power:+3.3V',
        f'#PWR{pwr_base+2:02d}',
        '+3.3V',
        position=pos(91.44, 78.74)
    )

    # GND symbols
    sch.components.add(
        'power:GND',
        f'#PWR{pwr_base+3:02d}',
        'GND',
        position=pos(160.02, 116.84)
    )
    sch.components.add(
        'power:GND',
        f'#PWR{pwr_base+4:02d}',
        'GND',
        position=pos(144.78, 74.93)
    )
    sch.components.add(
        'power:GND',
        f'#PWR{pwr_base+5:02d}',
        'GND',
        position=pos(128.27, 135.89)
    )
    sch.components.add(
        'power:GND',
        f'#PWR{pwr_base+6:02d}',
        'GND',
        position=pos(96.52, 97.79)  # Back to original
    )
    sch.components.add(
        'power:GND',
        f'#PWR{pwr_base+7:02d}',
        'GND',
        position=pos(177.8, 80.01),  # Moved up 1 grid from 81.28
        rotation=270  # Rotated for debug header
    )

    # Wiring - all positions from original circuit
    wires = [
        # VDD power distribution
        ((138.43, 74.93), (144.78, 74.93)),
        ((144.78, 74.93), (149.86, 74.93)),
        ((128.27, 64.77), (137.16, 64.77)),
        ((137.16, 64.77), (138.43, 64.77)),
        ((138.43, 64.77), (149.86, 64.77)),
        ((128.27, 64.77), (128.27, 82.55)),
        ((137.16, 63.5), (137.16, 64.77)),
        ((138.43, 64.77), (138.43, 67.31)),
        ((149.86, 64.77), (149.86, 67.31)),

        # NRST circuit (adjusted for R10 moved up 1 grid)
        ((91.44, 88.9), (96.52, 88.9)),    # R10 pin 2 to C3 (adjusted from 90.17)
        ((96.52, 88.9), (110.49, 88.9)),   # C3 to MCU NRST (adjusted from 90.17)
        ((86.36, 88.9), (91.44, 88.9)),    # Label to R10 (adjusted from 90.17)
        ((91.44, 81.28), (91.44, 78.74)),  # R10 pin 1 to +3.3V (adjusted from 82.55)

        # LED circuit (adjusted for R11 down 1 grid, D10 back down)
        ((146.05, 95.25), (160.02, 95.25)),    # MCU PA7 to horizontal wire
        ((160.02, 95.25), (160.02, 97.79)),    # Vertical up to R11 pin 1
        ((160.02, 105.41), (160.02, 105.41)),  # R11 pin 2 to D10 cathode (pin 1)
        ((160.02, 113.03), (160.02, 116.84)),  # D10 anode (pin 2) to GND

        # Debug header
        ((173.99, 78.74), (179.07, 78.74)),  # +3.3V
        ((177.8, 80.01), (179.07, 80.01)),   # GND (moved up 1 grid)
        ((172.72, 83.82), (179.07, 83.82)),  # SWDIO
        ((172.72, 85.09), (179.07, 85.09)),  # SWCLK (adjusted from 86.36)

        # SWD signals from MCU
        ((148.59, 115.57), (146.05, 115.57)),  # SWDIO
        ((148.59, 116.84), (146.05, 116.84)),  # SWCLK (adjusted from 118.11)
    ]

    for start, end in wires:
        sch.add_wire(start=pos(start[0], start[1]), end=pos(end[0], end[1]))

    # Labels
    labels = [
        ('NRST', (86.36, 88.9), 0),      # Fixed: adjusted for R10 moved up
        ('SWDIO', (148.59, 115.57), 0),
        ('SWCLK', (148.59, 116.84), 0),  # Fixed: was 118.11, moved up 1 grid to 116.84
        ('SWDIO', (172.72, 83.82), 0),
        ('SWCLK', (172.72, 85.09), 0),   # Fixed: was 86.36, moved up 1 grid to 85.09
    ]

    for text, (x, y), rotation in labels:
        sch.add_label(text, position=pos(x, y), rotation=rotation)

    # Graphical elements
    # Main circuit border rectangle
    sch.add_rectangle(
        start=pos(72.39, 43.815),
        end=pos(193.04, 151.13)
    )

    # Debug section border rectangle
    sch.add_rectangle(
        start=pos(161.29, 64.77),
        end=pos(187.325, 90.17)
    )

    # Title text
    sch.add_text(
        "STM32G030K8Tx MICROCONTROLLER",
        position=pos(131.572, 50.8),
        size=2.5
    )

    # Subtitle
    sch.add_text(
        "ARM Cortex-M0+ @ 64MHz • 64KB Flash • 8KB RAM",
        position=pos(128.778, 147.32),
        size=1.27
    )

    # Debug label
    sch.add_text(
        "Debug",
        position=pos(173.482, 68.58),
        size=2.0
    )

    return components


if __name__ == "__main__":
    # Test: Create schematic with STM32 circuit at origin
    sch = ksa.create_schematic("STM32_Parametric_Test")

    print("Creating STM32 microprocessor circuit...")
    components = create_stm32_microprocessor(sch, x_offset=0, y_offset=0, instance=1)

    print(f"\nCreated {len(components)} components:")
    for name, comp in components.items():
        print(f"  {name}: {comp.reference} ({comp.value})")

    # Save schematic
    output_file = "stm32_parametric_test.kicad_sch"
    sch.save(output_file)
    print(f"\nSchematic saved to: {output_file}")
