"""
kicad-sch-api Example: STM32G030K8Tx Microprocessor Circuit

Demonstrates:
- STM32G030K8Tx microcontroller placement
- Power supply decoupling
- Reset circuit with protection
- LED indicator circuit
- SWD debug interface
- Complete grid-aligned wiring using grid units for intuitive positioning

Perfect for learning embedded systems design!
Grid-based positioning makes it easy to adjust layout - all positions in grid units!
"""

import kicad_sch_api as ksa

# KiCAD standard grid
GRID = 1.27  # mm


def p(x_grid, y_grid):
    """Convert grid units to mm. Makes code much more readable!"""
    return (x_grid * GRID, y_grid * GRID)


def create_stm32_microprocessor(sch):
    """
    Create STM32G030K8Tx microprocessor circuit with grid-aligned components.
    All positions are specified in GRID UNITS (1.27mm each) for intuitive layout.
    This makes it easy to adjust positions - just change grid numbers!
    """

    # ===== RESISTORS =====
    sch.components.add("Device:R", "R1", "10k", position=p(28, 48))
    sch.components.add("Device:R", "R2", "330", position=p(84, 55))

    # ===== CAPACITORS =====
    sch.components.add("Device:C", "C1", "100nF", position=p(61, 35))
    sch.components.add("Device:C_Polarized", "C2", "10uF", position=p(72, 35))
    sch.components.add("Device:C", "C3", "100nF", position=p(30, 54))

    # ===== LED =====
    sch.components.add("Device:LED", "D1", "GREEN", position=p(84, 65), rotation=90)

    # ===== MICROCONTROLLER =====
    sch.components.add(
        "MCU_ST_STM32G0:STM32G030K8Tx", "U1", "STM32G030K8Tx", position=p(56, 67)
    )

    # ===== SWD DEBUG CONNECTOR =====
    sch.components.add(
        "Connector:Conn_01x04_Pin", "J1", "SWD", position=p(112, 39), rotation=180
    )

    # ===== POWER SYMBOLS =====
    # +3.3V
    sch.components.add("power:+3.3V", "#PWR01", "+3.3V", position=p(28, 43))
    sch.components.add("power:+3.3V", "#PWR02", "+3.3V", position=p(62, 29))
    sch.components.add("power:+3.3V", "#PWR03", "+3.3V", position=p(102, 35))

    # GND
    sch.components.add("power:GND", "#PWR04", "GND", position=p(24, 58))
    sch.components.add("power:GND", "#PWR05", "GND", position=p(67, 38))
    sch.components.add("power:GND", "#PWR06", "GND", position=p(84, 70))
    sch.components.add("power:GND", "#PWR07", "GND", position=p(56, 89))
    sch.components.add("power:GND", "#PWR08", "GND", position=p(105, 37), rotation=270)

    # ===== WIRING WITH AUTO-ROUTING =====
    # Power supply (VDD) distribution
    sch.add_wire(start=p(62, 29), end=p(62, 32))  # From VDD symbol down to power rail
    sch.add_wire(start=p(61, 32), end=p(62, 32))  # C1 to power rail
    sch.add_wire(start=p(62, 32), end=p(72, 32))  # Power rail to C2
    sch.add_wire(start=p(56, 32), end=p(61, 32))  # MCU VDD to C1
    sch.add_wire(start=p(56, 45), end=p(56, 32))  # MCU pin to power
    sch.add_wire(start=p(67, 38), end=p(72, 38))  # GND to C2
    sch.add_wire(start=p(61, 38), end=p(67, 38))  # C1 to GND

    # Reset circuit (NRST)
    sch.add_wire(start=p(28, 43), end=p(28, 45))  # VDD to R1
    sch.add_wire(start=p(42, 45), end=p(50, 51))  # R1 to junction
    sch.add_wire(start=p(42, 51), end=p(56, 51))  # Junction to MCU NRST
    sch.add_wire(start=p(19, 51), end=p(24, 51))  # External to C3
    sch.add_wire(start=p(24, 51), end=p(28, 51))  # C3 to R1
    sch.add_wire(start=p(24, 57), end=p(24, 58))  # C3 to GND

    # LED indicator circuit
    sch.add_wire(start=p(70, 51), end=p(84, 51))  # MCU PA0 to R2
    sch.add_wire(start=p(84, 52), end=p(84, 51))  # R2 to LED anode
    sch.add_wire(start=p(84, 58), end=p(84, 62))  # LED cathode down
    sch.add_wire(start=p(84, 68), end=p(84, 70))  # LED to GND

    # Debug header (SWD connector) - pins are on left side due to 180° rotation
    sch.add_wire(start=p(100, 38), end=p(112, 38))  # SWCLK
    sch.add_wire(start=p(100, 40), end=p(112, 40))  # SWDIO
    sch.add_wire(start=p(104, 36), end=p(112, 36))  # GND to header
    sch.add_wire(start=p(101, 34), end=p(112, 34))  # VDD to header

    # Ground connections
    sch.add_wire(start=p(56, 87), end=p(56, 89))  # MCU GND to GND symbol

    # ===== LABELS =====
    sch.add_label("NRST", position=p(42, 51))
    sch.add_label("SWDIO", position=p(100, 40))
    sch.add_label("SWCLK", position=p(100, 38))

    # ===== DECORATIVE ELEMENTS =====
    sch.add_rectangle(start=p(16, 26), end=p(120, 95))
    sch.add_text("STM32G030K8Tx MICROCONTROLLER", position=p(51, 20), size=2.5)


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
