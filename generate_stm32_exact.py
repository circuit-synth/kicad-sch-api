#!/usr/bin/env python3
"""
Generate STM32G030K8Tx Microprocessor Circuit - Exact Recreation
This recreates the cleaned-up schematic with exact component positions and wiring.
"""

import kicad_sch_api as ksa

print("=" * 80)
print("GENERATING STM32G030K8Tx MICROPROCESSOR CIRCUIT")
print("=" * 80)
print()

# Create new schematic
print("📄 Creating new schematic...")
sch = ksa.create_schematic('STM32_Microprocessor')
print(f"✅ Created schematic: {sch.name}")
print()

# ==========================================================================
# Add Components - Exact positions from cleaned-up schematic
# ==========================================================================
print("🔧 Adding components...")

# Main MCU
u1 = sch.components.add(
    'MCU_ST_STM32G0:STM32G030K8Tx',
    'U1',
    'STM32G030K8Tx',
    position=(128.27, 110.49),
    rotation=0
)
print(f"  ✓ U1 - STM32G030K8Tx @ (128.27, 110.49)")

# Resistors
r1 = sch.components.add('Device:R', 'R1', '10k', position=(91.44, 86.36), rotation=0)
print(f"  ✓ R1 - 10k @ (91.44, 86.36)")

r3 = sch.components.add('Device:R', 'R3', '330', position=(160.02, 101.60), rotation=0)
print(f"  ✓ R3 - 330Ω @ (160.02, 101.60)")

# LED
d1 = sch.components.add('Device:LED', 'D1', 'GREEN', position=(160.02, 109.22), rotation=90)
print(f"  ✓ D1 - GREEN LED @ (160.02, 109.22)")

# Capacitors
c1 = sch.components.add('Device:C', 'C1', '100nF', position=(138.43, 71.12), rotation=0)
print(f"  ✓ C1 - 100nF @ (138.43, 71.12)")

c2 = sch.components.add('Device:C_Polarized', 'C2', '10uF', position=(149.86, 71.12), rotation=0)
print(f"  ✓ C2 - 10uF @ (149.86, 71.12)")

c3 = sch.components.add('Device:C', 'C3', '100nF', position=(96.52, 93.98), rotation=0)
print(f"  ✓ C3 - 100nF @ (96.52, 93.98)")

# SWD Debug Header (moved down 2.54mm)
j1 = sch.components.add('Connector:Conn_01x04_Pin', 'J1', 'SWD', position=(184.15, 83.82), rotation=180)
print(f"  ✓ J1 - SWD Debug Header @ (184.15, 83.82), rotation=180°")

print()

# ==========================================================================
# Add Power Symbols
# ==========================================================================
print("⚡ Adding power symbols...")

pwr01 = sch.components.add('power:+3.3V', '#PWR01', '+3.3V', position=(137.16, 63.50), rotation=0)
print(f"  ✓ #PWR01 (+3.3V) @ (137.16, 63.50)")

pwr02 = sch.components.add('power:+3.3V', '#PWR02', '+3.3V', position=(173.99, 78.74), rotation=0)
print(f"  ✓ #PWR02 (+3.3V) @ (173.99, 78.74)")

pwr03 = sch.components.add('power:+3.3V', '#PWR03', '+3.3V', position=(91.44, 78.74), rotation=0)
print(f"  ✓ #PWR03 (+3.3V) @ (91.44, 78.74)")

gnd05 = sch.components.add('power:GND', '#PWR05', 'GND', position=(160.02, 116.84), rotation=0)
print(f"  ✓ #PWR05 (GND) @ (160.02, 116.84)")

gnd06 = sch.components.add('power:GND', '#PWR06', 'GND', position=(144.78, 74.93), rotation=0)
print(f"  ✓ #PWR06 (GND) @ (144.78, 74.93)")

gnd07 = sch.components.add('power:GND', '#PWR07', 'GND', position=(128.27, 135.89), rotation=0)
print(f"  ✓ #PWR07 (GND) @ (128.27, 135.89)")

gnd08 = sch.components.add('power:GND', '#PWR08', 'GND', position=(96.52, 97.79), rotation=0)
print(f"  ✓ #PWR08 (GND) @ (96.52, 97.79)")

gnd09 = sch.components.add('power:GND', '#PWR09', 'GND', position=(177.80, 81.28), rotation=270)
print(f"  ✓ #PWR09 (GND) @ (177.80, 81.28)")

print()

# ==========================================================================
# Add Labels
# ==========================================================================
print("🏷️  Adding signal labels...")

sch.add_label("NRST", position=(86.36, 90.17), rotation=180)
sch.add_label("SWDIO", position=(148.59, 115.57), rotation=0)
sch.add_label("SWCLK", position=(148.59, 118.11), rotation=0)
sch.add_label("SWDIO", position=(172.72, 83.82), rotation=180)
sch.add_label("SWCLK", position=(172.72, 86.36), rotation=180)

print(f"  ✓ Added 5 labels: NRST, SWDIO (x2), SWCLK (x2)")
print()

# ==========================================================================
# Add Wiring
# ==========================================================================
print("🔌 Adding wiring...")

