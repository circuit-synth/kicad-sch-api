#!/usr/bin/env python3
"""
STM32G431 Simple Development Board - Hierarchical Design

Simplified STM32G4 example using STM32G431RBT6 (64-pin LQFP).
This is easier to understand and work with than the G474 version.

Features:
- STM32G431RBT6 (64-pin LQFP - easier to solder than QFN)
- Simplified power supply
- USB-C for power and programming
- Basic user interface (1 button, 1 LED)
- SWD debug header
- Fewer components for clarity

Perfect for learning hierarchical schematic design!
"""

import kicad_sch_api as ksa
from pathlib import Path

# Output directory
output_dir = Path("examples/stm32g431_simple")
output_dir.mkdir(exist_ok=True)

print("Creating simplified STM32G431 hierarchical schematic...")
print("This is a beginner-friendly version with fewer components:\n")

# **IMPORTANT**: All hierarchical sheets MUST use the same project name!
PROJECT_NAME = "STM32G431_Simple"

# Sheet positions
SHEET_WIDTH = 50.8
SHEET_HEIGHT = 38.1
COL1_X = 50.8
COL2_X = COL1_X + SHEET_WIDTH + 25.4
ROW1_Y = 50.8
ROW2_Y = ROW1_Y + SHEET_HEIGHT + 25.4

# =============================================================================
# MAIN TOP-LEVEL SCHEMATIC
# =============================================================================
print(f"1. Creating main schematic (project: {PROJECT_NAME})...")
main = ksa.create_schematic(PROJECT_NAME)

# Get parent UUID for hierarchy context
parent_uuid = main.uuid
print(f"   Parent UUID: {parent_uuid}")

main.add_text(
    "STM32G431 Simple Development Board",
    position=(127.0, 25.4),
    effects={'font_size': (2.5, 2.5), 'bold': True}
)

# Power sheet
print("   - Adding power supply sheet...")
power_sheet_uuid = main.sheets.add_sheet(
    name="Power Supply",
    filename="power.kicad_sch",
    position=(COL1_X, ROW1_Y),
    size=(SHEET_WIDTH, SHEET_HEIGHT),
    project_name=PROJECT_NAME
)
main.sheets.add_sheet_pin(power_sheet_uuid, "VBUS", "input", "left", 5)
main.sheets.add_sheet_pin(power_sheet_uuid, "+3.3V", "output", "right", 5)
main.sheets.add_sheet_pin(power_sheet_uuid, "GND", "passive", "bottom", 10)

# MCU sheet
print("   - Adding microcontroller sheet...")
mcu_sheet_uuid = main.sheets.add_sheet(
    name="Microcontroller",
    filename="mcu.kicad_sch",
    position=(COL2_X, ROW1_Y),
    size=(SHEET_WIDTH, SHEET_HEIGHT),
    project_name=PROJECT_NAME
)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "+3.3V", "input", "left", 5)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "GND", "passive", "bottom", 10)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "NRST", "bidirectional", "right", 5)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "SWDIO", "bidirectional", "right", 10)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "SWCLK", "input", "right", 15)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "LED", "output", "right", 20)

# USB sheet
print("   - Adding USB interface sheet...")
usb_sheet_uuid = main.sheets.add_sheet(
    name="USB Interface",
    filename="usb.kicad_sch",
    position=(COL1_X, ROW2_Y),
    size=(SHEET_WIDTH, SHEET_HEIGHT),
    project_name=PROJECT_NAME
)
main.sheets.add_sheet_pin(usb_sheet_uuid, "VBUS", "output", "right", 5)
main.sheets.add_sheet_pin(usb_sheet_uuid, "GND", "passive", "bottom", 10)

# User interface sheet
print("   - Adding user interface sheet...")
ui_sheet_uuid = main.sheets.add_sheet(
    name="User Interface",
    filename="ui.kicad_sch",
    position=(COL2_X, ROW2_Y),
    size=(SHEET_WIDTH, SHEET_HEIGHT),
    project_name=PROJECT_NAME
)
main.sheets.add_sheet_pin(ui_sheet_uuid, "+3.3V", "input", "left", 5)
main.sheets.add_sheet_pin(ui_sheet_uuid, "GND", "passive", "bottom", 10)
main.sheets.add_sheet_pin(ui_sheet_uuid, "NRST", "output", "right", 5)
main.sheets.add_sheet_pin(ui_sheet_uuid, "LED", "input", "left", 15)
main.sheets.add_sheet_pin(ui_sheet_uuid, "SWDIO", "bidirectional", "right", 10)
main.sheets.add_sheet_pin(ui_sheet_uuid, "SWCLK", "input", "right", 15)

