# PRD: KiCAD-Exact Component Property Positioning

## Overview

Replicate KiCAD's native `fields_autoplaced` property positioning algorithm to ensure:
1. Programmatically generated components match KiCAD's auto-placement exactly
2. Round-trip format preservation - load user schematics and save them byte-perfectly

Currently, the library uses hardcoded offsets that don't match KiCAD's positioning logic, resulting in properties appearing in wrong positions with incorrect justification.

## Success Criteria

- [ ] Property positions (Reference, Value, Footprint, etc.) match KiCAD's auto-placement for all component rotations (0°, 90°, 180°, 270°)
- [ ] Text justification matches KiCAD's defaults
- [ ] `fields_autoplaced yes` flag emitted on generated components
- [ ] Round-trip preservation: Load KiCAD schematic → save → output matches input byte-perfectly
- [ ] Works for all component types: 2-pin passives, ICs, multi-unit components, connectors
- [ ] All existing tests pass (may need updates for new positioning)
- [ ] Format preservation validated against reference schematics

## Functional Requirements

### REQ-1: Property Position Calculation
Replicate KiCAD's algorithm for calculating Reference, Value, and Footprint property positions based on:
- Component position
- Component rotation (0°, 90°, 180°, 270°)
- Component bounding box (from symbol library)
- Property type (Reference, Value, Footprint, Datasheet, Description, custom)

### REQ-2: Text Justification
Apply correct text justification (`justify left`, `justify right`, `justify center`) matching KiCAD's defaults for each rotation.

### REQ-3: Fields Autoplaced Flag
Emit `(fields_autoplaced yes)` on all programmatically generated components.

### REQ-4: Round-Trip Preservation
When loading existing KiCAD schematics:
- Preserve exact property positions from input
- Preserve existing justification settings
- Preserve `fields_autoplaced` flag state
- Output matches input byte-perfectly

### REQ-5: Multi-Unit Component Support
Handle multi-unit components (ICs like 7400, TL072):
- Each unit may have different positioning based on symbol variant
- Properties positioned relative to unit bounding box
- Consistent positioning across all units

### REQ-6: Hidden Property Stacking
Hidden properties (Datasheet, Description, custom fields):
- Positioned at component center or as per KiCAD defaults
- Stacked with appropriate vertical offset
- Preserve exact format from KiCAD

## KiCAD Format Specifications

### S-Expression Structure

**Component with autoplaced fields (KiCAD format):**
```
(symbol
  (lib_id "Device:R")
  (at 96.52 100.33 0)
  (unit 1)
  (exclude_from_sim no)
  (in_bom yes)
  (on_board yes)
  (dnp no)
  (fields_autoplaced yes)  ← REQUIRED FLAG
  (uuid "...")
  (property "Reference" "R1"
    (at 99.06 99.0599 0)  ← Position calculated by KiCAD
    (effects
      (font (size 1.27 1.27))
      (justify left)  ← Justification based on rotation
    )
  )
  (property "Value" "10k"
    (at 99.06 101.5999 0)
    (effects
      (font (size 1.27 1.27))
      (justify left)
    )
  )
  ...
)
```

### Property Positioning Patterns (Observed)

**From reference schematics (`tests/reference_kicad_projects/rotated_resistor_*deg/`):**

**0° Rotation (horizontal, pins left/right):**
- Component at (96.52, 100.33)
- Reference at (99.06, 99.06) - offset: (+2.54, -1.27) - RIGHT and ABOVE
- Value at (99.06, 101.60) - offset: (+2.54, +1.27) - RIGHT and BELOW
- Justification: `left` (anchored at left edge of text)

**90° Rotation (vertical, pins up/down):**
- Component at (98.425, 102.235)
- Reference at (97.155, 99.695) - offset: (-1.27, -2.54) - LEFT and ABOVE
- Value at (99.695, 99.695) - offset: (+1.27, -2.54) - RIGHT and ABOVE
- Justification: `left`

