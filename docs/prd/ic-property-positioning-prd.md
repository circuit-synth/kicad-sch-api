# PRD: IC Component Property Positioning Rules

## Overview

Add property positioning rules for IC components to `POSITIONING_RULES` dictionary in `property_positioning.py`. Currently, IC components fall back to the resistor pattern (offset +2.54mm, -1.27mm) which is inappropriate for large ICs, causing property text to be placed too close to the component body.

This PRD addresses Issue #176 by adding positioning rules for 6 tested IC components that currently trigger "No positioning rule" warnings.

## Success Criteria

- [ ] No warnings about missing positioning rules for the 6 tested IC components
- [ ] Property text positioned at correct offsets matching KiCAD's native auto-placement
- [ ] All existing tests pass
- [ ] New tests validate IC property positioning
- [ ] Format preservation maintained (round-trip load/save)

## Functional Requirements

### REQ-1: Extract Property Positions from KiCAD Symbol Libraries

Parse `.kicad_sym` files to extract property positions for:
- RF_Module:ESP32-WROOM-32 (RF module, 38-pin, ~40×86mm)
- 74xx:74LS245 (SOIC-20W level shifter)
- Interface_UART:MAX3485 (SOIC-8 transceiver)
- Regulator_Linear:AMS1117-3.3 (SOT-223 LDO)
- Regulator_Switching:TPS54202DDC (SOT-23-6 buck converter)
- Transistor_FET:AO3401A (SOT-23 P-FET)

Extract `(at x y rotation)` from each symbol's Reference, Value, and Footprint properties.

### REQ-2: Add Rules to POSITIONING_RULES Dictionary

Add entries to `kicad_sch_api/core/property_positioning.py`:

```python
POSITIONING_RULES = {
    # Existing rules...

    # NEW IC rules
    "RF_Module:ESP32-WROOM-32": ComponentPositioningRule(...),
    "74xx:74LS245": ComponentPositioningRule(...),
    "Interface_UART:MAX3485": ComponentPositioningRule(...),
    "Regulator_Linear:AMS1117-3.3": ComponentPositioningRule(...),
    "Regulator_Switching:TPS54202DDC": ComponentPositioningRule(...),
    "Transistor_FET:AO3401A": ComponentPositioningRule(...),
}
```

### REQ-3: Validate Against Reference Schematics

Create reference schematics for each IC component showing:
- Component at standard position (100, 100)
- KiCAD's native auto-placement for properties
- All properties visible for analysis

### REQ-4: Round-Trip Format Preservation

Ensure loading and saving schematics with these IC components preserves exact property positions.

## KiCAD Format Specifications

### Symbol Library File Format

Property positions are defined in `.kicad_sym` files:

```
(symbol "ESP32-WROOM-32"
    (property "Reference" "U"
        (at -12.7 34.29 0)    # Position relative to symbol center
        (effects ...)
    )
    (property "Value" "ESP32-WROOM-32"
        (at 1.27 34.29 0)
        (effects ...)
    )
    (property "Footprint" "RF_Module:ESP32-WROOM-32"
        (at 0 -38.1 0)
        (effects ...)
    )
)
```

The `(at x y rotation)` values become offsets in `PropertyOffset`.

### KiCAD Library Locations

