#!/usr/bin/env python3
"""Fixed resistor divider with proper pin connections."""

import kicad_sch_api as ksa

def main():
    # Create schematic
    sch = ksa.create_schematic("Resistor Divider Fixed")

    # Add power symbols
    pwr_3v3 = sch.components.add(
        lib_id="power:+3.3V",
        reference="#PWR02",
        value="+3.3V",
        position=(91.44, 69.85),
    )

    gnd = sch.components.add(
        lib_id="power:GND",
        reference="#PWR01",
        value="GND",
        position=(91.44, 95.25),
    )

    # Add resistors
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(91.44, 73.66),
    )

    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="10k",
        position=(91.44, 91.44),
    )

    # Get actual pin positions for reference
    r1_pins = sch._wire_manager.list_component_pins('R1')
    r2_pins = sch._wire_manager.list_component_pins('R2')

    print("R1 pins:", r1_pins)
    print("R2 pins:", r2_pins)

    # R1 pins: [('1', Point(x=91.44, y=77.47)), ('2', Point(x=91.44, y=69.85))]
    # R2 pins: [('1', Point(x=91.44, y=95.25)), ('2', Point(x=91.44, y=87.63))]

    # Connect using pin-to-pin wiring:
    # 1. Connect R1 pin 1 to R2 pin 2 (voltage divider junction)
    wire1_uuid = sch.add_wire_between_pins("R1", "1", "R2", "2")

    # Add junction at the voltage divider midpoint
    junction_pos = (91.44, 82.55)  # Midpoint between R1 pin 1 and R2 pin 2
    sch.junctions.add(position=junction_pos, diameter=0, color=(0, 0, 0, 0))

    # 2. Connect from junction to VOUT label position
    vout_pos = (100.33, 82.55)  # Adjusted to match junction height
    sch.wires.add(start=junction_pos, end=vout_pos)

    # Add VOUT label
    sch.add_label(text="VOUT", position=vout_pos, rotation=0, size=1.27)

    print("✅ Created properly connected resistor divider")

    sch.save("fixed_resistor_divider.kicad_sch")

    import subprocess
    subprocess.run(["open", "fixed_resistor_divider.kicad_sch"])

if __name__ == "__main__":
    main()