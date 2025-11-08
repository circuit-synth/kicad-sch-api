#!/usr/bin/env python3
"""
kicad-sch-api Example Circuit - Parametric Circuit Demonstration

This example demonstrates how to create reusable parametric circuit blocks that can be
placed anywhere on a schematic using simple grid-based positioning.

Features:
- Voltage Divider (10k/10k) - 2.5V output
- 5V Power Supply (LM7805) - regulated power
- RC Low-Pass Filter (1kHz) - signal filtering
- STM32G030K8Tx Microprocessor - complete MCU with support circuitry

All circuits use grid-based positioning where you pass in (x, y) as integers representing
grid units. 1 grid unit = 1.27mm (50 mil standard KiCAD grid).
"""

import kicad_sch_api as ksa


def snap_to_grid(value: float, grid_size: float = 1.27) -> float:
    """Snap a coordinate value to the nearest grid point."""
    return round(value / grid_size) * grid_size


# ============================================================================
# VOLTAGE DIVIDER CIRCUIT
# ============================================================================

def create_voltage_divider(sch, x_offset_grids: int, y_offset_grids: int, instance: int = 1):
    """
    Create a voltage divider circuit at specified grid location.

    Args:
        sch: Schematic object
        x_offset_grids: X offset in grid units (integers)
        y_offset_grids: Y offset in grid units (integers)
        instance: Circuit instance number for unique references

    Returns:
        dict: Dictionary of created components
    """
    GRID = 1.27  # mm per grid unit

    def pos(x_grid, y_grid):
        """Convert grid position to mm coordinates"""
        return ((x_offset_grids + x_grid) * GRID, (y_offset_grids + y_grid) * GRID)

    # Generate unique references
    r1_ref = f"R{instance}1" if instance > 1 else "R1"
    r2_ref = f"R{instance}2" if instance > 1 else "R2"

    # Component positions in GRID UNITS (clean integers!)
    r1_pos = pos(6, 10)
    r2_pos = pos(6, 19)

    # Components
    r1 = sch.components.add("Device:R", r1_ref, "10k", position=r1_pos)
    r2 = sch.components.add("Device:R", r2_ref, "10k", position=r2_pos)

    # Junction between resistors
    junction_pos = pos(6, 15)
    sch.junctions.add(position=junction_pos)

    # Labels
    sch.add_label("VCC", position=pos(6, 6))
    sch.add_label("VOUT", position=pos(10, 15))
    sch.add_label("GND", position=pos(6, 23))

    # Wires - get pin positions
    r1_pins = sch.list_component_pins(r1_ref)
    r2_pins = sch.list_component_pins(r2_ref)

    r1_pin1 = r1_pins[0][1]  # Top pin
    r1_pin2 = r1_pins[1][1]  # Bottom pin
    r2_pin1 = r2_pins[0][1]  # Top pin
    r2_pin2 = r2_pins[1][1]  # Bottom pin

    sch.add_wire(start=pos(6, 6), end=r1_pin1)
    sch.add_wire(start=r1_pin2, end=junction_pos)
    sch.add_wire(start=junction_pos, end=r2_pin1)
    sch.add_wire(start=r2_pin2, end=pos(6, 23))
    sch.add_wire(start=junction_pos, end=pos(10, 15))

    # Rectangle border
    sch.add_rectangle(start=pos(0, 0), end=pos(24, 36))

    # Title
    sch.add_text("VOLTAGE DIVIDER", position=pos(11, 2), size=2.0)

    # Formula annotation
    formula_text = "Vout = Vin × R2/(R1+R2)\nVout = 2.5V @ Vin=5V"
    sch.add_text_box(
        formula_text,
        position=pos(2, 29),
        size=(20 * GRID, 6 * GRID),
        font_size=1.27
    )

    return {r1_ref: r1, r2_ref: r2}


# ============================================================================
# 5V POWER SUPPLY CIRCUIT
# ============================================================================

