# Property Positioning Analysis - 10 Component Reference Schematics

## Overview

This document analyzes KiCAD's native `fields_autoplaced` property positioning across 10 different component types. The reference schematics were created by manually placing each component in KiCAD and letting it auto-arrange the properties.

**Key Finding**: Properties are NOT positioned using simple fixed offsets. Instead, KiCAD uses complex positioning logic that considers:
- Component library definition and pin layout
- Component rotation
- Bounding box calculations
- Component class/type

## Reference Schematics Created

All schematics stored in: `tests/reference_kicad_projects/property_positioning_*/`

| # | Component Type | Lib ID | File | Comp Pos | Details |
|---|---|---|---|---|---|
| 1 | Resistor | Device:R | property_positioning_resistor/resistor.kicad_sch | (100.00, 100.00) | 2-pin passive, simple |
| 2 | Capacitor | Device:C | property_positioning_capacitor/capacitor.kicad_sch | (118.11, 68.58) | 2-pin passive, unpolarized |
| 3 | Inductor | Device:L | property_positioning_inductor/inductor.kicad_sch | (96.52, 62.23) | 2-pin passive, coil |
| 4 | Diode | Device:D | property_positioning_diode/diode.kicad_sch | (123.19, 81.28) | 2-pin semiconductor |
| 5 | LED | Device:LED | property_positioning_led/led.kicad_sch | (120.65, 73.66) | 2-pin, polar |
| 6 | BJT Transistor | Transistor_BJT:2N2219 | property_positioning_transistor_bjt/transistor_bjt.kicad_sch | (127.00, 91.44) | 3-pin, active |
| 7 | Op-Amp | Amplifier_Operational:TL072 | property_positioning_op_amp/op_amp.kicad_sch | (123.19, 40.64) | 8-pin IC, multi-unit |
| 8 | Logic IC | 74xx:74HC595 | property_positioning_logic_ic/logic_ic.kicad_sch | (130.81, 57.15) | 16-pin IC, complex |
| 9 | Connector | Connector:Conn_01x04_Pin | property_positioning_connector/connector.kicad_sch | (137.16, 69.85) | 4-pin, header |
| 10 | Capacitor Polarized | Device:C_Polarized | property_positioning_capacitor_electrolytic/capacitor_electrolytic.kicad_sch | (139.70, 69.85) | 2-pin, polarized |

## Property Positioning Patterns

### 1. RESISTOR (Device:R) @ (100, 100, 0°)

**Library**: Device:R
**Component Position**: (100.00, 100.00) @ 0°
**Rotation**: Horizontal (pins left/right)

**Properties**:
```
Reference R1      @ (102.54, 98.7299, 0°)   Offset: (+2.54, -1.2701)   justify left
Value 10k         @ (102.54, 101.2699, 0°)  Offset: (+2.54, +1.2699)   justify left
Footprint ""      @ (98.222, 100, 90°)      Offset: (-1.778, 0)        hide yes
Datasheet "~"     @ (100, 100, 0°)          Offset: (0, 0)             hide yes
Description ""    @ (100, 100, 0°)          Offset: (0, 0)             hide yes
```

**Pattern**: Reference and Value RIGHT and STACKED vertically
- Ref above component (offset -1.27)
- Val below component (offset +1.27)
- Both use `justify left`

---

### 2. CAPACITOR (Device:C) @ (118.11, 68.58, 0°)

**Library**: Device:C (unpolarized)
**Component Position**: (118.11, 68.58) @ 0°
**Rotation**: Horizontal

**Properties**:
```
Reference C?      @ (118.75, 71.12, 0°)     Offset: (+0.64, +2.54)
Value 100nF       @ (118.75, 66.04, 0°)     Offset: (+0.64, -2.54)
Footprint ""      @ (119.08, 64.77, 0°)     Offset: (+0.97, -3.81)
Datasheet "~"     @ (118.11, 68.58, 0°)     Offset: (0, 0)
Description ""    @ (118.11, 68.58, 0°)     Offset: (0, 0)
```

**Pattern**: Slightly RIGHT and STACKED
- Different offsets than resistor (0.64 instead of 2.54)
- Suggests library-specific positioning

---

### 3. INDUCTOR (Device:L) @ (96.52, 62.23, 0°)

**Library**: Device:L
**Component Position**: (96.52, 62.23) @ 0°
**Rotation**: Horizontal

**Properties**:
```
Reference L?      @ (95.25, 62.23, 90°)     Offset: (-1.27, 0)
Value 10uH        @ (98.43, 62.23, 90°)     Offset: (+1.91, 0)
Footprint ""      @ (96.52, 62.23, 0°)      Offset: (0, 0)
Datasheet "~"     @ (96.52, 62.23, 0°)      Offset: (0, 0)
Description ""    @ (96.52, 62.23, 0°)      Offset: (0, 0)
```