# Labels
main.add_label("+3.3V", position=(COL1_X + SHEET_WIDTH + 5, ROW1_Y + 5))
main.add_label("GND", position=(COL1_X + 10, ROW2_Y + SHEET_HEIGHT + 5))
main.add_label("VBUS", position=(COL1_X + SHEET_WIDTH + 5, ROW2_Y + 5))

main_file = output_dir / f"{PROJECT_NAME}.kicad_sch"
main.save(str(main_file))
print(f"   ✓ Saved: {main_file}")

# =============================================================================
# POWER SUPPLY SHEET
# =============================================================================
print(f"\n2. Creating power supply sheet (project: {PROJECT_NAME})...")
power = ksa.create_schematic(PROJECT_NAME)

# Set hierarchy context for child schematic
power.set_hierarchy_context(parent_uuid, power_sheet_uuid)
print(f"   Set hierarchy context: /{parent_uuid}/{power_sheet_uuid}")

# Simple 3.3V LDO regulator
vreg = power.components.add(
    'Regulator_Linear:AMS1117-3.3',
    'U2',
    'AMS1117-3.3',
    position=(127.0, 101.6)
)
vreg.footprint = 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'

# Input capacitor
c_in = power.components.add('Device:C', 'C1', '10µF', position=(101.6, 101.6))
c_in.footprint = 'Capacitor_SMD:C_0805_2012Metric'

# Output capacitor
c_out = power.components.add('Device:C', 'C2', '10µF', position=(152.4, 101.6))
c_out.footprint = 'Capacitor_SMD:C_0805_2012Metric'

# Labels
power.add_label("VBUS", position=(76.2, 101.6))
power.add_label("+3.3V", position=(177.8, 101.6))
power.add_label("GND", position=(127.0, 127.0))

power_file = output_dir / "power.kicad_sch"
power.save(str(power_file))
print(f"   ✓ Saved: {power_file}")

# =============================================================================
# MCU SHEET
# =============================================================================
print(f"\n3. Creating microcontroller sheet (project: {PROJECT_NAME})...")
mcu_sch = ksa.create_schematic(PROJECT_NAME)

# Set hierarchy context for child schematic
mcu_sch.set_hierarchy_context(parent_uuid, mcu_sheet_uuid)
print(f"   Set hierarchy context: /{parent_uuid}/{mcu_sheet_uuid}")

# STM32G431RBT6 - 64-pin LQFP (easier to solder than QFN!)
mcu = mcu_sch.components.add(
    'MCU_ST_STM32G4:STM32G431R_6-8-B_Tx',
    'U1',
    'STM32G431RBT6',
    position=(127.0, 101.6)
)
mcu.footprint = 'Package_QFP:LQFP-64_10x10mm_P0.5mm'

# Just the essential decoupling capacitors (simplified!)
cap_positions = [
    (101.6, 76.2),   # VDD decoupling
    (152.4, 76.2),   # VDD decoupling
    (101.6, 127.0),  # VDDA decoupling
]
for i, pos in enumerate(cap_positions, start=3):
    cap = mcu_sch.components.add('Device:C', f'C{i}', '100nF', position=pos)
    cap.footprint = 'Capacitor_SMD:C_0603_1608Metric'

# NRST pull-up
r_nrst = mcu_sch.components.add('Device:R', 'R1', '10k', position=(76.2, 76.2))
r_nrst.footprint = 'Resistor_SMD:R_0603_1608Metric'

# Boot0 pull-down (so it boots from flash by default)
r_boot = mcu_sch.components.add('Device:R', 'R2', '10k', position=(76.2, 88.9))
r_boot.footprint = 'Resistor_SMD:R_0603_1608Metric'

# Labels
mcu_sch.add_label("+3.3V", position=(76.2, 63.5))
mcu_sch.add_label("GND", position=(127.0, 152.4))
mcu_sch.add_label("NRST", position=(63.5, 76.2))
mcu_sch.add_label("SWDIO", position=(177.8, 101.6))
mcu_sch.add_label("SWCLK", position=(177.8, 109.22))
mcu_sch.add_label("LED", position=(177.8, 116.84))

mcu_file = output_dir / "mcu.kicad_sch"
mcu_sch.save(str(mcu_file))
print(f"   ✓ Saved: {mcu_file}")

# =============================================================================
# USB SHEET
# =============================================================================
print(f"\n4. Creating USB interface sheet (project: {PROJECT_NAME})...")
usb_sch = ksa.create_schematic(PROJECT_NAME)

# Set hierarchy context for child schematic
usb_sch.set_hierarchy_context(parent_uuid, usb_sheet_uuid)
print(f"   Set hierarchy context: /{parent_uuid}/{usb_sheet_uuid}")

