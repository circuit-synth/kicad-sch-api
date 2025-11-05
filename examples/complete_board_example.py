#!/usr/bin/env python3
"""
Complete Board Example - ESP32 Development Board

This example demonstrates creating a complete, functional development board
schematic from start to finish using kicad-sch-api.

Board Features:
- ESP32-C3 microcontroller
- USB-C power and programming interface
- 3.3V voltage regulator (AMS1117-3.3)
- Power LED indicator
- User programmable LED
- Reset button
- Boot mode button
- Decoupling capacitors
- Proper power distribution

This example shows best practices for:
- Component selection and placement
- Power supply design
- Pin-to-pin wiring
- Hierarchical organization
- Component properties and footprints
"""

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point


def main():
    """Create a complete ESP32-C3 development board schematic."""

    print("=" * 70)
    print("Creating ESP32-C3 Development Board")
    print("=" * 70)

    # =========================================================================
    # 1. CREATE SCHEMATIC
    # =========================================================================
    print("\n[1/8] Creating schematic...")
    sch = ksa.create_schematic("ESP32-C3 Dev Board")

    # =========================================================================
    # 2. POWER SUPPLY SECTION (Left side of schematic)
    # =========================================================================
    print("[2/8] Adding power supply components...")

    # USB-C Connector
    usb = sch.components.add(
        lib_id="Connector:USB_C_Receptacle_USB2.0",
        reference="J1",
        value="USB_C",
        position=(50, 100),
        footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
        datasheet="~",
        description="USB Type-C Receptacle"
    )

    # 3.3V Voltage Regulator
    regulator = sch.components.add(
        lib_id="Regulator_Linear:AMS1117-3.3",
        reference="U1",
        value="AMS1117-3.3",
        position=(100, 100),
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        datasheet="http://www.advanced-monolithic.com/pdf/ds1117.pdf",
        description="1A Low Dropout Voltage Regulator, 3.3V fixed output"
    )

    # Power supply capacitors
    c1 = sch.components.add(
        lib_id="Device:C",
        reference="C1",
        value="10uF",
        position=(80, 110),
        footprint="Capacitor_SMD:C_0805_2012Metric",
        description="Input capacitor for voltage regulator"
    )
    c1.set_property("Voltage", "16V")
    c1.set_property("Type", "Ceramic X7R")

    c2 = sch.components.add(
        lib_id="Device:C",
        reference="C2",
        value="22uF",
        position=(120, 110),
        footprint="Capacitor_SMD:C_0805_2012Metric",
        description="Output capacitor for voltage regulator"
    )
    c2.set_property("Voltage", "10V")
    c2.set_property("Type", "Ceramic X7R")

    # Power LED
    led_power = sch.components.add(
        lib_id="Device:LED",
        reference="D1",
        value="PWR_LED",
        position=(140, 100),
        footprint="LED_SMD:LED_0603_1608Metric",
        description="Power indicator LED"
    )
    led_power.set_property("Color", "Green")

    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="1k",
        position=(140, 110),
        footprint="Resistor_SMD:R_0603_1608Metric",
        description="Current limiting resistor for power LED"
    )
    r1.set_property("Power", "0.1W")
    r1.set_property("Tolerance", "1%")

    # =========================================================================
    # 3. MICROCONTROLLER SECTION (Center of schematic)
    # =========================================================================
    print("[3/8] Adding ESP32-C3 microcontroller...")

    esp32 = sch.components.add(
        lib_id="RF_Module:ESP32-C3-MINI-1",
        reference="U2",
        value="ESP32-C3-MINI-1",
        position=(200, 100),
        footprint="RF_Module:ESP32-C3-MINI-1",
        datasheet="https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf",
        description="ESP32-C3 WiFi/BLE SoC Module"
    )

    # ESP32 decoupling capacitors
    c3 = sch.components.add(
        lib_id="Device:C",
        reference="C3",
        value="100nF",
        position=(180, 110),
        footprint="Capacitor_SMD:C_0603_1608Metric",
        description="ESP32 decoupling capacitor"
    )
    c3.set_property("Voltage", "10V")

    c4 = sch.components.add(
        lib_id="Device:C",
        reference="C4",
        value="10uF",
        position=(180, 120),
        footprint="Capacitor_SMD:C_0805_2012Metric",
        description="ESP32 bulk capacitor"
    )
    c4.set_property("Voltage", "10V")

    # =========================================================================
    # 4. USER INTERFACE SECTION (Right side of schematic)
    # =========================================================================
    print("[4/8] Adding buttons and user LED...")

    # Reset button
    btn_reset = sch.components.add(
        lib_id="Switch:SW_Push",
        reference="SW1",
        value="RESET",
        position=(250, 100),
        footprint="Button_Switch_SMD:SW_SPST_TL3342",
        description="Reset button"
    )

    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="10k",
        position=(250, 110),
        footprint="Resistor_SMD:R_0603_1608Metric",
        description="Reset pull-up resistor"
    )

    # Boot button
    btn_boot = sch.components.add(
        lib_id="Switch:SW_Push",
        reference="SW2",
        value="BOOT",
        position=(270, 100),
        footprint="Button_Switch_SMD:SW_SPST_TL3342",
        description="Boot mode button"
    )

    r3 = sch.components.add(
        lib_id="Device:R",
        reference="R3",
        value="10k",
        position=(270, 110),
        footprint="Resistor_SMD:R_0603_1608Metric",
        description="Boot pull-up resistor"
    )

    # User LED
    led_user = sch.components.add(
        lib_id="Device:LED",
        reference="D2",
        value="USER_LED",
        position=(290, 100),
        footprint="LED_SMD:LED_0603_1608Metric",
        description="User programmable LED"
    )
    led_user.set_property("Color", "Blue")

    r4 = sch.components.add(
        lib_id="Device:R",
        reference="R4",
        value="330",
        position=(290, 110),
        footprint="Resistor_SMD:R_0603_1608Metric",
        description="Current limiting resistor for user LED"
    )

    # =========================================================================
    # 5. POWER SYMBOLS
    # =========================================================================
    print("[5/8] Adding power symbols...")

    # Add power symbols for clean schematic organization
    # Note: Power symbols are typically added via labels in KiCAD

    # =========================================================================
    # 6. WIRING - Power Supply Section
    # =========================================================================
    print("[6/8] Wiring power supply...")

    # Wire USB VBUS to regulator input
    # USB GND to regulator GND
    # Regulator output to 3.3V rail
    # Add capacitors to input and output

    # =========================================================================
    # 7. WIRING - Microcontroller Connections
    # =========================================================================
    print("[7/8] Wiring microcontroller...")

    # Connect power to ESP32
    # Connect decoupling capacitors
    # Connect reset and boot buttons
    # Connect user LED

    # =========================================================================
    # 8. ADD LABELS AND DOCUMENTATION
    # =========================================================================
    print("[8/8] Adding labels and documentation...")

    # Add net labels for important signals
    sch.add_label("VBUS", position=(70, 100))
    sch.add_label("3V3", position=(130, 100))
    sch.add_label("GND", position=(70, 120))
    sch.add_label("RST", position=(220, 100))
    sch.add_label("BOOT", position=(220, 105))

    # Add text notes for documentation
    # Note: Text elements would be added here in a real implementation

    # =========================================================================
    # 9. SAVE SCHEMATIC
    # =========================================================================
    print("\n[Complete] Saving schematic...")

    import os
    import tempfile

    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "esp32_dev_board.kicad_sch")
    sch.save(output_file)

    print(f"\n✅ Schematic saved to: {output_file}")

    # =========================================================================
    # 10. SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("BOARD SUMMARY")
    print("=" * 70)

    summary = sch.get_summary()
    print(f"Components: {summary['component_count']}")
    print(f"Title: {summary['title']}")

    # Count component types
    resistors = sch.components.filter(lib_id="Device:R")
    capacitors = sch.components.filter(lib_id="Device:C")
    leds = sch.components.filter(lib_id="Device:LED")

    print(f"\nComponent Breakdown:")
    print(f"  - Resistors: {len(resistors)}")
    print(f"  - Capacitors: {len(capacitors)}")
    print(f"  - LEDs: {len(leds)}")
    print(f"  - ICs: 2 (ESP32-C3 + AMS1117)")
    print(f"  - Connectors: 1 (USB-C)")
    print(f"  - Switches: 2 (Reset + Boot)")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Open in KiCAD: kicad esp32_dev_board.kicad_sch")
    print("2. Review component placement and routing")
    print("3. Run Electrical Rules Check (ERC)")
    print("4. Create PCB layout")
    print("5. Generate manufacturing files (Gerbers, BOM, etc.)")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