**180° Rotation (horizontal flipped):**
- Component at (100.33, 100.33)
- Reference at (97.79, 101.60) - offset: (-2.54, +1.27) - LEFT and BELOW
- Value at (97.79, 99.06) - offset: (-2.54, -1.27) - LEFT and ABOVE
- Justification: `left`
- **Note**: Reference/Value vertical order SWAPPED vs 0°

**270° Rotation (vertical flipped):**
- Component at (98.425, 98.425)
- Reference at (99.695, 100.965) - offset: (+1.27, +2.54) - RIGHT and BELOW
- Value at (97.155, 100.965) - offset: (-1.27, +2.54) - LEFT and BELOW
- Justification: `left`

**Pattern Analysis:**
- Offsets are NOT simple rotations of a base offset
- Properties positioned to side of component, never overlapping body
- Vertical/horizontal stacking depends on component orientation
- Reference/Value order swaps at 180°

### Version Compatibility
- KiCAD 7.0+ format (version 20230121+)
- KiCAD 8.0+ format (version 20240524+)
- KiCAD 9.0+ format (version 20250114) - current default

## Technical Constraints

### Backward Compatibility
**Breaking change allowed** - no need to preserve old positioning behavior. Update:
- Default positioning logic in `config.get_property_position()`
- All component generation code
- Tests that verify exact positions

### Format Preservation Requirements
**Critical**: When loading existing schematics, preserve exact format:
- If input has `fields_autoplaced yes`, preserve exact property positions
- If input has `fields_autoplaced no` or missing, preserve as-is
- Property justification preserved exactly
- Property rotation preserved exactly
- No regeneration of positions on round-trip

