#!/usr/bin/env python3
"""
STM32F411 Black Pill Development Board Example

Based on Phil's Lab #65 KiCad STM32 PCB Design Tutorial and the popular
WeAct STM32F411CEU6 "Black Pill" development board.

This example creates a complete STM32F411-based development board with:
- STM32F411CEU6 microcontroller (ARM Cortex-M4 @ 100MHz)
- USB Type-C connector for power and programming
- 3.3V voltage regulator
- 25MHz HSE crystal oscillator
- 32.768kHz LSE crystal for RTC
- User LED (PC13)
- User button (PA0)
- BOOT0 button
- NRST (Reset) button
- SWD programming interface
- All GPIO broken out to headers

Board Specifications:
- MCU: STM32F411CEU6 (100MHz, 512KB Flash, 128KB RAM)
- Power: USB-C 5V input, 3.3V regulated output
- Crystals: 25MHz main, 32.768kHz RTC
- Programming: SWD interface (ST-Link compatible)
- I/O: All pins broken out to dual 20-pin headers

Reference: Phil's Lab #65 - KiCad 6 STM32 PCB Design Full Tutorial
"""

import kicad_sch_api as ksa


def main():
    """Create STM32F411 Black Pill development board schematic."""

    print("=" * 70)
    print("STM32F411 Black Pill Development Board")
    print("Based on Phil's Lab #65 Tutorial")
    print("=" * 70)

    # Create schematic
    sch = ksa.create_schematic("STM32F411 Black Pill")

    # =========================================================================
    # 1. MICROCONTROLLER - Center of schematic
    # =========================================================================
    print("\n[1/9] Adding STM32F411CEU6 microcontroller...")

    mcu = sch.components.add(
        lib_id="MCU_ST_STM32F4:STM32F411CEUx",
        reference="U1",
        value="STM32F411CEU6",
        position=(150, 150),
        footprint="Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm",
        datasheet="https://www.st.com/resource/en/datasheet/stm32f411ce.pdf",
        description="ARM Cortex-M4 100MHz, 512KB Flash, 128KB RAM"
    )

    # =========================================================================
    # 2. POWER SUPPLY - Left side
    # =========================================================================
    print("[2/9] Adding power supply components...")

    # USB Type-C connector
    usb = sch.components.add(
        lib_id="Connector:USB_C_Receptacle_USB2.0",
        reference="J1",
        value="USB_C",
        position=(50, 100),
        footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
        description="USB Type-C receptacle for power and data"
    )

    # 3.3V LDO Regulator (AMS1117-3.3 or XC6206P332MR)
    regulator = sch.components.add(
        lib_id="Regulator_Linear:AMS1117-3.3",
        reference="U2",
        value="AMS1117-3.3",
        position=(100, 100),
        footprint="Package_TO_SOT_SMD:SOT-223-3_TabPin2",
        datasheet="http://www.advanced-monolithic.com/pdf/ds1117.pdf",
        description="1A 3.3V Low Dropout Linear Regulator"
    )

    # Input capacitor (10uF)
    c1 = sch.components.add(
        lib_id="Device:C",
        reference="C1",
        value="10uF",
        position=(80, 110),
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    c1.set_property("Voltage", "16V")
    c1.set_property("Type", "Ceramic X7R")

    # Output capacitor (22uF)
    c2 = sch.components.add(
        lib_id="Device:C",
        reference="C2",
        value="22uF",
        position=(120, 110),
        footprint="Capacitor_SMD:C_0805_2012Metric"
    )
    c2.set_property("Voltage", "10V")
    c2.set_property("Type", "Ceramic X7R")

    # Power LED with current limiting resistor
    led_power = sch.components.add(
        lib_id="Device:LED",
        reference="D1",
        value="PWR_LED",
        position=(140, 100),
        footprint="LED_SMD:LED_0603_1608Metric"
    )
    led_power.set_property("Color", "Red")

    r_led_power = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="1k",
        position=(140, 110),
        footprint="Resistor_SMD:R_0603_1608Metric"
    )

    # =========================================================================
    # 3. DECOUPLING CAPACITORS - Around MCU
    # =========================================================================
    print("[3/9] Adding decoupling capacitors...")

    # Multiple 100nF decoupling capacitors for each VDD pin
    decoupling_caps = []
    for i in range(4):
        cap = sch.components.add(
            lib_id="Device:C",
            reference=f"C{i+3}",  # C3, C4, C5, C6
            value="100nF",
            position=(130 + i*10, 130),
            footprint="Capacitor_SMD:C_0603_1608Metric"
        )
        cap.set_property("Voltage", "16V")
        cap.set_property("Type", "Ceramic X7R")
        decoupling_caps.append(cap)

    # 1uF bulk capacitor
    c_bulk = sch.components.add(
        lib_id="Device:C",
        reference="C7",
        value="1uF",
        position=(170, 130),
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )
    c_bulk.set_property("Voltage", "16V")

    # =========================================================================
    # 4. HIGH SPEED EXTERNAL CRYSTAL (HSE) - 25MHz
    # =========================================================================
    print("[4/9] Adding 25MHz HSE crystal...")

    # 25MHz crystal
    crystal_hse = sch.components.add(
        lib_id="Device:Crystal_GND24",
        reference="Y1",
        value="25MHz",
        position=(120, 150),
        footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
        description="25MHz High Speed External crystal"
    )

    # Crystal load capacitors (20pF typical for 25MHz 9pF crystal)
    c_hse1 = sch.components.add(
        lib_id="Device:C",
        reference="C8",
        value="20pF",
        position=(110, 155),
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )

    c_hse2 = sch.components.add(
        lib_id="Device:C",
        reference="C9",
        value="20pF",
        position=(130, 155),
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )

    # =========================================================================
    # 5. LOW SPEED EXTERNAL CRYSTAL (LSE) - 32.768kHz for RTC
    # =========================================================================
    print("[5/9] Adding 32.768kHz LSE crystal...")

    crystal_lse = sch.components.add(
        lib_id="Device:Crystal",
        reference="Y2",
        value="32.768kHz",
        position=(120, 170),
        footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
        description="32.768kHz Low Speed External crystal for RTC"
    )

    # LSE load capacitors (6.5pF for 32.768kHz 6pF crystal)
    c_lse1 = sch.components.add(
        lib_id="Device:C",
        reference="C10",
        value="6.5pF",
        position=(110, 175),
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )

    c_lse2 = sch.components.add(
        lib_id="Device:C",
        reference="C11",
        value="6.5pF",
        position=(130, 175),
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )

    # =========================================================================
    # 6. BOOT AND RESET CIRCUITRY
    # =========================================================================
    print("[6/9] Adding BOOT0 and NRST buttons...")

    # BOOT0 button (with pull-down resistor)
    btn_boot = sch.components.add(
        lib_id="Switch:SW_Push",
        reference="SW1",
        value="BOOT0",
        position=(180, 180),
        footprint="Button_Switch_SMD:SW_SPST_TL3342",
        description="BOOT0 mode selection button"
    )

    r_boot = sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="10k",
        position=(180, 190),
        footprint="Resistor_SMD:R_0603_1608Metric",
        description="BOOT0 pull-down resistor"
    )

    # NRST (Reset) button with pull-up resistor
    btn_reset = sch.components.add(
        lib_id="Switch:SW_Push",
        reference="SW2",
        value="RESET",
        position=(200, 180),
        footprint="Button_Switch_SMD:SW_SPST_TL3342",
        description="NRST reset button"
    )

    r_reset = sch.components.add(
        lib_id="Device:R",
        reference="R3",
        value="10k",
        position=(200, 170),
        footprint="Resistor_SMD:R_0603_1608Metric",
        description="NRST pull-up resistor"
    )

    # Reset capacitor for clean reset
    c_reset = sch.components.add(
        lib_id="Device:C",
        reference="C12",
        value="100nF",
        position=(210, 180),
        footprint="Capacitor_SMD:C_0603_1608Metric"
    )

    # =========================================================================
    # 7. USER LED AND BUTTON
    # =========================================================================
    print("[7/9] Adding user LED (PC13) and button (PA0)...")

    # User LED on PC13 (active low)
    led_user = sch.components.add(
        lib_id="Device:LED",
        reference="D2",
        value="USER_LED",
        position=(220, 150),
        footprint="LED_SMD:LED_0603_1608Metric"
    )
    led_user.set_property("Color", "Blue")

    r_led_user = sch.components.add(
        lib_id="Device:R",
        reference="R4",
        value="1k",
        position=(220, 160),
        footprint="Resistor_SMD:R_0603_1608Metric"
    )

    # User button on PA0
    btn_user = sch.components.add(
        lib_id="Switch:SW_Push",
        reference="SW3",
        value="USER",
        position=(220, 130),
        footprint="Button_Switch_SMD:SW_SPST_TL3342",
        description="User button on PA0"
    )

    r_user = sch.components.add(
        lib_id="Device:R",
        reference="R5",
        value="10k",
        position=(220, 140),
        footprint="Resistor_SMD:R_0603_1608Metric",
        description="User button pull-down"
    )

    # =========================================================================
    # 8. SWD PROGRAMMING INTERFACE
    # =========================================================================
    print("[8/9] Adding SWD programming connector...")

    # 4-pin SWD connector (3.3V, SWDIO, SWCLK, GND)
    swd_connector = sch.components.add(
        lib_id="Connector:Conn_01x04",
        reference="J2",
        value="SWD",
        position=(50, 150),
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        description="SWD programming interface"
    )

    # =========================================================================
    # 9. GPIO HEADER CONNECTORS
    # =========================================================================
    print("[9/9] Adding GPIO headers...")

    # Left side header (20 pins)
    header_left = sch.components.add(
        lib_id="Connector:Conn_01x20",
        reference="J3",
        value="GPIO_LEFT",
        position=(50, 200),
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x20_P2.54mm_Vertical"
    )

    # Right side header (20 pins)
    header_right = sch.components.add(
        lib_id="Connector:Conn_01x20",
        reference="J4",
        value="GPIO_RIGHT",
        position=(250, 200),
        footprint="Connector_PinHeader_2.54mm:PinHeader_1x20_P2.54mm_Vertical"
    )

    # =========================================================================
    # 10. ADD LABELS FOR KEY NETS
    # =========================================================================
    print("\n[Complete] Adding net labels...")

    # Power labels
    sch.add_label("VBUS", position=(70, 100))
    sch.add_label("3V3", position=(130, 100))
    sch.add_label("GND", position=(100, 120))

    # Signal labels
    sch.add_label("BOOT0", position=(175, 180))
    sch.add_label("NRST", position=(195, 180))
    sch.add_label("SWDIO", position=(55, 150))
    sch.add_label("SWCLK", position=(55, 155))

    # MCU pin labels
    sch.add_label("PC13", position=(215, 150))
    sch.add_label("PA0", position=(215, 130))
    sch.add_label("PH0-OSC_IN", position=(125, 150))
    sch.add_label("PH1-OSC_OUT", position=(125, 155))
    sch.add_label("PC14-OSC32_IN", position=(125, 170))
    sch.add_label("PC15-OSC32_OUT", position=(125, 175))

    # =========================================================================
    # 11. SAVE SCHEMATIC
    # =========================================================================
    print("\nSaving schematic...")

    import os
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "stm32f411_black_pill.kicad_sch")
    sch.save(output_file)

    print(f"✅ Schematic saved to: {output_file}")

    # =========================================================================
    # 12. SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("STM32F411 BLACK PILL BOARD SUMMARY")
    print("=" * 70)

    summary = sch.get_summary()
    print(f"Components: {summary['component_count']}")

    # Count component types
    resistors = sch.components.filter(lib_id="Device:R")
    capacitors = sch.components.filter(lib_id="Device:C")
    leds = sch.components.filter(lib_id="Device:LED")
    buttons = len([c for c in sch.components if "SW" in c.reference])

    print(f"\nComponent Breakdown:")
    print(f"  - Resistors: {len(resistors)}")
    print(f"  - Capacitors: {len(capacitors)}")
    print(f"  - LEDs: {len(leds)}")
    print(f"  - Buttons: {buttons}")
    print(f"  - Crystals: 2 (25MHz HSE, 32.768kHz LSE)")
    print(f"  - ICs: 2 (STM32F411CEU6, AMS1117-3.3)")
    print(f"  - Connectors: 4 (USB-C, SWD, 2x GPIO headers)")

    print("\n" + "=" * 70)
    print("FEATURES")
    print("=" * 70)
    print("✅ STM32F411CEU6 - 100MHz ARM Cortex-M4")
    print("✅ 512KB Flash, 128KB RAM")
    print("✅ USB Type-C for power and programming")
    print("✅ 3.3V regulated power supply")
    print("✅ 25MHz HSE crystal for main clock")
    print("✅ 32.768kHz LSE for RTC")
    print("✅ SWD programming interface")
    print("✅ BOOT0 and NRST buttons")
    print("✅ User LED (PC13) and button (PA0)")
    print("✅ All GPIO broken out to headers")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Open in KiCAD: kicad stm32f411_black_pill.kicad_sch")
    print("2. Complete pin-to-pin wiring")
    print("3. Run Electrical Rules Check (ERC)")
    print("4. Create PCB layout (reference: Phil's Lab #65)")
    print("5. Generate Gerbers and BOM for manufacturing")
    print("\nReference: Phil's Lab #65 - KiCad 6 STM32 PCB Design Tutorial")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