# All wires from the cleaned-up schematic
wires = [
    ((138.43, 74.93), (144.78, 74.93)),
    ((91.44, 90.17), (96.52, 90.17)),
    ((128.27, 64.77), (137.16, 64.77)),
    ((137.16, 64.77), (138.43, 64.77)),
    ((148.59, 115.57), (146.05, 115.57)),
    ((173.99, 78.74), (179.07, 78.74)),
    ((128.27, 64.77), (128.27, 82.55)),
    ((138.43, 64.77), (149.86, 64.77)),
    ((160.02, 95.25), (160.02, 97.79)),
    ((149.86, 64.77), (149.86, 67.31)),
    ((137.16, 63.50), (137.16, 64.77)),
    ((86.36, 90.17), (91.44, 90.17)),
    ((160.02, 113.03), (160.02, 116.84)),
    ((144.78, 74.93), (149.86, 74.93)),
    ((172.72, 86.36), (179.07, 86.36)),
    ((91.44, 82.55), (91.44, 78.74)),
    ((146.05, 95.25), (160.02, 95.25)),
    ((96.52, 90.17), (110.49, 90.17)),
    ((138.43, 64.77), (138.43, 67.31)),
    ((177.80, 81.28), (179.07, 81.28)),
    ((148.59, 118.11), (146.05, 118.11)),
    ((172.72, 83.82), (179.07, 83.82)),
]

for i, (start, end) in enumerate(wires, 1):
    sch.add_wire(start=start, end=end)

print(f"  ✓ Added {len(wires)} wires")
print()

# ==========================================================================
# Add Junctions
# ==========================================================================
print("🔗 Adding junctions...")

junctions = [
    (144.78, 74.93),
    (137.16, 64.77),
    (138.43, 64.77),
    (91.44, 90.17),
    (96.52, 90.17),
]

for pos in junctions:
    sch.junctions.add(position=pos)

print(f"  ✓ Added {len(junctions)} junctions")
print()

# ==========================================================================
# Add Rectangles
# ==========================================================================
print("📐 Adding rectangles...")

# Main circuit border
sch.add_rectangle(
    start=(72.39, 43.815),
    end=(193.04, 151.13),
    stroke_width=0,
    fill_type='none'
)
print(f"  ✓ Main circuit border: (72.39, 43.815) → (193.04, 151.13)")

# Debug section border
sch.add_rectangle(
    start=(161.29, 64.77),
    end=(187.325, 90.17),
    stroke_width=0,
    fill_type='none'
)
print(f"  ✓ Debug section border: (161.29, 64.77) → (187.325, 90.17)")
print()

# ==========================================================================
# Add Text
# ==========================================================================
print("📝 Adding text annotations...")

# Title
sch.add_text(
    "STM32G030K8Tx MICROCONTROLLER",
    position=(131.572, 50.8),
    size=2.5
)
print(f"  ✓ Title: 'STM32G030K8Tx MICROCONTROLLER' @ (131.572, 50.8)")

# Subtitle
sch.add_text(
    "ARM Cortex-M0+ @ 64MHz • 64KB Flash • 8KB RAM",
    position=(128.778, 147.32),
    size=1.27
)
print(f"  ✓ Subtitle @ (128.778, 147.32)")

# Debug label
sch.add_text(
    "Debug",
    position=(173.482, 68.58),
    size=2.0
)
print(f"  ✓ Debug label @ (173.482, 68.58)")
print()

# ==========================================================================
# Save
# ==========================================================================
print("💾 Saving schematic...")
sch.save('stm32_microprocessor_generated.kicad_sch')
print(f"✅ Saved: stm32_microprocessor_generated.kicad_sch")
print()

# ==========================================================================
# Summary
# ==========================================================================
print("=" * 80)
print("📊 STM32 MICROPROCESSOR CIRCUIT GENERATED")
print("=" * 80)
print()
print("Components:")
print(f"  • U1 - STM32G030K8Tx (32-pin ARM Cortex-M0+)")
print(f"  • C1, C2, C3 - Power decoupling (100nF + 10µF + 100nF)")
print(f"  • R1 - 10kΩ NRST pull-up")
print(f"  • R3 - 330Ω LED current limiting")
print(f"  • D1 - Green status LED")
print(f"  • J1 - 4-pin SWD debug header")
print(f"  • 8 power symbols (+3.3V and GND)")
print()
print("Connectivity:")
print(f"  • {len(wires)} wires")
print(f"  • {len(junctions)} junctions")
print(f"  • 5 labels (NRST, SWDIO x2, SWCLK x2)")
print()
print("Graphical Elements:")
print(f"  • 2 rectangles (circuit border, debug section)")
print(f"  • 3 text annotations (title, subtitle, debug label)")
print()
print("Next Steps:")
print(f"  1. Open: open stm32_microprocessor_generated.kicad_sch")
print(f"  2. Compare with original: diff stm32_microprocessor.kicad_sch stm32_microprocessor_generated.kicad_sch")
print(f"  3. Generate PDF: kicad-cli sch export pdf stm32_microprocessor_generated.kicad_sch")
print()
print("=" * 80)