### Grid Alignment
All property positions must be grid-aligned (multiples of KiCAD's precision, typically 0.0001mm stored as 4 decimal places).

### Symbol Library Integration
Property positioning algorithm needs access to:
- Symbol bounding box (from library definition)
- Pin positions and orientations
- Symbol body dimensions

## Reference Schematic Requirements

### Primary References (Already Exist)
- `tests/reference_kicad_projects/rotated_resistor_0deg/` - 0° rotation baseline
- `tests/reference_kicad_projects/rotated_resistor_90deg/` - 90° rotation
- `tests/reference_kicad_projects/rotated_resistor_180deg/` - 180° rotation
- `tests/reference_kicad_projects/rotated_resistor_270deg/` - 270° rotation

### Additional References Needed
Create new reference schematics for:
1. **IC with multiple units** (e.g., 7400 quad NAND gate) at each rotation
2. **Op-amp** (e.g., TL072 dual op-amp) at each rotation
3. **Connector** (multi-pin connector) at each rotation
4. **Capacitor** (polarized) at each rotation
5. **Transistor** (3-pin component) at each rotation

Each reference demonstrates:
- Component at standard position (100, 100)
- Standard grid alignment
- KiCAD's native auto-placement
- All properties visible for analysis

## Edge Cases

### EDGE-1: Custom Properties
Components with custom properties beyond Reference/Value/Footprint:
- Position custom properties using same algorithm
- Stack vertically with configured offset
- Hidden properties at component center

### EDGE-2: Property Override
User explicitly sets property position (not autoplaced):
- Preserve exact position on load
- Don't recalculate on save
- Respect `fields_autoplaced` flag state

### EDGE-3: Symbol Variants
Components with multiple symbol variants (e.g., different pin layouts):
- Calculate positioning based on actual symbol variant used
- Bounding box may differ between variants

### EDGE-4: Power Symbols
Power symbols (VCC, GND) have special positioning rules:
- Already handled by `_create_power_symbol_value_property()`
- Verify compatibility with new algorithm

### EDGE-5: Zero-Rotation Components
Some components may have non-standard rotations or mirroring:
- Handle angles other than 0/90/180/270 gracefully
- Preserve exact positioning for non-standard angles

## Impact Analysis

### Parser Changes
**File**: `kicad_sch_api/parsers/elements/symbol_parser.py`
- ✅ Already parses `fields_autoplaced` flag (line 254)
- ✅ Already parses property positions and justification
- ❌ Need to preserve exact positions (don't recalculate on load)

### Formatter Changes
**File**: `kicad_sch_api/parsers/elements/symbol_parser.py`
- ✅ Already emits `fields_autoplaced yes` (line 254)
- ❌ Need to emit correct property positions using new algorithm
- ❌ Need to emit correct justification based on rotation

### Type Changes
**File**: `kicad_sch_api/core/types.py`
- ✅ `SchematicSymbol` already has `fields_autoplaced: bool = True` (line 690)
- ✅ Properties already store position and effects
- ❌ May need to track whether position was user-set or auto-calculated

### Configuration Changes
**File**: `kicad_sch_api/core/config.py`
- ❌ Replace `PropertyOffsets` with KiCAD-exact algorithm
- ❌ Add `get_kicad_property_position()` method
- ❌ Consider symbol bounding box in calculation
- ❌ Remove hardcoded offsets (breaking change)

### Symbol Library Integration
**File**: `kicad_sch_api/symbols/cache.py` or `library/cache.py`
- ❌ Need symbol bounding box calculation
- ❌ Need pin position/orientation data
- ✅ Symbol loading already works

### MCP Tool Compatibility
**MCP Server**: External `mcp-kicad-sch-api`
- Generated components will have better positioning automatically
- No MCP tool changes needed (API unchanged)
- Visual improvement for AI-generated circuits

## Out of Scope

### NOT Included in This PRD
- ❌ Manual property repositioning API (future enhancement)
- ❌ Custom justification override (use KiCAD defaults only)
- ❌ Property font size/style customization (separate from positioning)
- ❌ Schematic aesthetic optimization (layout, wire routing)
- ❌ Component auto-placement on schematic (position selection)

## Acceptance Criteria

### Implementation Complete When:
1. ✅ All tests pass (update test expectations for new positions)
2. ✅ Reference tests validate byte-perfect format match
3. ✅ Round-trip test: load reference → save → diff shows zero changes
4. ✅ Generated components have `fields_autoplaced yes` flag
5. ✅ Property positions match KiCAD auto-placement for all rotations
6. ✅ Property justification matches KiCAD defaults
7. ✅ Works for all component types tested (passives, ICs, connectors)
8. ✅ Multi-unit components position correctly
9. ✅ Manual validation: Open generated schematic in KiCAD → looks native
10. ✅ No visual indication that schematic was programmatically generated

### Test Coverage Requirements
- Unit tests for position calculation algorithm
- Reference tests for each component type at each rotation
- Round-trip preservation tests
- Edge case tests (custom properties, user overrides, power symbols)
- Format preservation validation

## Implementation Strategy

### Phase 1: Reverse Engineer Algorithm
1. Create reference schematics for multiple component types
2. Analyze KiCAD output for each type/rotation
3. Document positioning patterns and rules
4. Identify algorithm inputs (bounding box, rotation, type)

### Phase 2: Symbol Bounding Box
1. Extract bounding box from symbol library definitions
2. Calculate effective bounding box per rotation
3. Cache bounding box data for performance

### Phase 3: Position Calculation
1. Implement position calculation algorithm
2. Handle all rotations (0°, 90°, 180°, 270°)
3. Apply justification based on rotation
4. Stack hidden properties appropriately

### Phase 4: Round-Trip Preservation
1. Parse existing property positions
2. Preserve positions on load
3. Only calculate for new components
4. Validate byte-perfect output

### Phase 5: Testing & Validation
1. Update existing tests for new positions
2. Add reference tests for all component types
3. Validate round-trip preservation
4. Manual KiCAD validation

## Related Issues & PRs

- Issue #150: Default component property text positioning doesn't match KiCAD auto-placement
- PR #91: Component rotation handling (pin positions)
- PR #148: Text effects preservation
- ADR-003: Format Preservation Strategy (docs/ADR.md)

## References

- KiCAD source code: `eeschema/sch_symbol.cpp` (auto-placement logic)
- Reference schematics: `tests/reference_kicad_projects/rotated_resistor_*/`
- Configuration: `kicad_sch_api/core/config.py:185-227`
- Symbol parser: `kicad_sch_api/parsers/elements/symbol_parser.py:441`