**Pattern**: HORIZONTALLY stacked, text rotated 90°
- Reference LEFT (offset -1.27)
- Value RIGHT (offset +1.91)
- Both rotated 90° for horizontal arrangement

---

### 4. DIODE (Device:D) @ (123.19, 81.28, 0°)

**Library**: Device:D
**Component Position**: (123.19, 81.28) @ 0°
**Rotation**: Horizontal

**Properties**:
```
Reference D?      @ (123.19, 83.82, 0°)     Offset: (0, +2.54)
Value 1N4148      @ (123.19, 78.74, 0°)     Offset: (0, -2.54)
Footprint ""      @ (123.19, 81.28, 0°)     Offset: (0, 0)
Datasheet "~"     @ (123.19, 81.28, 0°)     Offset: (0, 0)
Description ""    @ (123.19, 81.28, 0°)     Offset: (0, 0)
```

**Pattern**: VERTICALLY stacked on component body
- Reference ABOVE (+2.54)
- Value BELOW (-2.54)
- No horizontal offset

---

### 5. LED (Device:LED) @ (120.65, 73.66, 0°)

**Library**: Device:LED
**Component Position**: (120.65, 73.66) @ 0°
**Rotation**: Horizontal

**Properties**:
```
Reference D?      @ (120.65, 76.20, 0°)     Offset: (0, +2.54)
Value LED         @ (120.65, 71.12, 0°)     Offset: (0, -2.54)
Footprint ""      @ (120.65, 73.66, 0°)     Offset: (0, 0)
Datasheet "~"     @ (120.65, 73.66, 0°)     Offset: (0, 0)
Description ""    @ (120.65, 73.66, 0°)     Offset: (0, 0)
```

**Pattern**: Same as DIODE (variant of same symbol)
- VERTICALLY stacked on centerline

---

### 6. BJT TRANSISTOR (Transistor_BJT:2N2219) @ (127.00, 91.44, 0°)

**Library**: Transistor_BJT:2N2219
**Component Position**: (127.00, 91.44) @ 0°
**Rotation**: Horizontal (3-pin)

**Properties**:
```
Reference Q?      @ (132.08, 93.35, 0°)     Offset: (+5.08, +1.91)
Value 2N2219      @ (132.08, 91.44, 0°)     Offset: (+5.08, 0)
Footprint ""      @ (132.08, 89.53, 0°)     Offset: (+5.08, -1.91)
Datasheet "~"     @ (127.00, 91.44, 0°)     Offset: (0, 0)
Description ""    @ (127.00, 91.44, 0°)     Offset: (0, 0)
```

**Pattern**: RIGHT and STACKED (wider offset than resistor)
- All properties RIGHT (+5.08)
- Stacked vertically with different spacing

---

### 7. OP-AMP (Amplifier_Operational:TL072) @ (123.19, 40.64, 0°)

**Library**: Amplifier_Operational:TL072 (8-pin DIP, dual)
**Component Position**: (123.19, 40.64) @ 0°
**Rotation**: Horizontal (multi-pin IC)

**Properties**:
```
Reference U?      @ (123.19, 45.72, 0°)     Offset: (0, +5.08)
Value TL072       @ (123.19, 35.56, 0°)     Offset: (0, -5.08)
Footprint ""      @ (123.19, 40.64, 0°)     Offset: (0, 0)
Datasheet "~"     @ (123.19, 40.64, 0°)     Offset: (0, 0)
Description ""    @ (123.19, 40.64, 0°)     Offset: (0, 0)
```

**Pattern**: VERTICALLY stacked (larger offsets for IC)
- Reference ABOVE (+5.08) - larger IC means larger spacing
- Value BELOW (-5.08)
- No horizontal offset

---

### 8. LOGIC IC (74xx:74HC595) @ (130.81, 57.15, 0°)

**Library**: 74xx:74HC595 (16-pin DIP, complex)
**Component Position**: (130.81, 57.15) @ 0°
**Rotation**: Horizontal

**Properties**:
```
Reference U?      @ (123.19, 71.12, 0°)     Offset: (-7.62, +13.97)
Value 74HC595     @ (123.19, 40.64, 0°)     Offset: (-7.62, -16.51)
Footprint ""      @ (130.81, 57.15, 0°)     Offset: (0, 0)
Datasheet "~"     @ (130.81, 57.15, 0°)     Offset: (0, 0)
Description ""    @ (130.81, 57.15, 0°)     Offset: (0, 0)
```

**Pattern**: LEFT and WIDE STACKING (IC-specific)
- Both properties LEFT (-7.62)
- Very large vertical spacing (+13.97 to -16.51)
- IC uses wider component area

---

### 9. CONNECTOR (Connector:Conn_01x04_Pin) @ (137.16, 69.85, 0°)

**Library**: Connector:Conn_01x04_Pin (4-pin header)
**Component Position**: (137.16, 69.85) @ 0°
**Rotation**: Vertical (pins top/bottom)

