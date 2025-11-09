# Reference: Text Effects

## Purpose

Demonstrates all text effects that can be modified on component properties (Reference, Value, Footprint). Used to validate parsing and preservation of KiCAD's effects S-expression format.

## Contents

**Components:**
- R1: Single resistor (Device:R, 10k) at position (100.33, 100.33)

**Modified Properties:**

### Reference Property "R1"
- **Font face**: Arial (custom font)
- **Font size**: 2.0 x 2.0 mm (larger than default 1.27)
- **Bold**: Yes
- **Color**: Red (RGB: 255, 0, 0, Alpha: 1.0)
- **Position**: (102.87, 98.552) relative to component
- **Rotation**: 90°
- **Justification**: left

### Value Property "10k"
- **Font size**: 1.5 x 1.5 mm (larger than default 1.27)
- **Italic**: Yes
- **Position**: (102.87, 101.5999) relative to component
- **Rotation**: 0°

### Footprint Property
- **Hidden**: Yes (demonstrates visibility toggle)
- **Font size**: 1.27 x 1.27 mm (default)

## Key S-expression Format

### Reference Property with Full Effects
```
(property "Reference" "R1"
    (at 102.87 98.552 90)           # Position (x, y, rotation)
    (effects
        (font
            (face "Arial")          # Custom font
            (size 2 2)              # Font size (height, width) in mm
            (bold yes)              # Bold flag
            (color 255 0 0 1)       # Color RGBA (R, G, B, Alpha)
        )
        (justify left)              # Text justification
    )
)
```

### Value Property with Italic
```
(property "Value" "10k"
    (at 102.87 101.5999 0)
    (effects
        (font
            (size 1.5 1.5)
            (italic yes)            # Italic flag
        )
    )
)
```

### Hidden Footprint Property
```
(property "Footprint" ""
    (at 100.33 100.33 0)
    (effects
        (font
            (size 1.27 1.27)
        )
        (hide yes)                  # Visibility flag
    )
)
```

## Effects Tested

This reference validates parsing and preservation of:

- ✅ **Position**: `(at x y rotation)` - position relative to component with rotation
- ✅ **Font face**: `(face "FontName")` - custom font family
- ✅ **Font size**: `(size height width)` - text size in mm
- ✅ **Bold**: `(bold yes)` - bold flag
- ✅ **Italic**: `(italic yes)` - italic flag
- ✅ **Color**: `(color R G B A)` - RGBA color values
- ✅ **Justification**: `(justify left|right|center|top|bottom)` - text alignment
- ✅ **Visibility**: `(hide yes)` - show/hide toggle

## Used For

**Testing:**
- `tests/unit/test_text_effects.py` - Unit tests for effects parsing and modification
- `tests/reference_tests/test_text_effects_reference.py` - Reference format preservation tests

**Validation:**
- Verifies all text effects are parsed correctly from KiCAD files
- Ensures effects can be modified via API
- Confirms round-trip preservation (load → save → load)
- Validates S-expression format matches KiCAD exactly

## Created

- **Date**: 2025-01-08
- **Issue**: #134 - Add User Control for Component Label Positioning and Styling
- **PRD**: `docs/prd/text-effects-preservation-prd.md`
- **Manually created in**: KiCAD 9.0

## Notes

This is a **minimal reference** - one component only. Demonstrates all major text effects in a simple, focused schematic that's easy to debug and test against.
