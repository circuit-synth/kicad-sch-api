# Known Limitations

This document lists known limitations and future improvements for the kicad-sch-api project.

## Current Limitations

### 1. Component Rotation in Bounding Box Calculations

**File**: `kicad_sch_api/core/component_bounds.py:386`

**Issue**: Component rotation is not applied when calculating bounding boxes.

**Impact**:
- Bounding box calculations assume 0° rotation
- Rotated components may have inaccurate bounds for validation
- Does NOT affect routing or visual placement in most cases

**Current Status**: Documented as known limitation
- Components are typically placed without rotation in practice
- Routing algorithms avoid components regardless of rotation

**Priority**: LOW - Would improve accuracy for edge cases

**Future Implementation**: Apply rotation matrix transformation to bounding box after calculation

---

### 2. Symbol Rotation and Position Transformation in Pin Positioning

**File**: `kicad_sch_api/core/types.py:165` (SchematicSymbol.get_pin_position)

**Issue**: Pin position calculations don't account for component rotation or symbol offset transformations.

**Impact**:
- Pin-to-pin wiring may be slightly inaccurate for rotated components
- Affects automated wire routing accuracy

**Current Status**: Documented as known limitation
- Basic functionality works for 0° rotation (most common case)
- Users can work around by using explicit point coordinates

**Priority**: MEDIUM - Would improve wiring accuracy for rotated components

**Future Implementation**: Apply rotation matrix to pin positions before returning coordinates

---

### 3. Wire Connectivity Analysis

**File**: `kicad_sch_api/core/managers/wire.py:307`

**Issue**: Connectivity analysis for nets and wires is simplified.

**Impact**:
- Complex wire junction detection may miss some connections
- Affected by very short wire segments or unusual routing patterns

**Current Status**: Documented as known limitation
- Basic connectivity analysis works for standard schematics
- Advanced analysis would require intersection checking

**Priority**: MEDIUM - Would improve net analysis accuracy

**Future Implementation**: Implement sophisticated intersection detection and node clustering algorithms

---

## Test Coverage Gaps

See [TEST_COVERAGE_GAPS.md](TEST_COVERAGE_GAPS.md) for areas lacking unit test coverage.

---

## How to Contribute

If you're interested in implementing any of these improvements, please:
1. Open a GitHub issue discussing the approach
2. Reference this document in your PR
3. Add appropriate tests for your implementation
4. Update this document once resolved