Symbol libraries are located at:
- **macOS**: `/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/`
- **Linux**: `/usr/share/kicad/symbols/`
- **Windows**: `C:\Program Files\KiCad\share\kicad\symbols\`

Environment variables `KICAD_SYMBOL_DIR`, `KICAD8_SYMBOL_DIR`, or `KICAD9_SYMBOL_DIR` can override defaults.

## Technical Constraints

### Backward Compatibility

No breaking changes - adding new rules only. Existing components unaffected.

### Format Preservation Requirements

When loading schematics with these IC components:
- Preserve exact property positions from input
- Preserve justification settings
- Preserve `fields_autoplaced` flag state
- Output matches input byte-perfectly

### Grid Alignment

All positions must be grid-aligned (multiples of 1.27mm - KiCAD's default grid).

## Reference Schematic Requirements

### Components to Test

Create reference schematics for each of the 6 IC components:

1. **ESP32-WROOM-32** - Large RF module (40mm × 86mm)
   - Expected: Reference (-12.7, 34.29), Value (1.27, 34.29)
   - Pattern: Properties ABOVE component with large Y offset

2. **74LS245** - SOIC-20W level shifter
   - Expected: Reference (-7.62, 16.51), Value (-7.62, -16.51)
   - Pattern: Properties LEFT and stacked vertically

3. **MAX3485** - SOIC-8 transceiver
   - Expected: Reference (+2.1433, -17.78)
   - Pattern: Properties ABOVE component

4. **AMS1117-3.3** - SOT-223 voltage regulator
   - Expected: Centered text above component
   - Pattern: Similar to op-amp

5. **TPS54202DDC** - SOT-23-6 buck converter
   - Expected: Centered text above component
   - Pattern: Similar to small IC

6. **AO3401A** - SOT-23 P-FET
   - Expected: Larger horizontal offset than resistor
   - Pattern: Similar to BJT transistor

### Reference Creation Method

For each component:
1. Create schematic programmatically with `kicad-sch-api`
2. Open in KiCAD and let it auto-place fields
3. Save and analyze property positions
4. Use those positions to define `PropertyOffset` values

## Edge Cases

### EDGE-1: Multi-Unit IC Components

Some ICs (ESP32, 74LS245) may have multiple units. Verify positioning works for unit 1 (primary unit).

### EDGE-2: Component Rotation

Positioning rules are defined for 0° rotation. The existing `_apply_rotation_transform()` function handles rotation transforms.

### EDGE-3: Symbol Variants

Some components have multiple symbol variants. Use the default/most common variant for defining rules.

### EDGE-4: Missing Symbol Libraries

If symbol library files are not found, log a warning and use default resistor pattern as fallback (current behavior).

## Impact Analysis

### Parser Changes

**File**: `kicad_sch_api/parsers/elements/symbol_parser.py`
- ✅ No changes needed - parser already handles property positions

### Formatter Changes

**File**: `kicad_sch_api/parsers/elements/symbol_parser.py`
- ✅ No changes needed - formatter already uses positioning rules

### Property Positioning Changes

**File**: `kicad_sch_api/core/property_positioning.py`
- ❌ Add 6 new entries to `POSITIONING_RULES` dictionary
- ✅ Existing `get_property_position()` function works without modification
- ✅ Existing `_apply_rotation_transform()` handles rotation

### Symbol Library Integration

**Files**: `kicad_sch_api/library/cache.py`, `kicad_sch_api/symbols/`
- ✅ Symbol library discovery already works
- ✅ Symbol loading already works
- ❌ Need script to extract property positions from `.kicad_sym` files

### Test Changes

**New file**: `tests/unit/test_ic_property_positioning.py`
- Unit tests for each IC component's property positioning

**New file**: `tests/reference_tests/test_ic_property_references.py`
- Reference tests validating exact KiCAD format match

## Out of Scope

### NOT Included in This PRD

- ❌ Auto-extraction from symbol libraries at runtime (future enhancement)
- ❌ Component family pattern matching (e.g., all "Regulator_Linear:*")
- ❌ Additional IC components beyond the 6 tested
- ❌ Symbol library parsing library/framework
- ❌ Dynamic rule generation

## Acceptance Criteria

### Implementation Complete When:

1. ✅ All 6 IC components have entries in `POSITIONING_RULES`
2. ✅ Property offsets extracted from KiCAD symbol libraries
3. ✅ No warnings about missing positioning rules for tested ICs
4. ✅ Reference schematics created for all 6 ICs
5. ✅ Unit tests verify correct property offsets
6. ✅ Reference tests validate exact format match
7. ✅ Round-trip tests pass (load → save → identical output)
8. ✅ All existing tests continue to pass
9. ✅ Manual validation: Open generated schematics in KiCAD → properties positioned correctly
10. ✅ Visual inspection: Property text not overlapping component bodies

### Test Coverage Requirements

- Unit test for each IC component (6 tests)
- Reference test for each IC component (6 tests)
- Round-trip format preservation for each (6 tests)
- Regression test ensuring existing components unaffected

## Implementation Strategy

### Phase 1: Extract Property Positions

1. Locate KiCAD symbol library files for each IC
2. Parse `.kicad_sym` files manually or with script
3. Extract `(property "Reference" (at x y rotation) ...)` values
4. Document property positions for each IC

### Phase 2: Add Positioning Rules

1. Create `ComponentPositioningRule` for each IC
2. Add to `POSITIONING_RULES` dictionary
3. Verify rules are loaded correctly

### Phase 3: Create Reference Schematics

1. Generate schematic programmatically for each IC
2. Open in KiCAD and verify auto-placement
3. Save reference schematics
4. Document expected property positions

### Phase 4: Testing

1. Write unit tests for each IC's property offsets
2. Write reference tests comparing against KiCAD output
3. Add round-trip format preservation tests
4. Verify all existing tests still pass

### Phase 5: Validation

1. Manual validation in KiCAD
2. Visual inspection of property positions
3. Verify no overlap with component bodies
4. Confirm warnings eliminated

## Related Issues & PRs

- Issue #176: Missing IC property positioning rules causes incorrect text placement
- Issue #150: Default component property text positioning doesn't match KiCAD auto-placement
- PRD: docs/prd/property-positioning-prd.md (broader property positioning work)
- Analysis: docs/PROPERTY_POSITIONING_ANALYSIS.md

## References

- KiCAD symbol libraries: `$KICAD_SYMBOL_DIR/*.kicad_sym`
- Existing positioning rules: `kicad_sch_api/core/property_positioning.py:37-98`
- Existing reference tests: `tests/reference_tests/test_property_positioning_references.py`
- Property positioning analysis: `docs/PROPERTY_POSITIONING_ANALYSIS.md`
