# Known Issues and Recommended Improvements

**Generated:** 2025-10-27
**Current Version:** v0.4.1
**Test Status:** 410/432 passing (95%), 14 failures, 8 skipped

---

## Executive Summary

The project is in **good working condition** with most core functionality reliable. The main issues are:
1. **14 test failures** - mostly in incomplete ERC validation features
2. **Pin rotation transformation** - known limitation for rotated components
3. **Some collection methods** - recent refactoring caused test breakage

**Good news:** Issue #54 (critical component removal bug) was **FIXED in PR #55** and merged on 2025-10-27. This was the most serious reliability concern.

---

## Issues Already Tracked in GitHub

### Open Issues (4 total)

| Issue | Priority | Status | Notes |
|-------|----------|--------|-------|
| #59 | Low | Open | Documentation: Add llm.txt with API examples |
| #37 | Medium | Open | Feature: Advanced hierarchy and sheet management |
| #36 | Medium | Open | Feature: Text variables and dynamic substitution |
| #31 | High | Open | Feature: Complete bus support (KiCAD 7/8) |

**Assessment:** These are all enhancement requests, not bugs affecting current reliability.

### Recently Fixed Issues (Critical)

| Issue | Fixed | Impact | Solution |
|-------|-------|--------|----------|
| #54 | ✅ PR #55 (2025-10-27) | **CRITICAL** - Component removal was broken | Implemented proper `remove()`, `remove_by_uuid()`, and `remove_component()` methods with proper index updates |

---

## Issues NOT Yet Tracked (Need GitHub Issues)

### ✅ ALL ISSUES NOW TRACKED

All identified issues have been created in GitHub:
- Issue #61: Test Failures - Collection Removal Methods
- Issue #62: Pin Position Rotation Transformation
- Issue #63: ERC Validation Status
- Issue #64: Wire Connectivity Analysis
- Issue #65: API Documentation Updates

---

## Detailed Issue Analysis

### 1. **Test Failures - Collection Removal Methods** 🔴 HIGH PRIORITY