# Simple USB-C connector for power (not using USB data in this simple version)
usb = usb_sch.components.add(
    'Connector:USB_C_Receptacle_PowerOnly_6P',
    'J1',
    'USB-C Power',
    position=(127.0, 101.6)
)
usb.footprint = 'Connector_USB:USB_C_Receptacle_GCT_USB4510-03-A_6P_TopMnt_Horizontal'

# CC resistors for power-only mode (5.1k to indicate we're a sink)
r_cc1 = usb_sch.components.add('Device:R', 'R3', '5.1k', position=(152.4, 88.9))
r_cc1.footprint = 'Resistor_SMD:R_0603_1608Metric'

r_cc2 = usb_sch.components.add('Device:R', 'R4', '5.1k', position=(152.4, 96.52))
r_cc2.footprint = 'Resistor_SMD:R_0603_1608Metric'

# Labels
usb_sch.add_label("VBUS", position=(177.8, 101.6))
usb_sch.add_label("GND", position=(127.0, 127.0))

usb_file = output_dir / "usb.kicad_sch"
usb_sch.save(str(usb_file))
print(f"   ✓ Saved: {usb_file}")

# =============================================================================
# USER INTERFACE SHEET
# =============================================================================
print(f"\n5. Creating user interface sheet (project: {PROJECT_NAME})...")
ui_sch = ksa.create_schematic(PROJECT_NAME)

# Set hierarchy context for child schematic
ui_sch.set_hierarchy_context(parent_uuid, ui_sheet_uuid)
print(f"   Set hierarchy context: /{parent_uuid}/{ui_sheet_uuid}")

# One button (NRST)
sw_reset = ui_sch.components.add('Switch:SW_Push', 'SW1', 'RESET', position=(76.2, 76.2))
sw_reset.footprint = 'Button_Switch_SMD:SW_SPST_B3U-1000P'

# One LED on PC13 (the classic STM32 blinky LED!)
led = ui_sch.components.add('Device:LED', 'D1', 'green', position=(152.4, 76.2))
led.footprint = 'LED_SMD:LED_0805_2012Metric'

r_led = ui_sch.components.add('Device:R', 'R5', '470R', position=(177.8, 76.2))
r_led.footprint = 'Resistor_SMD:R_0603_1608Metric'

# SWD connector (4-pin header for ST-Link or similar)
swd = ui_sch.components.add(
    'Connector_Generic:Conn_01x04',
    'J2',
    'SWD',
    position=(76.2, 101.6)
)
swd.footprint = 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical'

# Labels
ui_sch.add_label("+3.3V", position=(50.8, 63.5))
ui_sch.add_label("GND", position=(127.0, 127.0))
ui_sch.add_label("NRST", position=(101.6, 76.2))
ui_sch.add_label("LED", position=(127.0, 76.2))
ui_sch.add_label("SWDIO", position=(101.6, 96.52))
ui_sch.add_label("SWCLK", position=(101.6, 104.14))

ui_file = output_dir / "ui.kicad_sch"
ui_sch.save(str(ui_file))
print(f"   ✓ Saved: {ui_file}")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "="*70)
print("✅ Successfully created simplified STM32G431 example!")
print("="*70)
print(f"\nOutput directory: {output_dir}/")
print("\nGenerated files:")
print(f"  - main.kicad_sch       (top-level with 4 sheet instances)")
print(f"  - power.kicad_sch      (simple AMS1117 3.3V regulator)")
print(f"  - mcu.kicad_sch        (STM32G431RBT6 64-pin LQFP)")
print(f"  - usb.kicad_sch        (USB-C power-only)")
print(f"  - ui.kicad_sch         (1 button + 1 LED + SWD)")
print(f"\nTotal sheets: 5")
print(f"Total components: ~14 (much simpler!)")
print(f"\nMCU: STM32G431RBT6 (64-pin LQFP)")
print("  - Easier to solder than QFN")
print("  - Same family as G474")
print("  - Perfect for learning")
print(f"\nProject name (all sheets): {PROJECT_NAME}")
print(f"\nOpen in KiCad:")
print(f"  kicad {output_dir}/{PROJECT_NAME}.kicad_sch")
print("\nSimplifications vs G474 version:")
print("  • USB-C power-only (no data lines)")
print("  • Single button (reset)")
print("  • Single LED (blinky on PC13)")
print("  • Fewer decoupling caps")
print("  • No external flash")
print("  • No GPIO expansion headers")
print("  • LQFP package (easier to hand-solder)")
print("\nPerfect for:")
print("  • Learning hierarchical design")
print("  • First STM32 board")
print("  • Understanding the basics")
print("  • Hand-soldering practice")