def create_power_supply(sch, x_offset: float, y_offset: float, instance: int = 1):
    """
    Create a 5V power supply circuit using LM7805.

    Args:
        sch: Schematic object
        x_offset: X offset in mm
        y_offset: Y offset in mm
        instance: Circuit instance number

    Returns:
        dict: Dictionary of created components
    """
    GRID = 2.54

    rect_x = snap_to_grid(x_offset)
    rect_y = snap_to_grid(y_offset)

    u_x = snap_to_grid(rect_x + GRID * 10)
    u_y = snap_to_grid(rect_y + GRID * 5.7)

    # Generate unique references
    if instance == 1:
        u_ref, c_in_ref, c_out_ref = "U1", "C1", "C2"
        pwr_refs = ["#PWR01", "#PWR02", "#PWR03", "#PWR04", "#PWR05"]
    else:
        u_ref = f"U{instance}"
        c_in_ref = f"C{instance}1"
        c_out_ref = f"C{instance}2"
        pwr_refs = [f"#PWR{instance}01", f"#PWR{instance}02", f"#PWR{instance}03",
                    f"#PWR{instance}04", f"#PWR{instance}05"]

    # Title
    title_x = snap_to_grid(u_x)
    title_y = snap_to_grid(rect_y + GRID * 1.35)
    sch.add_text("5V POWER SUPPLY", position=(title_x, title_y), size=2.0)

    # Component positions
    c_in_x = snap_to_grid(u_x - GRID * 6.5)
    c_in_y = snap_to_grid(u_y + GRID * 1.5)
    c_out_x = snap_to_grid(u_x + GRID * 5.5)
    c_out_y = snap_to_grid(u_y + GRID * 1.5)

    # Components
    c_in = sch.components.add("Device:C_Polarized", c_in_ref, "10uF", position=(c_in_x, c_in_y))
    u = sch.components.add("Regulator_Linear:LM7805_TO220", u_ref, "LM7805", position=(u_x, u_y))
    c_out = sch.components.add("Device:C", c_out_ref, "10uF", position=(c_out_x, c_out_y))

    # Power symbols
    vbus_x, vbus_y = c_in_x, snap_to_grid(c_in_y - GRID * 2)
    v5_x, v5_y = c_out_x, snap_to_grid(c_out_y - GRID * 2)

    sch.components.add("power:VBUS", pwr_refs[0], "VBUS", position=(vbus_x, vbus_y))
    sch.components.add("power:+5V", pwr_refs[1], "+5V", position=(v5_x, v5_y))

    # Ground symbols
    gnd_c_in_y = snap_to_grid(c_in_y + GRID * 1.5)
    gnd_u_y = snap_to_grid(u_y + GRID * 3)
    gnd_c_out_y = snap_to_grid(c_out_y + GRID * 1.5)

    sch.components.add("power:GND", pwr_refs[2], "GND", position=(c_in_x, gnd_c_in_y))
    sch.components.add("power:GND", pwr_refs[3], "GND", position=(u_x, gnd_u_y))
    sch.components.add("power:GND", pwr_refs[4], "GND", position=(c_out_x, gnd_c_out_y))

    # Junctions
    junction_in_x = c_in_x
    junction_in_y = snap_to_grid(vbus_y + GRID * 0.5)
    junction_out_x = c_out_x
    junction_out_y = snap_to_grid(v5_y + GRID * 0.5)

    sch.junctions.add(position=(junction_in_x, junction_in_y))
    sch.junctions.add(position=(junction_out_x, junction_out_y))

    # Get pin positions
    u_pins = sch.list_component_pins(u_ref)
    c_in_pins = sch.list_component_pins(c_in_ref)
    c_out_pins = sch.list_component_pins(c_out_ref)
    vbus_pins = sch.list_component_pins(pwr_refs[0])
    v5_pins = sch.list_component_pins(pwr_refs[1])
    gnd_in_pins = sch.list_component_pins(pwr_refs[2])
    gnd_u_pins = sch.list_component_pins(pwr_refs[3])
    gnd_out_pins = sch.list_component_pins(pwr_refs[4])

    # Wires - Input rail
    sch.add_wire(start=vbus_pins[0][1], end=(junction_in_x, junction_in_y))
    sch.add_wire(start=(junction_in_x, junction_in_y), end=c_in_pins[0][1])
    sch.add_wire(start=(junction_in_x, junction_in_y), end=u_pins[0][1])

    # Wires - Output rail
    sch.add_wire(start=u_pins[2][1], end=(junction_out_x, junction_out_y))
    sch.add_wire(start=(junction_out_x, junction_out_y), end=c_out_pins[0][1])
    sch.add_wire(start=(junction_out_x, junction_out_y), end=v5_pins[0][1])

    # Wires - Ground
    sch.add_wire(start=c_in_pins[1][1], end=gnd_in_pins[0][1])
    sch.add_wire(start=u_pins[1][1], end=gnd_u_pins[0][1])
    sch.add_wire(start=c_out_pins[1][1], end=gnd_out_pins[0][1])

    # Rectangle
    rect_end_x = snap_to_grid(rect_x + GRID * 20.5)
    rect_end_y = snap_to_grid(rect_y + GRID * 17)
    sch.add_rectangle(start=(rect_x, rect_y), end=(rect_end_x, rect_end_y))

    # Text box with specs
    text_box_x = snap_to_grid(rect_x + GRID * 11)
    text_box_y = snap_to_grid(rect_end_y - GRID * 4.5)
    text_box_width = snap_to_grid(GRID * 8.5)
    text_box_height = snap_to_grid(GRID * 4)

    specs_text = "Input: 7-35V DC\nOutput: 5V @ 1.5A max\nDropout: ~2V min"
    sch.add_text_box(
        specs_text,
        position=(text_box_x, text_box_y),
        size=(text_box_width, text_box_height),
        font_size=1.27
    )

    return {u_ref: u, c_in_ref: c_in, c_out_ref: c_out}