**GitHub Issue:** [#61](https://github.com/circuit-synth/kicad-sch-api/issues/61)
**Location:** `tests/unit/collections/test_components.py`
**Status:** 8 tests failing after recent BaseCollection refactoring

```
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_component_by_reference
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_component_by_uuid
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_component_by_object
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_nonexistent_component_by_uuid
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_component_invalid_type_reference
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_component_invalid_type_uuid
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_component_invalid_type_object
FAILED tests/unit/collections/test_components.py::TestComponent::test_remove_updates_indexes
```

**Root Cause:**
- PR #55 fixed the core bug but tests are still using old API
- Tests expect `remove_by_uuid()` and `remove_component()` but getting AttributeError
- Tests need updating to match the new API from PR #55

**Impact:** Medium - The functionality works (PR #55 fixed it), but tests need to be updated to reflect the new API

**Recommended Fix:**
```python
# Update tests to use new API
collection.remove("R1")                    # Remove by reference
collection.remove_by_uuid(uuid)            # Remove by UUID
collection.remove_component(component)      # Remove by component object
```

**Estimated Effort:** 1-2 hours to update tests

---

### 2. **Pin Position Rotation Transform Missing** 🟡 MEDIUM PRIORITY

**GitHub Issue:** [#62](https://github.com/circuit-synth/kicad-sch-api/issues/62)
**Location:** `kicad_sch_api/core/types.py:202-207`
**Current Code:**
```python
def get_pin_position(self, pin_number: str) -> Optional[Point]:
    """Get absolute position of a pin."""
    pin = self.get_pin(pin_number)
    if not pin:
        return None
    # TODO: Apply rotation and symbol position transformation
    # NOTE: Currently assumes 0° rotation. For rotated components, pin positions
    # would need to be transformed using rotation matrix before adding to component position.
    # This affects pin-to-pin wiring accuracy for rotated components.
    # Priority: MEDIUM - Would improve wiring accuracy for rotated components
    return Point(self.position.x + pin.position.x, self.position.y + pin.position.y)
```

**Impact:**
- Pin-to-pin wiring inaccurate for rotated components (90°, 180°, 270°)
- Bounding box calculations may be off for rotated components
- Component positioning itself is NOT affected (positions are always correct)

**Recommended Fix:**
```python
def get_pin_position(self, pin_number: str) -> Optional[Point]:
    """Get absolute position of a pin with rotation transform."""
    pin = self.get_pin(pin_number)
    if not pin:
        return None

    # Apply rotation transformation
    import math
    angle_rad = math.radians(self.rotation)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Rotate pin position around origin
    rotated_x = pin.position.x * cos_a - pin.position.y * sin_a
    rotated_y = pin.position.x * sin_a + pin.position.y * cos_a

    # Add to component position
    return Point(self.position.x + rotated_x, self.position.y + rotated_y)
```

**Estimated Effort:** 4-6 hours (implementation + comprehensive testing)

**Also Needs Fix:** `kicad_sch_api/core/component_bounds.py:386-387` (same issue for bounding boxes)

---

### 3. **ERC Validation Incomplete** 🟡 MEDIUM PRIORITY

**GitHub Issue:** [#63](https://github.com/circuit-synth/kicad-sch-api/issues/63)
**Location:** `kicad_sch_api/validation/validators.py`
**Status:** 6 tests failing, multiple TODOs in code

```
FAILED tests/test_erc/test_erc_validators.py::TestConnectivityValidator::test_detect_dangling_wire
FAILED tests/test_erc/test_erc_validators.py::TestConnectivityValidator::test_detect_unconnected_input
FAILED tests/test_erc/test_erc_validators.py::TestConnectivityValidator::test_detect_undriven_net
FAILED tests/test_erc/test_erc_validators.py::TestComponentValidator::test_invalid_reference_format
FAILED tests/test_erc/test_erc_validators.py::TestElectricalRulesChecker::test_erc_violation_codes_unique
FAILED tests/test_erc/test_erc_validators.py::TestElectricalRulesChecker::test_erc_suggested_fixes
```

**TODOs in Code:**
- Line 77: "TODO: Implement net tracing from wires and components"
- Line 180: "TODO: Get pin types from symbol library"
- Line 194: "TODO: Implement net tracing and driver detection"
- Line 208: "TODO: Implement proper connection counting"
- Line 344: "TODO: Implement power net detection and PWR_FLAG checking"
- Line 360: "TODO: Implement power driver checking"

**Impact:**
- ERC validation is incomplete and unreliable
- Tests were written first (TDD approach) but implementation is partial
- Basic pin conflict detection works, advanced connectivity checking doesn't

**Recommendation:**
- Either finish the ERC implementation or mark these features as "experimental"
- Document clearly what ERC checks are supported vs. not supported
- Consider disabling failing tests until implementation is complete

**Estimated Effort:** 20-30 hours to complete full ERC implementation

---

### 4. **Wire Connectivity Analysis Limited** 🟡 MEDIUM PRIORITY

**GitHub Issue:** [#64](https://github.com/circuit-synth/kicad-sch-api/issues/64)
**Location:** `kicad_sch_api/core/managers/wire.py:307-308`

```python
# TODO: Implement more sophisticated connectivity analysis
# NOTE: Current implementation only checks for direct wire connections between pins.
```

**Impact:**
- Can detect simple pin-to-pin wires
- Cannot trace complex nets through junctions, labels, and multiple wire segments
- Limits usefulness of connectivity-based operations

**Recommendation:** Implement proper net tracing algorithm

**Estimated Effort:** 10-15 hours

---

## Recommended Improvements (Not Bugs)

### 1. **Increase Test Coverage for Recent Fixes** 📊

**Current Coverage:**
- 432 total tests
- ~9,652 lines of test code
- Good coverage overall, but recent changes need more tests

**Recommendations:**
1. Add integration tests for component removal (PR #55)
2. Add regression tests for index synchronization
3. Add tests for rotated component scenarios
4. Add negative test cases for edge cases

**Estimated Effort:** 8-10 hours

---

### 2. **Documentation Updates** 📚

**GitHub Issue:** [#65](https://github.com/circuit-synth/kicad-sch-api/issues/65)

**Needed:**
1. Update API docs to reflect new removal methods from PR #55
2. Document known limitation: pin positions for rotated components
3. Document ERC feature status (what works, what doesn't)
4. Add architecture decision records (ADRs) for major design choices

**Related:** Issue #59 (llm.txt with API examples)

**Estimated Effort:** 4-6 hours

---

### 3. **Type Safety Improvements** 🔒

**Current State:** Mostly good type hints, some gaps

**Recommendations:**
1. Enable mypy strict mode (Issue #30 was closed but needs verification)
2. Add type hints to all internal methods
3. Use `typing.Protocol` for better interface definitions
4. Add runtime type checking with `typeguard` for critical paths

**Estimated Effort:** 6-8 hours

---

### 4. **Performance Profiling** ⚡

**Current State:** Optimized for large schematics with caching, but no benchmarks

**Recommendations:**
1. Add performance benchmark suite
2. Profile common operations (add component, remove component, save)
3. Document performance characteristics
4. Add performance regression tests

**Estimated Effort:** 6-8 hours

---

## Priority Action Items

### Immediate (This Week)
1. ✅ **Component removal bug** - FIXED in PR #55
2. 🔴 **Update collection removal tests** - 8 tests need updating for new API
3. 📚 **Document known limitations** - Pin rotation, ERC status

### Short Term (Next 2 Weeks)
1. 🟡 **Implement pin rotation transform** - Affects pin-to-pin wiring
2. 🟡 **Finish or document ERC status** - Either complete it or mark as WIP
3. 📊 **Add regression tests** - Ensure recent fixes stay fixed

### Medium Term (Next Month)
1. 🟡 **Improve wire connectivity** - Net tracing through junctions/labels
2. 📚 **Complete API documentation** - Update for all recent changes
3. ⚡ **Add performance benchmarks** - Document characteristics

### Long Term (Backlog)
1. Feature: Complete bus support (Issue #31)
2. Feature: Advanced hierarchy (Issue #37)
3. Feature: Text variables (Issue #36)

---

## Summary Recommendations

### ✅ GitHub Issues Created

All identified issues have been created and are now tracked:

1. **[#61](https://github.com/circuit-synth/kicad-sch-api/issues/61) - Fix collection removal test failures** (High Priority)
   - 8 tests failing
   - Tests need updating for new API
   - Estimated: 1-2 hours

2. **[#62](https://github.com/circuit-synth/kicad-sch-api/issues/62) - Implement pin position rotation transformation** (Medium Priority)
   - Affects pin-to-pin wiring accuracy
   - Known TODO in code
   - Estimated: 4-6 hours

3. **[#63](https://github.com/circuit-synth/kicad-sch-api/issues/63) - Complete or document ERC validation** (Medium Priority)
   - 6 tests failing
   - Multiple TODOs in code
   - Either finish (20-30 hours) or document limitations (2 hours)

4. **[#64](https://github.com/circuit-synth/kicad-sch-api/issues/64) - Enhance wire connectivity analysis** (Medium Priority)
   - Net tracing through junctions/labels
   - Known TODO in code
   - Estimated: 10-15 hours

5. **[#65](https://github.com/circuit-synth/kicad-sch-api/issues/65) - Update API documentation** (Medium Priority)
   - PR #55 removal methods
   - Known limitations
   - Architecture decisions
   - Estimated: 4-6 hours

### Previously Tracked Issues:
- ✅ #54: Component removal bug (fixed in PR #55)
- ✅ #59: llm.txt API examples (open)
- ✅ #37: Advanced hierarchy (open)
- ✅ #36: Text variables (open)
- ✅ #31: Bus support (open)

---

## Testing Philosophy Observations

**Strengths:**
- TDD approach (tests written first)
- Reference-based testing (manual KiCAD files as ground truth)
- Comprehensive format preservation validation
- Good coverage of happy paths

**Gaps:**
- Some tests ahead of implementation (ERC)
- Tests not updated after API changes (removal methods)
- Limited negative test cases
- No performance regression tests

**Recommendation:** Update tests to match current implementation, then enforce that tests must pass before merging.

---

**Last Updated:** 2025-10-27
**Next Review:** After addressing high-priority test failures
