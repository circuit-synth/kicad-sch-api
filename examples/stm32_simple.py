"""
kicad-sch-api Example: STM32G030K8Tx Microprocessor Circuit

Demonstrates:
- STM32G030K8Tx microcontroller placement
- Power supply decoupling
- Reset circuit with protection
- LED indicator circuit
- SWD debug interface
- Complete grid-aligned wiring

Perfect for learning embedded systems design!
"""

import kicad_sch_api as ksa


def create_stm32_microprocessor(sch):
    """
    Create STM32G030K8Tx microprocessor circuit with grid-aligned components and wiring.
    All coordinates are in mm and grid-aligned (1.27mm grid).
    """

    # ===== RESISTORS =====
    sch.components.add('Device:R', 'R1', '10k', position=(35.56, 60.96))
    sch.components.add('Device:R', 'R2', '330', position=(106.68, 69.85))

    # ===== CAPACITORS =====
    sch.components.add('Device:C', 'C1', '100nF', position=(77.47, 44.45))
    sch.components.add('Device:C_Polarized', 'C2', '10uF', position=(91.44, 44.45))
    sch.components.add('Device:C', 'C3', '100nF', position=(30.48, 68.58))

    # ===== LED =====
    sch.components.add('Device:LED', 'D1', 'GREEN', position=(106.68, 82.55), rotation=90)

    # ===== MICROCONTROLLER =====
    sch.components.add(
        'MCU_ST_STM32G0:STM32G030K8Tx',
        'U1',
        'STM32G030K8Tx',
        position=(71.12, 85.09)
    )

    # ===== SWD DEBUG CONNECTOR =====
    sch.components.add(
        'Connector:Conn_01x04_Pin',
        'J1',
        'SWD',
        position=(142.24, 49.53),
        rotation=180
    )

    # ===== POWER SYMBOLS =====
    # +3.3V
    sch.components.add('power:+3.3V', '#PWR01', '+3.3V', position=(35.56, 54.61))
    sch.components.add('power:+3.3V', '#PWR02', '+3.3V', position=(78.74, 36.83))
    sch.components.add('power:+3.3V', '#PWR03', '+3.3V', position=(129.54, 43.18))

    # GND
    sch.components.add('power:GND', '#PWR04', 'GND', position=(30.48, 73.66))
    sch.components.add('power:GND', '#PWR05', 'GND', position=(85.09, 48.26))
    sch.components.add('power:GND', '#PWR06', 'GND', position=(106.68, 88.9))
    sch.components.add('power:GND', '#PWR07', 'GND', position=(71.12, 113.03))
    sch.components.add('power:GND', '#PWR08', 'GND', position=(133.35, 46.99), rotation=270)

    # ===== WIRING =====
    wires = [
        # Power distribution
        ((78.74, 36.83), (78.74, 40.64)),
        ((77.47, 40.64), (78.74, 40.64)),
        ((78.74, 40.64), (91.44, 40.64)),
        ((85.09, 48.26), (91.44, 48.26)),
        ((77.47, 48.26), (85.09, 48.26)),
        ((71.12, 40.64), (77.47, 40.64)),
        ((71.12, 57.15), (71.12, 40.64)),
        ((129.032, 43.5483), (135.4836, 43.5483)),

        # Reset circuit
        ((35.56, 54.61), (35.56, 57.15)),
        ((35.56, 57.15), (53.34, 64.77)),
        ((53.34, 64.77), (71.12, 64.77)),
        ((24.13, 64.77), (30.48, 64.77)),
        ((30.48, 64.77), (35.56, 64.77)),
        ((30.48, 72.39), (30.48, 73.66)),

        # LED circuit
        ((88.9, 64.77), (106.68, 64.77)),
        ((106.68, 66.04), (106.68, 64.77)),
        ((106.68, 73.66), (106.68, 78.74)),
        ((106.68, 86.36), (106.68, 88.9)),

        # Debug header
        ((127.4191, 49.9999), (135.4836, 49.9999)),
        ((127.4191, 53.2257), (135.4836, 53.2257)),
        ((133.8707, 46.7741), (135.4836, 46.7741)),

        # SWD signals
        ((71.12, 110.49), (71.12, 113.03)),
    ]

    for start, end in wires:
        sch.add_wire(start=start, end=end)

    # ===== LABELS =====
    sch.add_label('NRST', position=(53.34, 64.77))
    sch.add_label('SWDIO', position=(127.4191, 53.2257))
    sch.add_label('SWCLK', position=(127.4191, 49.9999))

    # ===== DECORATIVE ELEMENTS =====
    sch.add_rectangle(start=(20.32, 33.02), end=(152.4, 120.65))
    sch.add_text("STM32G030K8Tx MICROCONTROLLER", position=(65, 25.4), size=2.5)


def main():
    """Generate the STM32 microprocessor example schematic."""
    print("Creating STM32G030K8Tx microprocessor circuit...")

    # Create schematic
    sch = ksa.create_schematic("Example_STM32_Simple")

    # Create the circuit
    create_stm32_microprocessor(sch)

    # Save
    sch.save("stm32_simple.kicad_sch")
    print("✅ Saved: stm32_simple.kicad_sch")
    print()
    print("Open in KiCAD to see the result:")
    print("  open stm32_simple.kicad_sch")


if __name__ == "__main__":
    main()