# ============================================================================
# RC LOW-PASS FILTER CIRCUIT
# ============================================================================

def create_rc_filter(sch, x_offset: float, y_offset: float, instance: int = 1):
    """
    Create an RC low-pass filter circuit.

    Args:
        sch: Schematic object
        x_offset: X offset in mm
        y_offset: Y offset in mm
        instance: Circuit instance number

    Returns:
        dict: Dictionary of created components
    """
    import math

    GRID = 2.54

    rect_x = snap_to_grid(x_offset)
    rect_y = snap_to_grid(y_offset)

    # Generate unique references
    if instance == 1:
        r_ref, c_ref = "R3", "C3"
        pwr_ref = "#PWR06"
    else:
        r_ref = f"R{instance}3"
        c_ref = f"C{instance}3"
        pwr_ref = f"#PWR{instance}06"

    # Title
    title_x = snap_to_grid(rect_x + GRID * 7.75)
    title_y = snap_to_grid(rect_y + GRID * 2.1)
    sch.add_text("RC LOW-PASS FILTER", position=(title_x, title_y), size=2.0)

    # Signal line Y position
    signal_y = snap_to_grid(rect_y + GRID * 6.5)

    # Resistor position (horizontal)
    r_x = snap_to_grid(rect_x + GRID * 6.5)
    r_y = signal_y

    # Capacitor position (vertical)
    c_x = snap_to_grid(rect_x + GRID * 10.5)
    c_y = snap_to_grid(signal_y + GRID * 3.5)

    # Junction point
    junction_x = c_x
    junction_y = signal_y

    # Components
    r = sch.components.add("Device:R", r_ref, "1k", position=(r_x, r_y), rotation=90)
    c = sch.components.add("Device:C", c_ref, "100nF", position=(c_x, c_y))

    # GND power symbol
    gnd_x = c_x
    gnd_y = snap_to_grid(c_y + GRID * 1.5)
    sch.components.add("power:GND", pwr_ref, "GND", position=(gnd_x, gnd_y))

    # Labels
    in_label_x = snap_to_grid(rect_x + GRID * 3)
    in_label_y = signal_y
    out_label_x = snap_to_grid(rect_x + GRID * 13)
    out_label_y = signal_y

    sch.add_label("IN", position=(in_label_x, in_label_y))
    sch.add_label("OUT", position=(out_label_x, out_label_y))

    # Junction
    sch.junctions.add(position=(junction_x, junction_y))

    # Get pin positions
    r_pins = sch.list_component_pins(r_ref)
    c_pins = sch.list_component_pins(c_ref)
    gnd_pins = sch.list_component_pins(pwr_ref)

    # Determine left and right pins (rotation affects pin order)
    r_pin1_pos = r_pins[0][1]
    r_pin2_pos = r_pins[1][1]

    if r_pin1_pos.x < r_pin2_pos.x:
        r_left_pin = r_pin1_pos
        r_right_pin = r_pin2_pos
    else:
        r_left_pin = r_pin2_pos
        r_right_pin = r_pin1_pos

    # Wires
    sch.add_wire(start=(in_label_x, in_label_y), end=r_left_pin)
    sch.add_wire(start=r_right_pin, end=(junction_x, junction_y))
    sch.add_wire(start=(junction_x, junction_y), end=(out_label_x, out_label_y))
    sch.add_wire(start=(junction_x, junction_y), end=c_pins[0][1])
    sch.add_wire(start=c_pins[1][1], end=gnd_pins[0][1])

    # Calculate and display cutoff frequency
    R = 1000  # 1kΩ
    C = 100e-9  # 100nF
    fc = 1 / (2 * math.pi * R * C)

    fc_text_x = snap_to_grid(rect_x + GRID * 6.7)
    fc_text_y = snap_to_grid(rect_y + GRID * 16.5)
    formula_x = snap_to_grid(rect_x + GRID * 6.7)
    formula_y = snap_to_grid(rect_y + GRID * 18)

    sch.add_text(f"fc = {fc/1000:.2f} kHz", position=(fc_text_x, fc_text_y), size=1.27)
    sch.add_text("fc = 1/(2πRC)", position=(formula_x, formula_y), size=1.27)

    # Rectangle
    rect_end_x = snap_to_grid(rect_x + GRID * 17)
    rect_end_y = snap_to_grid(rect_y + GRID * 19.5)
    sch.add_rectangle(start=(rect_x, rect_y), end=(rect_end_x, rect_end_y))

    return {r_ref: r, c_ref: c}


