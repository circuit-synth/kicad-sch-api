#!/usr/bin/env python3
"""
Complete kicad-sch-api Example

Demonstrates all major features in one comprehensive example.
"""

import os
import kicad_sch_api as ksa


def main():
    """Create a complete schematic demonstrating all features."""

    # Create schematic
    sch = ksa.create_schematic("Example Circuit")

    # =========================================================================
    # 1. Add Components
    # =========================================================================

    # Microcontroller
    mcu = sch.components.add(
        "MCU_ST_STM32F4:STM32F411CEUx", "U1", "STM32F411CEU6",
        position=(100, 100),
        footprint="Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm"
    )

    # Voltage regulator
    reg = sch.components.add(
        "Regulator_Linear:AMS1117-3.3", "U2", "AMS1117-3.3",
        position=(50, 100),
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2"
    )

    # Resistors
    r1 = sch.components.add("Device:R", "R1", "10k", (150, 100),
                           footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = sch.components.add("Device:R", "R2", "1k", (150, 110),
                           footprint="Resistor_SMD:R_0603_1608Metric")

    # Capacitors
    c1 = sch.components.add("Device:C", "C1", "100nF", (70, 110),
                           footprint="Capacitor_SMD:C_0603_1608Metric")
    c2 = sch.components.add("Device:C", "C2", "10uF", (80, 110),
                           footprint="Capacitor_SMD:C_0805_2012Metric")

    # LED
    led = sch.components.add("Device:LED", "D1", "LED", (170, 100),
                            footprint="LED_SMD:LED_0603_1608Metric")

    # Button
    btn = sch.components.add("Switch:SW_Push", "SW1", "RESET", (120, 120),
                            footprint="Button_Switch_SMD:SW_SPST_TL3342")

    # Connector
    conn = sch.components.add("Connector_Generic:Conn_01x04", "J1", "SWD",
                             position=(50, 120),
                             footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")

    # =========================================================================
    # 2. Set Component Properties
    # =========================================================================

    r1.set_property("Power", "0.1W")
    r1.set_property("Tolerance", "1%")

    c1.set_property("Voltage", "50V")
    c2.set_property("Voltage", "16V")

    led.set_property("Color", "Blue")

    # =========================================================================
    # 3. Add Wires
    # =========================================================================

    # Simple wire
    sch.wires.add(start=(90, 100), end=(95, 100))

    # Pin-to-pin wire (automatic position calculation)
    sch.add_wire_between_pins("R1", "2", "D1", "1")

    # =========================================================================
    # 4. Add Labels
    # =========================================================================

    sch.add_label("3V3", position=(85, 100))
    sch.add_label("GND", position=(70, 120))
    sch.add_label("SWDIO", position=(55, 120))
    sch.add_label("SWCLK", position=(55, 125))

    # Hierarchical label
    sch.add_hierarchical_label("VCC", position=(40, 100), shape="input")

    # =========================================================================
    # 5. Add Text
    # =========================================================================

    sch.add_text("Example Circuit v1.0", position=(150, 50))

    # =========================================================================
    # 6. Filter and Search Components
    # =========================================================================

    # Find all resistors
    resistors = sch.components.filter(lib_id="Device:R")
    print(f"Resistors: {len(resistors)}")

    # Find specific component
    mcu_found = sch.components.get("U1")
    print(f"Found MCU: {mcu_found.reference}")

    # Find by value
    ten_k = sch.components.filter(value="10k")
    print(f"10k components: {len(ten_k)}")

    # =========================================================================
    # 7. Bulk Operations
    # =========================================================================

    # Update all resistors at once
    sch.components.bulk_update(
        criteria={'lib_id': 'Device:R'},
        updates={'properties': {'Tolerance': '1%', 'Power': '0.1W'}}
    )

    # =========================================================================
    # 8. Validation
    # =========================================================================

    issues = sch.validate()
    print(f"Validation issues: {len(issues)}")
    for issue in issues:
        if issue.level.value == "error":
            print(f"  ERROR: {issue.message}")

    # =========================================================================
    # 9. Save Schematic
    # =========================================================================

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "example.kicad_sch")

    sch.save(output_file)

    print(f"\n✅ Created schematic: {output_file}")
    print(f"   Components: {len(sch.components)}")
    print(f"   Wires: {len(sch.wires)}")


if __name__ == "__main__":
    main()