**Properties**:
```
Reference J?      @ (137.16, 74.93, 0°)     Offset: (0, +5.08)
Value Conn...     @ (137.16, 62.23, 0°)     Offset: (0, -7.62)
Footprint ""      @ (137.16, 69.85, 0°)     Offset: (0, 0)
Datasheet "~"     @ (137.16, 69.85, 0°)     Offset: (0, 0)
Description ""    @ (137.16, 69.85, 0°)     Offset: (0, 0)
```

**Pattern**: VERTICALLY stacked (multi-pin connector)
- Reference ABOVE (+5.08)
- Value BELOW (-7.62) - slightly asymmetric
- No horizontal offset

---

### 10. CAPACITOR POLARIZED (Device:C_Polarized) @ (139.70, 69.85, 0°)

**Library**: Device:C_Polarized
**Component Position**: (139.70, 69.85) @ 0°
**Rotation**: Horizontal

**Properties**:
```
Reference C?      @ (140.34, 72.39, 0°)     Offset: (+0.64, +2.54)
Value C_Polariz.. @ (140.34, 67.31, 0°)     Offset: (+0.64, -2.54)
Footprint ""      @ (140.67, 66.04, 0°)     Offset: (+0.97, -3.81)
Datasheet "~"     @ (139.70, 69.85, 0°)     Offset: (0, 0)
Description ""    @ (139.70, 69.85, 0°)     Offset: (0, 0)
```

**Pattern**: Similar to unpolarized CAPACITOR
- Slightly RIGHT (+0.64, same as capacitor)
- STACKED vertically
- Library variant of same pattern

---

## Key Findings

### 1. Library-Specific Positioning

Positioning is NOT generic per rotation. It's **library-specific**:
- **Resistor** (Device:R): offset (+2.54, ±1.27)
- **Capacitor** (Device:C): offset (+0.64, ±2.54)
- **Diode** (Device:D): offset (0, ±2.54) - different from Resistor!
- **BJT** (Transistor_BJT:*): offset (+5.08, varies)
- **Op-Amp/IC** (Amplifier_Operational:*, 74xx:*): offset (0 or ±7.62, ±5.08-16.51)

### 2. Property Rotation

Some components rotate the property text itself (e.g., Inductor):
- Resistor: Reference @ 0° rotation (text horizontal)
- Inductor: Reference @ 90° rotation (text vertical)
- Diode: Reference @ 0° rotation

This is based on **optimal text positioning** for the component shape.

### 3. Vertical vs Horizontal Stacking

- **2-pin components with horizontal layout** (Resistor): Properties positioned RIGHT, stacked vertically
- **2-pin components on centerline** (Diode, LED): Properties stacked VERTICALLY on centerline
- **Multi-pin ICs**: Properties positioned LEFT or on centerline, large vertical spacing
- **Connectors**: Properties stacked VERTICALLY on centerline

### 4. Hidden Properties

All hidden properties (Datasheet, Description, ki_keywords, etc.) are positioned at:
- Component center (0, 0) offset
- Rotation 0° regardless of component rotation
- `hide yes` flag in effects

### 5. Footprint Property Special Handling

Footprint property typically:
- Positioned left/offset from component
- Rotated 90° (vertical text)
- Hidden from schematic

---

## Implementation Challenges

### Challenge 1: Symbol Library Access
Need to read symbol definitions to determine:
- Component bounding box dimensions
- Pin positions and orientations
- Reference positioning relative to body

### Challenge 2: Multi-Unit Components
Op-Amps and other ICs with multiple units need separate positioning per unit.

### Challenge 3: Symbol Variants
Same library ID may have multiple symbols (e.g., different pin counts) requiring different positioning.

### Challenge 4: Rotation Handling
At 90°/180°/270° rotations, the positioning algorithm must:
- Recalculate offsets as rotation transforms
- Adjust text rotation to remain readable
- Consider component bounding box rotation

---

## Next Steps for Implementation

1. **Extract Symbol Bounding Boxes**: Build cache of dimensions for all symbols
2. **Map Components to Positioning Rules**: Identify rules per library/family
3. **Implement Rotation Transforms**: Handle 0°, 90°, 180°, 270° correctly
4. **Test Against References**: Validate generated positions match KiCAD exactly

---

## Reference Schematic Locations

All schematics are saved in `tests/reference_kicad_projects/`:
- `property_positioning_resistor/`
- `property_positioning_capacitor/`
- `property_positioning_inductor/`
- `property_positioning_diode/`
- `property_positioning_led/`
- `property_positioning_transistor_bjt/`
- `property_positioning_op_amp/`
- `property_positioning_logic_ic/`
- `property_positioning_connector/`
- `property_positioning_capacitor_electrolytic/`

Each contains a `.kicad_sch` file with KiCAD's native auto-placed properties.