# ============================================================================
# STM32 MICROPROCESSOR CIRCUIT
# ============================================================================

def create_stm32_microprocessor(sch, x_offset=0, y_offset=0, instance=1):
    """
    Create STM32G030K8Tx microprocessor circuit at specified position.

    Args:
        sch: Schematic object
        x_offset: X offset in mm
        y_offset: Y offset in mm
        instance: Circuit instance number

    Returns:
        dict: Dictionary of created components
    """
    # Original circuit origin
    ORIGIN_X = 72.39
    ORIGIN_Y = 43.815

    def pos(abs_x, abs_y):
        """Convert absolute position to offset position"""
        rel_x = abs_x - ORIGIN_X
        rel_y = abs_y - ORIGIN_Y
        return (snap_to_grid(x_offset + rel_x), snap_to_grid(y_offset + rel_y))

    # Reference designators
    base_num = (instance - 1) * 100
    u_ref = f'U{instance + 1}' if instance > 1 else 'U1'
    c_refs = [f'C{base_num + 10 + i}' for i in range(3)]
    r_refs = [f'R{base_num + 10 + i}' for i in range(2)]
    d_ref = f'D{base_num + 10}'
    j_ref = f'J{instance}'

    components = {}

    # Microcontroller
    components['mcu'] = sch.components.add(
        'MCU_ST_STM32G0:STM32G030K8Tx', u_ref, 'STM32G030K8Tx',
        position=pos(128.27, 110.49), rotation=0
    )

    # Resistors
    components['r_nrst'] = sch.components.add(
        'Device:R', r_refs[0], '10k',
        position=pos(91.44, 85.09), rotation=0
    )
    components['r_led'] = sch.components.add(
        'Device:R', r_refs[1], '330',
        position=pos(160.02, 101.6), rotation=0
    )

    # LED
    components['led'] = sch.components.add(
        'Device:LED', d_ref, 'GREEN',
        position=pos(160.02, 109.22), rotation=90
    )

    # Capacitors
    components['c_vdd1'] = sch.components.add(
        'Device:C', c_refs[0], '100nF',
        position=pos(138.43, 70.49), rotation=0  # Moved up 0.5 grid
    )
    components['c_vdd2'] = sch.components.add(
        'Device:C_Polarized', c_refs[1], '10uF',
        position=pos(149.86, 70.49), rotation=0  # Moved up 0.5 grid
    )
    components['c_nrst'] = sch.components.add(
        'Device:C', c_refs[2], '100nF',
        position=pos(96.52, 93.98), rotation=0
    )

    # Debug connector
    components['debug'] = sch.components.add(
        'Connector:Conn_01x04_Pin', j_ref, 'SWD',
        position=pos(184.15, 83.82), rotation=180
    )

    # Power symbols
    pwr_base = base_num + 20
    sch.components.add('power:+3.3V', f'#PWR{pwr_base:02d}', '+3.3V', position=pos(137.16, 63.5))
    sch.components.add('power:+3.3V', f'#PWR{pwr_base+1:02d}', '+3.3V', position=pos(173.99, 78.74))
    sch.components.add('power:+3.3V', f'#PWR{pwr_base+2:02d}', '+3.3V', position=pos(91.44, 78.74))
    sch.components.add('power:GND', f'#PWR{pwr_base+3:02d}', 'GND', position=pos(160.02, 116.84))
    sch.components.add('power:GND', f'#PWR{pwr_base+4:02d}', 'GND', position=pos(144.78, 74.3))  # Moved up 0.5 grid
    sch.components.add('power:GND', f'#PWR{pwr_base+5:02d}', 'GND', position=pos(128.27, 135.89))
    sch.components.add('power:GND', f'#PWR{pwr_base+6:02d}', 'GND', position=pos(96.52, 97.79))
    sch.components.add('power:GND', f'#PWR{pwr_base+7:02d}', 'GND', position=pos(177.8, 80.01), rotation=270)

    # Wiring
    wires = [
        # VDD power distribution
        ((138.43, 74.3), (144.78, 74.3)),  # GND rail moved up 0.5 grid
        ((144.78, 74.3), (149.86, 74.3)),  # GND rail moved up 0.5 grid
        ((128.27, 64.77), (137.16, 64.77)),
        ((137.16, 64.77), (138.43, 64.77)),
        ((138.43, 64.77), (149.86, 64.77)),
        ((128.27, 64.77), (128.27, 82.55)),
        ((137.16, 63.5), (137.16, 64.77)),
        ((138.43, 64.77), (138.43, 66.68)),  # Cap top pin moved up 0.5 grid
        ((149.86, 64.77), (149.86, 66.68)),  # Cap top pin moved up 0.5 grid
        # NRST circuit
        ((91.44, 88.9), (96.52, 88.9)),
        ((96.52, 88.9), (110.49, 88.9)),
        ((86.36, 88.9), (91.44, 88.9)),
        ((91.44, 81.28), (91.44, 78.74)),
        # LED circuit
        ((146.05, 95.25), (160.02, 95.25)),
        ((160.02, 95.25), (160.02, 97.79)),
        ((160.02, 105.41), (160.02, 105.41)),
        ((160.02, 113.03), (160.02, 116.84)),
        # Debug header
        ((173.99, 78.74), (179.07, 78.74)),
        ((177.8, 80.01), (179.07, 80.01)),
        ((172.72, 83.82), (179.07, 83.82)),
        ((172.72, 85.09), (179.07, 85.09)),
        # SWD signals
        ((148.59, 115.57), (146.05, 115.57)),
        ((148.59, 116.84), (146.05, 116.84)),
    ]

    for start, end in wires:
        sch.add_wire(start=pos(start[0], start[1]), end=pos(end[0], end[1]))

    # Labels
    labels = [
        ('NRST', (86.36, 88.9), 0),
        ('SWDIO', (148.59, 115.57), 0),
        ('SWCLK', (148.59, 116.84), 0),
        ('SWDIO', (172.72, 83.82), 0),
        ('SWCLK', (172.72, 85.09), 0),
    ]

    for text, (x, y), rotation in labels:
        sch.add_label(text, position=pos(x, y), rotation=rotation)

    # Graphical elements
    sch.add_rectangle(start=pos(72.39, 43.815), end=pos(193.04, 151.13))
    sch.add_rectangle(start=pos(161.29, 64.77), end=pos(187.325, 90.17))
    sch.add_text("STM32G030K8Tx MICROCONTROLLER", position=pos(131.572, 50.8), size=2.5)
    sch.add_text("ARM Cortex-M0+ @ 64MHz • 64KB Flash • 8KB RAM", position=pos(128.778, 147.32), size=1.27)
    sch.add_text("Debug", position=pos(173.482, 68.58), size=2.0)

    return components


