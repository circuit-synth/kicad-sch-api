# Round-Trip Fidelity Issues

This document tracks issues discovered when loading and re-saving KiCAD schematics.

## Issue #1: Pin UUIDs Not Preserved

**Discovered:** 2025-11-08
**Severity:** High (breaks round-trip capability)

### Description

When loading a schematic and immediately saving it back (with no modifications), the library strips all pin-level UUIDs from components.

### Example

**Original schematic:**
```lisp
(symbol
  (lib_id "MCU_ST_STM32G0:STM32G030K8Tx")
  (at 128.27 110.49 0)
  (property "Reference" "U1" ...)
  (property "Value" "STM32G030K8Tx" ...)
  (pin "1"
    (uuid "fee47a85-7570-4989-91d5-ecdd982560d2")
  )
  (pin "2"
    (uuid "fda5684a-54f2-4e76-851c-d127cd59bf0e")
  )
  ...
)
```

**After load → save:**
```lisp
(symbol
  (lib_id "MCU_ST_STM32G0:STM32G030K8Tx")
  (at 128.27 110.49 0)
  (property "Reference" "U1" ...)
  (property "Value" "STM32G030K8Tx" ...)
  (instances
    (project "STM32_Microprocessor"
      (path "/83c5e24d-5e3d-4e1d-960c-7b505762d8f1"
        (reference "U1")
        (unit 1)
      )
    )
  )
)
```

All `(pin ...)` entries are removed!

### Impact

- **Round-trip capability broken**: Cannot load customer schematic → save → get identical output
- **Pin-specific metadata lost**: Pin UUIDs are used for cross-referencing in hierarchical designs
- **Version control noise**: Every save changes hundreds of lines unnecessarily

### Test Results

Test file: `test_roundtrip_fidelity.py`

```
❌ DIFFERENCES FOUND: 403 lines differ
  • UUID differences: 63
  • Property differences: 0
  • Position differences: 9
```

### Root Cause

The library's Component dataclass likely doesn't have a field for pin UUIDs, so they're not parsed or stored during loading.

### Required Fix

1. **Parse pin UUIDs** when loading components
2. **Store pin UUIDs** in Component dataclass
3. **Emit pin UUIDs** when saving components
4. **Preserve exact formatting** of pin entries

### Related Issues

This is related to the broader need for **granular component text control** mentioned by the user. For perfect round-trip capability, the library needs to preserve:

- Pin UUIDs ❌ (currently lost)
- Component property positions ✅ (working)
- Component property effects ✅ (working)
- Property justification ✅ (working)
- Additional properties (Footprint, Datasheet, etc.) ⚠️ (needs verification)
- Custom component properties ⚠️ (needs verification)

## Issue #2: Component Text Positioning (User Concern)

**Status:** Under investigation

User mentioned: "when we generate components we generate them really weird with the text"

Initial testing shows text positions match correctly for simple components (R, C), but may have issues with:
- Complex multi-unit components
- Rotated components
- Components with custom property positioning
- Footprint/Datasheet property visibility and positioning

**Action:** Need more specific examples from user to identify the exact issue.

---

## Testing Strategy

1. Create comprehensive round-trip tests for all component types
2. Test with real customer schematics (if available)
3. Add format preservation tests for pin UUIDs
4. Verify property preservation for all standard KiCAD properties

## Priority

**HIGH** - This is critical for the library's stated goal of "exact format preservation" and real-world usability with existing schematics.
