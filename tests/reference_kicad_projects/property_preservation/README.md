# Reference: Property Preservation

## Purpose

This reference schematic demonstrates complete component property preservation including custom properties with mixed visibility states.

## Contents

### Component: R1 (Device:R)
- **Position:** (100.33, 100.33) with rotation=0
- **Value:** 10k
- **Footprint:** Resistor_SMD:R_0603_1608Metric

### Properties

| Property | Value | Visible | Justify | Notes |
|----------|-------|---------|---------|-------|
| Reference | "R1" | ✓ Yes | left | Standard property |
| Value | "10k" | ✓ Yes | left | Standard property |
| Footprint | "Resistor_SMD:R_0603_1608Metric" | ✗ Hidden | - | Standard property |
| Datasheet | "~" | ✗ Hidden | - | Standard property |
| Description | "" | ✓ Yes | - | Standard property (empty value) |
| MPN | "C0603FR-0710KL" | ✗ Hidden | - | Custom property |
| Manufacturer | "Yageo" | ✓ Yes | right top | Custom property with justify |
| Tolearnce | "1%" | ✓ Yes | left bottom | Custom property with justify (typo preserved) |

## Key S-expression Format Discovered

### Visible Property (no hide flag)
```lisp
(property "Reference" "R1"
  (at 102.87 99.0599 0)
  (effects
    (font (size 1.27 1.27))
    (justify left)
  )
)
```

### Hidden Property (with hide flag)
```lisp
(property "Footprint" "Resistor_SMD:R_0603_1608Metric"
  (at 98.552 100.33 90)
  (effects
    (font (size 1.27 1.27))
    (hide yes)
  )
)
```

### Custom Property with Justification
```lisp
(property "Manufacturer" "Yageo"
  (at 100.33 100.33 0)
  (effects
    (font (size 1.27 1.27))
    (justify right top)
  )
)
```

## Critical Format Details

1. **Hide flag format:** `(hide yes)` appears in effects section
2. **Visible = no hide flag:** Visible properties have NO hide flag (not `(hide no)`, just absent)
3. **Justification preserved:** User-set justification values must be preserved
4. **Property order:** Reference, Value, Footprint, Datasheet, Description, then custom properties
5. **Empty values:** Description has empty string value but is still visible

## Used For

- **Testing:** Unit and reference tests for property visibility tracking
- **Validation:** Round-trip preservation of all properties and visibility states
- **Format preservation:** Ensuring `hidden_properties` set correctly maps to `(hide yes)` flags

## Created

- **Date:** 2025-11-08
- **Issue:** #140
- **PRD:** docs/prd/property-preservation-prd.md
- **KiCAD Version:** 9.0 (version 20250114)