# ============================================================================
# MAIN - CREATE DEMONSTRATION SCHEMATIC
# ============================================================================

def main():
    """Create a demonstration schematic with all parametric circuits."""

    print("=" * 80)
    print("🚀 kicad-sch-api Example Circuit")
    print("=" * 80)
    print()
    print("Creating demonstration schematic with parametric circuits...")
    print()

    # Create schematic
    sch = ksa.create_schematic("Example_Circuit")

    # Grid spacing for circuit placement
    CIRCUIT_GRID = 47  # grid units between circuits (≈60mm)
    START_X = 16  # grid units (≈20mm)
    START_Y = 16  # grid units

    print("📍 Placing circuits:")
    print("  Row 1: Voltage Divider | Power Supply | RC Filter")
    print("  Row 2: STM32 Microprocessor")
    print()

    # Row 1: Three circuits side by side
    print("  1. Voltage Divider...")
    create_voltage_divider(sch, START_X, START_Y, instance=1)

    print("  2. 5V Power Supply (LM7805)...")
    create_power_supply(sch, START_X + CIRCUIT_GRID, START_Y, instance=1)

    print("  3. RC Low-Pass Filter...")
    create_rc_filter(sch, START_X + CIRCUIT_GRID * 2.3, START_Y, instance=1)

    # Row 2: STM32 Microprocessor
    print("  4. STM32G030K8Tx Microprocessor...")
    circuit4_x_mm = START_X * 1.27
    circuit4_y_mm = (START_Y + int(CIRCUIT_GRID * 1.2)) * 1.27
    create_stm32_microprocessor(sch, circuit4_x_mm, circuit4_y_mm, instance=2)

    # Add explanation text box to the right
    print("  5. Adding explanation text box...")
    GRID = 1.27
    text_box_x = (START_X + CIRCUIT_GRID * 3.2) * GRID  # To the right of all circuits
    text_box_y = START_Y * GRID
    text_box_width = 50 * GRID  # ~63mm wide
    text_box_height = 80 * GRID  # ~102mm tall

    explanation_text = """STM32G030K8Tx BASIC CIRCUIT

This example demonstrates a complete minimal
STM32 microcontroller circuit with:

POWER SUPPLY:
• 3.3V input (from voltage regulator)
• 100nF decoupling capacitors (C110, C111)
• 10µF bulk capacitor for stability

RESET CIRCUIT:
• 10kΩ pull-up resistor to 3.3V
• 100nF capacitor for debouncing
• NRST pin protected from noise

LED INDICATOR:
• Green LED on PA7 GPIO pin
• 330Ω current limiting resistor
• Simple visual feedback circuit

DEBUG INTERFACE:
• 4-pin SWD header for programming
• SWDIO and SWCLK debug signals
• Standard ARM Cortex-M debug port

FEATURES:
• ARM Cortex-M0+ core @ 64MHz
• 64KB Flash memory
• 8KB SRAM
• Minimal external components
• Perfect for learning embedded systems

This circuit provides everything needed
for a basic STM32 project with programming,
debugging, and I/O capabilities."""

    sch.add_text_box(
        explanation_text,
        position=(text_box_x, text_box_y),
        size=(text_box_width, text_box_height),
        font_size=1.27
    )

    print()
    print("=" * 80)
    print("📊 Schematic Statistics:")
    print("=" * 80)

    # Count components
    resistors = len([c for c in sch.components if 'Device:R' in c.lib_id])
    capacitors = len([c for c in sch.components if 'Device:C' in c.lib_id or 'C_Polarized' in c.lib_id])
    regulators = len([c for c in sch.components if 'Regulator' in c.lib_id])
    mcus = len([c for c in sch.components if 'MCU' in c.lib_id or 'STM32' in c.lib_id])
    leds = len([c for c in sch.components if 'LED' in c.lib_id])
    connectors = len([c for c in sch.components if 'Connector' in c.lib_id])
    power_symbols = len([c for c in sch.components if c.reference.startswith('#PWR')])

    print(f"  • Total Components: {len(sch.components)}")
    print(f"    - Resistors: {resistors}")
    print(f"    - Capacitors: {capacitors}")
    print(f"    - Voltage Regulators: {regulators}")
    print(f"    - Microcontrollers: {mcus}")
    print(f"    - LEDs: {leds}")
    print(f"    - Connectors: {connectors}")
    print(f"    - Power Symbols: {power_symbols}")
    print(f"  • Wires: {len(sch.wires)}")
    print(f"  • Labels: {len(sch.labels)}")
    print(f"  • Junctions: {len(sch.junctions)}")
    print()

    # Save
    output_file = "example_circuit.kicad_sch"
    print(f"💾 Saving schematic to: {output_file}")
    sch.save(output_file)
    print(f"✅ Saved successfully!")
    print()

    print("=" * 80)
    print("🎉 Example Complete!")
    print("=" * 80)
    print()
    print("Circuits Included:")
    print("  1. ⚡ Voltage Divider - 10kΩ/10kΩ resistive divider")
    print("  2. 🔌 5V Power Supply - LM7805 linear regulator")
    print("  3. 📊 RC Low-Pass Filter - 1kΩ/100nF filter (fc = 1.59 kHz)")
    print("  4. 🖥️  STM32 Microprocessor - Complete MCU circuit")
    print()
    print("Features Demonstrated:")
    print("  ✅ Parametric circuit functions (reusable at any position)")
    print("  ✅ Grid-based positioning with integer coordinates")
    print("  ✅ Automatic wire routing with pin position queries")
    print("  ✅ Power symbols and labels")
    print("  ✅ Grouping rectangles for visual organization")
    print()
    print(f"Open in KiCAD:  open {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
